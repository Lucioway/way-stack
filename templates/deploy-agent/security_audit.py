"""DeployAgent — Security Audit.

Performs security checks on a project:
  - Secrets detection (regex patterns for API keys, passwords, tokens)
  - .gitignore validation
  - Dependency audit (npm audit)
  - OWASP static analysis (XSS, injection, CSRF)
  - Data loss prevention checks
"""

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from config import (
    GITIGNORE_REQUIRED,
    OWASP_PATTERNS,
    SCAN_EXTENSIONS,
    SCAN_SKIP_DIRS,
    SCAN_SKIP_FILES,
    SECRET_PATTERNS,
)

logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    severity: str       # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str       # secrets, gitignore, dependency, owasp, config
    title: str
    description: str
    file_path: str = ""
    line_number: int = 0
    recommendation: str = ""

    def __str__(self) -> str:
        loc = f" ({self.file_path}:{self.line_number})" if self.file_path else ""
        return f"[{self.severity}] {self.category}: {self.title}{loc}"


@dataclass
class SecurityReport:
    findings: list[SecurityFinding] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    deploy_blocked: bool = False
    summary: str = ""

    def add(self, finding: SecurityFinding):
        self.findings.append(finding)
        match finding.severity:
            case "CRITICAL":
                self.critical_count += 1
            case "HIGH":
                self.high_count += 1
            case "MEDIUM":
                self.medium_count += 1
            case "LOW":
                self.low_count += 1
            case "INFO":
                self.info_count += 1

    def finalize(self):
        self.deploy_blocked = self.critical_count > 0 or self.high_count > 0
        total = len(self.findings)
        if total == 0:
            self.summary = "No security issues found. Project is clean."
        else:
            self.summary = (
                f"{total} findings: {self.critical_count} critical, "
                f"{self.high_count} high, {self.medium_count} medium, "
                f"{self.low_count} low, {self.info_count} info. "
                f"{'DEPLOY BLOCKED' if self.deploy_blocked else 'Deploy allowed'}."
            )

    def to_markdown(self) -> str:
        lines = [
            "# Security Audit Report",
            "",
            f"**Summary**: {self.summary}",
            f"**Deploy Status**: {'BLOCKED' if self.deploy_blocked else 'ALLOWED'}",
            "",
            "## Findings",
            "",
        ]

        if not self.findings:
            lines.append("No issues found.")
            return "\n".join(lines)

        # Group by severity
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            sev_findings = [f for f in self.findings if f.severity == sev]
            if not sev_findings:
                continue
            lines.append(f"### {sev} ({len(sev_findings)})")
            lines.append("")
            for f in sev_findings:
                loc = f"  - File: `{f.file_path}:{f.line_number}`" if f.file_path else ""
                lines.append(f"- **{f.title}** [{f.category}]")
                lines.append(f"  - {f.description}")
                if loc:
                    lines.append(loc)
                if f.recommendation:
                    lines.append(f"  - Fix: {f.recommendation}")
                lines.append("")

        return "\n".join(lines)


def run_audit(project_path: str, scan_report=None) -> SecurityReport:
    """Run full security audit on a project."""
    path = Path(project_path).resolve()
    report = SecurityReport()

    logger.info("Starting security audit...")

    # 1. Secrets detection
    _check_secrets(path, report)

    # 2. Gitignore validation
    _check_gitignore(path, report)

    # 3. Dependency audit
    _check_dependencies(path, report, scan_report)

    # 4. OWASP static scan
    _check_owasp(path, report)

    # 5. Config security
    _check_config_security(path, report, scan_report)

    # Finalize
    report.finalize()

    # Write report to file
    report_path = path / "SECURITY_REPORT.md"
    try:
        report_path.write_text(report.to_markdown(), encoding="utf-8")
        logger.info(f"Security report written to {report_path}")
    except IOError as e:
        logger.warning(f"Could not write security report: {e}")

    return report


def _iter_source_files(path: Path):
    """Iterate over scannable source files, skipping irrelevant dirs/files."""
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SCAN_SKIP_DIRS]
        for fname in files:
            if fname in SCAN_SKIP_FILES:
                continue
            fpath = Path(root) / fname
            if fpath.suffix.lower() in SCAN_EXTENSIONS:
                yield fpath


def _check_secrets(path: Path, report: SecurityReport):
    """Scan source files for hardcoded secrets."""
    logger.info("Checking for hardcoded secrets...")

    # Files to exclude from secrets scanning
    exclude_names = {".env.example", ".env.sample", ".env.local.example"}
    exclude_dirs = {"test", "tests", "__tests__", "__mocks__", "fixtures", "snapshots"}

    compiled_patterns = [(re.compile(p), desc) for p, desc in SECRET_PATTERNS]

    for fpath in _iter_source_files(path):
        # Skip example env files
        if fpath.name in exclude_names:
            continue
        # Skip test fixtures (less strict)
        rel_parts = fpath.relative_to(path).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue
        # Skip .env files that are SUPPOSED to exist (but flag .env itself)
        if fpath.name == ".env" or fpath.name == ".env.local":
            report.add(SecurityFinding(
                severity="CRITICAL",
                category="secrets",
                title=f"Environment file '{fpath.name}' found in project",
                description="This file likely contains secrets and must not be committed.",
                file_path=str(fpath.relative_to(path)),
                recommendation=f"Add '{fpath.name}' to .gitignore and remove from tracking.",
            ))
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except IOError:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*"):
                continue

            for pattern, desc in compiled_patterns:
                if pattern.search(line):
                    # Double-check: skip if it's a placeholder
                    if any(ph in line.lower() for ph in [
                        "your_", "xxx", "placeholder", "example", "changeme",
                        "todo", "fixme", "replace", "process.env", "import.meta.env",
                    ]):
                        continue
                    report.add(SecurityFinding(
                        severity="CRITICAL",
                        category="secrets",
                        title=desc,
                        description=f"Potential secret found: {line.strip()[:80]}...",
                        file_path=str(fpath.relative_to(path)),
                        line_number=line_num,
                        recommendation="Move this value to environment variables.",
                    ))
                    break  # One finding per line is enough


def _check_gitignore(path: Path, report: SecurityReport):
    """Validate .gitignore exists and contains required entries."""
    logger.info("Checking .gitignore...")

    gitignore_path = path / ".gitignore"
    if not gitignore_path.exists():
        report.add(SecurityFinding(
            severity="HIGH",
            category="gitignore",
            title=".gitignore file is MISSING",
            description="Without .gitignore, sensitive files may be committed to git.",
            file_path=".gitignore",
            recommendation="Create .gitignore with standard exclusions.",
        ))
        return

    try:
        content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    except IOError:
        return

    lines = {line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")}

    for required in GITIGNORE_REQUIRED:
        # Check if the pattern or a parent pattern is present
        found = False
        for line in lines:
            if required in line or line.startswith(required.rstrip("/")):
                found = True
                break
        if not found:
            severity = "HIGH" if "env" in required.lower() else "MEDIUM"
            report.add(SecurityFinding(
                severity=severity,
                category="gitignore",
                title=f"Missing '{required}' in .gitignore",
                description=f"The pattern '{required}' should be in .gitignore to prevent accidental commits.",
                file_path=".gitignore",
                recommendation=f"Add '{required}' to .gitignore.",
            ))


def _check_dependencies(path: Path, report: SecurityReport, scan_report=None):
    """Run npm audit (or equivalent) to check for known vulnerabilities."""
    logger.info("Checking dependencies for known vulnerabilities...")

    pkg_manager = "npm"
    if scan_report:
        pkg_manager = scan_report.package_manager

    # Only run if package.json exists
    if not (path / "package.json").exists():
        report.add(SecurityFinding(
            severity="INFO",
            category="dependency",
            title="No package.json — dependency audit skipped",
            description="Cannot run dependency audit without package.json.",
        ))
        return

    # Only run if node_modules or lockfile exists
    has_lockfile = any(
        (path / f).exists()
        for f in ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb"]
    )
    if not has_lockfile:
        report.add(SecurityFinding(
            severity="INFO",
            category="dependency",
            title="No lockfile found — dependency audit skipped",
            description="Run 'npm install' first to generate a lockfile for audit.",
            recommendation=f"Run '{pkg_manager} install' before deploying.",
        ))
        return

    # Run npm audit
    try:
        cmd = ["npm", "audit", "--json"]
        if pkg_manager == "pnpm":
            cmd = ["pnpm", "audit", "--json"]
        elif pkg_manager == "yarn":
            cmd = ["yarn", "audit", "--json"]

        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if pkg_manager in ("npm", "pnpm"):
            try:
                audit_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.warning("Could not parse npm audit output")
                return

            vulns = audit_data.get("vulnerabilities", {})
            for pkg_name, vuln_info in vulns.items():
                npm_severity = vuln_info.get("severity", "low")
                severity_map = {
                    "critical": "CRITICAL",
                    "high": "HIGH",
                    "moderate": "MEDIUM",
                    "low": "LOW",
                    "info": "INFO",
                }
                severity = severity_map.get(npm_severity, "MEDIUM")
                report.add(SecurityFinding(
                    severity=severity,
                    category="dependency",
                    title=f"Vulnerable package: {pkg_name}",
                    description=f"Severity: {npm_severity}. {vuln_info.get('title', '')}",
                    recommendation=f"Run '{pkg_manager} audit fix' or update {pkg_name}.",
                ))

    except FileNotFoundError:
        report.add(SecurityFinding(
            severity="INFO",
            category="dependency",
            title=f"'{pkg_manager}' not found — dependency audit skipped",
            description=f"Install {pkg_manager} to enable dependency auditing.",
        ))
    except subprocess.TimeoutExpired:
        report.add(SecurityFinding(
            severity="INFO",
            category="dependency",
            title="Dependency audit timed out",
            description="npm audit took too long. Run manually.",
        ))


def _check_owasp(path: Path, report: SecurityReport):
    """Static analysis for common OWASP vulnerabilities."""
    logger.info("Running OWASP static analysis...")

    compiled = [(re.compile(p), cat, sev, rec) for p, cat, sev, rec in OWASP_PATTERNS]

    for fpath in _iter_source_files(path):
        # Only check JS/TS/JSX/TSX
        if fpath.suffix.lower() not in (".js", ".jsx", ".ts", ".tsx", ".mjs"):
            continue

        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except IOError:
            continue

        rel_path = str(fpath.relative_to(path))

        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern, category, severity, recommendation in compiled:
                if pattern.search(line):
                    report.add(SecurityFinding(
                        severity=severity,
                        category="owasp",
                        title=f"{category} risk detected",
                        description=f"Pattern: {line.strip()[:100]}",
                        file_path=rel_path,
                        line_number=line_num,
                        recommendation=recommendation,
                    ))


def _check_config_security(path: Path, report: SecurityReport, scan_report=None):
    """Check framework config for security issues."""
    logger.info("Checking configuration security...")

    framework = scan_report.framework if scan_report else "unknown"

    if framework == "nextjs":
        # Check next.config
        for config_name in ["next.config.ts", "next.config.js", "next.config.mjs"]:
            config_path = path / config_name
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding="utf-8", errors="ignore")
                except IOError:
                    continue

                if "poweredByHeader" not in content:
                    report.add(SecurityFinding(
                        severity="LOW",
                        category="config",
                        title="X-Powered-By header not disabled",
                        description="Next.js sends X-Powered-By header by default, revealing tech stack.",
                        file_path=config_name,
                        recommendation="Add 'poweredByHeader: false' to next.config.",
                    ))

                if "'export'" in content or '"export"' in content:
                    if scan_report and scan_report.has_api_routes:
                        report.add(SecurityFinding(
                            severity="HIGH",
                            category="config",
                            title="Static export with API routes",
                            description="output: 'export' is incompatible with API routes — they won't work.",
                            file_path=config_name,
                            recommendation="Remove output: 'export' or remove API routes.",
                        ))
                break

    # Check for debug/dev flags in production config
    for fpath in _iter_source_files(path):
        if fpath.name in ("next.config.ts", "next.config.js", "vite.config.ts", "vite.config.js"):
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                if "reactStrictMode: false" in content:
                    report.add(SecurityFinding(
                        severity="LOW",
                        category="config",
                        title="React Strict Mode disabled",
                        description="Strict mode helps catch bugs in development.",
                        file_path=str(fpath.relative_to(path)),
                        recommendation="Set reactStrictMode: true.",
                    ))
            except IOError:
                pass

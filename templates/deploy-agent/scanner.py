"""DeployAgent — Project Scanner.

Analizza una cartella di progetto e identifica framework, struttura,
dipendenze, auth, database, env vars e entry points.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from config import (
    AUTH_PACKAGES,
    DB_PACKAGES,
    FRAMEWORK_DETECTION,
    SCAN_EXTENSIONS,
    SCAN_SKIP_DIRS,
    SCAN_SKIP_FILES,
)

logger = logging.getLogger(__name__)


@dataclass
class ScanReport:
    project_path: str = ""
    project_name: str = ""
    framework: str = "unknown"
    package_manager: str = "npm"
    node_version: str = ""
    has_typescript: bool = False
    entry_points: list[str] = field(default_factory=list)
    has_auth: bool = False
    auth_provider: str = ""
    has_database: bool = False
    db_provider: str = ""
    has_api_routes: bool = False
    env_vars_needed: list[str] = field(default_factory=list)
    dependencies: dict = field(default_factory=dict)
    dev_dependencies: dict = field(default_factory=dict)
    file_count: int = 0
    total_size_mb: float = 0.0
    warnings: list[str] = field(default_factory=list)
    has_vercel_config: bool = False
    has_gitignore: bool = False
    has_env_example: bool = False
    build_command: str = ""
    source_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_path": self.project_path,
            "project_name": self.project_name,
            "framework": self.framework,
            "package_manager": self.package_manager,
            "node_version": self.node_version,
            "has_typescript": self.has_typescript,
            "entry_points": self.entry_points,
            "has_auth": self.has_auth,
            "auth_provider": self.auth_provider,
            "has_database": self.has_database,
            "db_provider": self.db_provider,
            "has_api_routes": self.has_api_routes,
            "env_vars_needed": self.env_vars_needed,
            "file_count": self.file_count,
            "total_size_mb": round(self.total_size_mb, 2),
            "warnings": self.warnings,
            "has_vercel_config": self.has_vercel_config,
            "has_gitignore": self.has_gitignore,
            "has_env_example": self.has_env_example,
            "build_command": self.build_command,
        }

    def summary(self) -> str:
        lines = [
            f"=== Project Scan Report ===",
            f"Project:         {self.project_name}",
            f"Path:            {self.project_path}",
            f"Framework:       {self.framework}",
            f"Package Manager: {self.package_manager}",
            f"TypeScript:      {'Yes' if self.has_typescript else 'No'}",
            f"Files:           {self.file_count}",
            f"Size:            {self.total_size_mb:.2f} MB",
            f"Auth:            {self.auth_provider if self.has_auth else 'None'}",
            f"Database:        {self.db_provider if self.has_database else 'None'}",
            f"API Routes:      {'Yes' if self.has_api_routes else 'No'}",
            f"Vercel Config:   {'Yes' if self.has_vercel_config else 'No'}",
            f".gitignore:      {'Yes' if self.has_gitignore else 'MISSING'}",
            f".env.example:    {'Yes' if self.has_env_example else 'No'}",
            f"Build Command:   {self.build_command or 'auto-detect'}",
        ]
        if self.env_vars_needed:
            lines.append(f"Env Vars Needed: {', '.join(self.env_vars_needed)}")
        if self.entry_points:
            lines.append(f"Entry Points:    {', '.join(self.entry_points[:5])}")
        if self.warnings:
            lines.append(f"\n--- Warnings ---")
            for w in self.warnings:
                lines.append(f"  ! {w}")
        return "\n".join(lines)


def scan_project(project_path: str) -> ScanReport:
    """Scan a project directory and return a ScanReport."""
    path = Path(project_path).resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Project path not found: {project_path}")

    report = ScanReport(
        project_path=str(path),
        project_name=path.name,
    )

    # Read package.json
    pkg_json = _read_package_json(path)
    if pkg_json:
        report.dependencies = pkg_json.get("dependencies", {})
        report.dev_dependencies = pkg_json.get("devDependencies", {})
        all_deps = {**report.dependencies, **report.dev_dependencies}

        # Node version
        engines = pkg_json.get("engines", {})
        report.node_version = engines.get("node", "")

        # Build command
        scripts = pkg_json.get("scripts", {})
        report.build_command = scripts.get("build", "")
    else:
        all_deps = {}
        report.warnings.append("No package.json found — is this a Node.js project?")

    # Detect framework
    report.framework = _detect_framework(path, all_deps)
    logger.info(f"Framework detected: {report.framework}")

    # Detect package manager
    report.package_manager = _detect_package_manager(path)

    # Detect TypeScript
    report.has_typescript = (
        "typescript" in all_deps
        or (path / "tsconfig.json").exists()
    )

    # Detect auth
    report.has_auth, report.auth_provider = _detect_auth(all_deps)

    # Detect database
    report.has_database, report.db_provider = _detect_database(all_deps)

    # Check config files
    report.has_vercel_config = (
        (path / "vercel.json").exists()
        or (path / "vercel.ts").exists()
    )
    report.has_gitignore = (path / ".gitignore").exists()
    report.has_env_example = (
        (path / ".env.example").exists()
        or (path / ".env.sample").exists()
    )

    if not report.has_gitignore:
        report.warnings.append(".gitignore is MISSING — secrets could be committed")

    # Scan files
    source_files = []
    total_size = 0
    file_count = 0

    for root, dirs, files in os.walk(path):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SCAN_SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            rel = fpath.relative_to(path)

            if fname in SCAN_SKIP_FILES:
                continue

            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            total_size += size
            file_count += 1

            ext = fpath.suffix.lower()
            if ext in SCAN_EXTENSIONS:
                source_files.append(str(rel))

    report.file_count = file_count
    report.total_size_mb = total_size / (1024 * 1024)
    report.source_files = source_files

    # Detect entry points and API routes
    report.entry_points = _detect_entry_points(path, report.framework, source_files)
    report.has_api_routes = _detect_api_routes(source_files)

    # Detect env vars needed
    report.env_vars_needed = _detect_env_vars(path, source_files)

    logger.info(f"Scan complete: {file_count} files, {report.total_size_mb:.2f} MB")
    return report


def _read_package_json(path: Path) -> dict | None:
    pkg_path = path / "package.json"
    if not pkg_path.exists():
        return None
    try:
        with open(pkg_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read package.json: {e}")
        return None


def _detect_framework(path: Path, deps: dict) -> str:
    for framework, rules in FRAMEWORK_DETECTION.items():
        # Check config files first (most specific)
        for config_file in rules["files"]:
            if (path / config_file).exists():
                return framework
        # Check dependencies
        if rules["deps"] and all(d in deps for d in rules["deps"]):
            return framework
    # Fallback: check for index.html (static site)
    if (path / "index.html").exists() or (path / "public" / "index.html").exists():
        return "static"
    return "unknown"


def _detect_package_manager(path: Path) -> str:
    if (path / "bun.lockb").exists():
        return "bun"
    if (path / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (path / "yarn.lock").exists():
        return "yarn"
    return "npm"


def _detect_auth(deps: dict) -> tuple[bool, str]:
    for provider, packages in AUTH_PACKAGES.items():
        for pkg in packages:
            if pkg in deps:
                return True, provider
    return False, ""


def _detect_database(deps: dict) -> tuple[bool, str]:
    for provider, packages in DB_PACKAGES.items():
        for pkg in packages:
            if pkg in deps:
                return True, provider
    return False, ""


def _detect_entry_points(path: Path, framework: str, source_files: list[str]) -> list[str]:
    entries = []

    if framework == "nextjs":
        # App Router pages
        for f in source_files:
            normalized = f.replace("\\", "/")
            if "/app/" in normalized and ("page.tsx" in normalized or "page.jsx" in normalized or "page.js" in normalized):
                entries.append(f)
        # Pages Router
        for f in source_files:
            normalized = f.replace("\\", "/")
            if "/pages/" in normalized and ("index." in normalized or "_app." in normalized):
                entries.append(f)
    elif framework in ("react-vite", "react-cra", "vue-vite"):
        for f in source_files:
            normalized = f.replace("\\", "/")
            if normalized.endswith(("main.tsx", "main.jsx", "main.ts", "main.js", "index.tsx", "index.jsx", "App.tsx", "App.jsx")):
                entries.append(f)
    elif framework == "static":
        for f in source_files:
            if f.endswith("index.html"):
                entries.append(f)
    else:
        # Generic: look for common entry points
        for f in source_files:
            normalized = f.replace("\\", "/")
            if "page." in normalized or "index." in normalized or "App." in normalized:
                entries.append(f)

    return entries[:20]  # Cap at 20


def _detect_api_routes(source_files: list[str]) -> bool:
    for f in source_files:
        normalized = f.replace("\\", "/")
        if "/api/" in normalized and ("route." in normalized or "index." in normalized):
            return True
    return False


def _detect_env_vars(path: Path, source_files: list[str]) -> list[str]:
    env_vars = set()

    # Read .env.example / .env.sample
    for env_file in [".env.example", ".env.sample", ".env.local.example"]:
        env_path = path / env_file
        if env_path.exists():
            try:
                with open(env_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            var_name = line.split("=", 1)[0].strip()
                            env_vars.add(var_name)
            except IOError:
                pass

    # Scan source files for process.env. and import.meta.env.
    import re
    env_pattern = re.compile(r'(?:process\.env\.|import\.meta\.env\.)([A-Z_][A-Z0-9_]*)')

    for rel_file in source_files:
        fpath = path / rel_file
        if not fpath.suffix in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            matches = env_pattern.findall(content)
            env_vars.update(matches)
        except IOError:
            pass

    # Remove common ones that are auto-set
    auto_set = {"NODE_ENV", "VERCEL", "VERCEL_URL", "VERCEL_ENV", "CI", "PORT"}
    env_vars -= auto_set

    return sorted(env_vars)

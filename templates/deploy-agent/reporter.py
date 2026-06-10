"""DeployAgent — Report Generator.

Formats and prints scan reports, security reports, and final deployment summary.
"""

import logging

logger = logging.getLogger(__name__)


def print_scan_report(scan_report) -> None:
    """Print the project scan report to console."""
    print("\n" + scan_report.summary())
    print()


def print_security_report(security_report) -> None:
    """Print the security audit report to console."""
    print(f"\n=== Security Audit Results ===")
    print(f"Summary: {security_report.summary}")
    print()

    if not security_report.findings:
        print("  No issues found. Project is clean!")
        return

    # Group by severity
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        findings = [f for f in security_report.findings if f.severity == sev]
        if not findings:
            continue

        icon = {"CRITICAL": "!!!", "HIGH": "!!", "MEDIUM": "!", "LOW": "~", "INFO": "i"}[sev]
        print(f"\n  [{icon}] {sev} ({len(findings)})")
        for f in findings:
            loc = f" @ {f.file_path}:{f.line_number}" if f.file_path else ""
            print(f"      - {f.title}{loc}")
            if f.recommendation:
                print(f"        Fix: {f.recommendation}")
    print()


def print_final_report(
    scan_report,
    security_report=None,
    auth_result: dict = None,
    repo_url: str = "",
    deploy_result: dict = None,
) -> None:
    """Print the final deployment summary."""
    print("\n" + "=" * 60)
    print("  DEPLOYMENT COMPLETE")
    print("=" * 60)
    print()

    # Project info
    print(f"  Project:    {scan_report.project_name}")
    print(f"  Framework:  {scan_report.framework}")
    print(f"  TypeScript: {'Yes' if scan_report.has_typescript else 'No'}")
    print()

    # Security
    if security_report:
        status = "BLOCKED" if security_report.deploy_blocked else "PASSED"
        print(f"  Security:   {status} ({security_report.summary})")
    else:
        print(f"  Security:   Skipped")

    # Auth
    if auth_result:
        auth_status = auth_result.get("status", "unknown")
        print(f"  Auth:       {auth_status}")
        if auth_result.get("provider"):
            print(f"  Provider:   {auth_result['provider']}")
    else:
        print(f"  Auth:       Skipped")

    # Git
    if repo_url:
        print(f"  Repository: {repo_url}")
    else:
        print(f"  Repository: Not pushed")

    # Deploy
    if deploy_result:
        print(f"  Preview:    {deploy_result.get('preview_url', 'N/A')}")
        print(f"  Production: {deploy_result.get('production_url', 'N/A')}")
        print(f"  Status:     {deploy_result.get('status', 'unknown')}")
    else:
        print(f"  Deploy:     Not deployed")

    # Warnings
    all_warnings = scan_report.warnings[:]
    if security_report and security_report.deploy_blocked:
        all_warnings.append("Security audit found critical/high issues — review SECURITY_REPORT.md")

    if all_warnings:
        print(f"\n  --- Warnings ---")
        for w in all_warnings:
            print(f"  ! {w}")

    print()
    print("=" * 60)
    print()

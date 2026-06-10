"""DeployAgent — Entry Point.

Orchestrates the full deploy pipeline:
  scan → security audit → auth setup → git push → vercel deploy

Usage:
  python main.py --project /path/to/project
  python main.py --project /path/to/project --dry-run
  python main.py --project /path/to/project --scan-only
  python main.py --project /path/to/project --skip-auth
  python main.py --project /path/to/project --skip-security
  python main.py --project /path/to/project --repo-url https://github.com/your-user/existing-repo
"""

import argparse
import logging
import sys

from config import LOG_DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)


def ask_user(question: str, default: str = "y") -> bool:
    """Ask the user a yes/no question. Returns True for yes."""
    suffix = " [Y/n] " if default == "y" else " [y/N] "
    try:
        answer = input(question + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default == "y"
    if not answer:
        return default == "y"
    return answer in ("y", "yes", "si", "s")


def ask_user_choice(question: str, options: list[str]) -> str:
    """Ask the user to pick from a list of options."""
    print(f"\n{question}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            choice = input(f"Choose [1-{len(options)}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return options[0]
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"  Invalid choice. Enter a number 1-{len(options)}.")


def ask_user_input(question: str, default: str = "") -> str:
    """Ask the user for free-text input."""
    suffix = f" [{default}]: " if default else ": "
    try:
        answer = input(question + suffix).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return answer or default


def run_pipeline(args: argparse.Namespace) -> None:
    """Execute the full deploy pipeline."""
    from scanner import scan_project
    from security_audit import run_audit
    from reporter import print_scan_report, print_security_report, print_final_report

    project_path = args.project
    dry_run = args.dry_run

    if dry_run:
        print("\n*** DRY RUN MODE — no changes will be made ***\n")

    # === STEP 1: SCAN ===
    print("\n" + "=" * 60)
    print("  STEP 1/5: PROJECT SCAN")
    print("=" * 60)

    scan_report = scan_project(project_path)
    print_scan_report(scan_report)

    if scan_report.framework == "unknown":
        if not ask_user("Framework not recognized. Continue anyway?", "n"):
            print("Aborted.")
            sys.exit(1)

    if args.scan_only:
        print("\n--scan-only: stopping after scan.")
        return

    # === STEP 2: SECURITY AUDIT ===
    if not args.skip_security:
        print("\n" + "=" * 60)
        print("  STEP 2/5: SECURITY AUDIT")
        print("=" * 60)

        security_report = run_audit(project_path, scan_report)
        print_security_report(security_report)

        if security_report.deploy_blocked:
            print("\n!!! DEPLOY BLOCKED — Critical/High vulnerabilities found !!!")
            if not ask_user("Override and continue despite security issues?", "n"):
                print("Aborted. Fix the issues above and re-run.")
                sys.exit(1)
            print("WARNING: Proceeding with known vulnerabilities.")
    else:
        print("\n--skip-security: skipping security audit.")
        security_report = None

    # === STEP 3: AUTH SETUP ===
    if not args.skip_auth:
        print("\n" + "=" * 60)
        print("  STEP 3/5: AUTH SETUP")
        print("=" * 60)

        from auth_setup import check_and_setup_auth
        auth_result = check_and_setup_auth(project_path, scan_report, dry_run)
    else:
        print("\n--skip-auth: skipping auth setup.")
        auth_result = {"status": "skipped"}

    # === STEP 4: GIT PUSH ===
    print("\n" + "=" * 60)
    print("  STEP 4/5: GIT REPOSITORY")
    print("=" * 60)

    from git_manager import setup_repo
    repo_url = setup_repo(
        project_path,
        repo_url=args.repo_url,
        dry_run=dry_run,
    )

    # === STEP 5: VERCEL DEPLOY ===
    print("\n" + "=" * 60)
    print("  STEP 5/5: VERCEL DEPLOY")
    print("=" * 60)

    from deployer import deploy
    deploy_result = deploy(
        project_path,
        repo_url=repo_url,
        scan_report=scan_report,
        dry_run=dry_run,
    )

    # === FINAL REPORT ===
    print_final_report(
        scan_report=scan_report,
        security_report=security_report,
        auth_result=auth_result,
        repo_url=repo_url,
        deploy_result=deploy_result,
    )


def main():
    parser = argparse.ArgumentParser(
        description="DeployAgent — Scan, secure, and deploy web projects to Vercel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Path to the project directory to deploy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate without making changes",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only run project scan, then stop",
    )
    parser.add_argument(
        "--skip-auth",
        action="store_true",
        help="Skip authentication setup",
    )
    parser.add_argument(
        "--skip-security",
        action="store_true",
        help="Skip security audit",
    )
    parser.add_argument(
        "--repo-url",
        default=None,
        help="Use existing Git repo URL instead of creating new one",
    )

    args = parser.parse_args()

    # Validate project path
    from pathlib import Path
    if not Path(args.project).is_dir():
        print(f"ERROR: Project path not found: {args.project}")
        sys.exit(1)

    try:
        run_pipeline(args)
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()

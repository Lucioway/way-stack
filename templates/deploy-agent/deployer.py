"""DeployAgent — Vercel Deployer.

Handles Vercel linking, environment variables, preview/production deployment,
and security headers configuration.
"""

import json
import logging
import subprocess
from pathlib import Path

from config import SECURITY_HEADERS

logger = logging.getLogger(__name__)


def deploy(
    project_path: str,
    repo_url: str = "",
    scan_report=None,
    dry_run: bool = False,
) -> dict:
    """Deploy project to Vercel.

    Returns dict with preview_url, production_url, status.
    """
    from main import ask_user, ask_user_input

    path = Path(project_path).resolve()
    result = {"preview_url": "", "production_url": "", "status": "pending"}

    # Check vercel CLI
    if not _check_vercel_cli():
        print("\n  ERROR: Vercel CLI not installed.")
        print("  Install with: npm i -g vercel")
        result["status"] = "failed"
        return result

    if dry_run:
        print("\n  [DRY RUN] Would deploy to Vercel:")
        print(f"    - Link project: {path.name}")
        print(f"    - Configure env vars")
        print(f"    - Deploy preview → deploy production")
        result["status"] = "dry-run"
        result["preview_url"] = f"https://{path.name}-preview.vercel.app"
        result["production_url"] = f"https://{path.name}.vercel.app"
        return result

    # 1. Install dependencies if needed
    _install_dependencies(path, scan_report)

    # 2. Add security headers to vercel.json
    _ensure_security_headers(path)

    # 3. Link to Vercel
    print("\n  Linking project to Vercel...")
    if not _vercel_link(path):
        print("  ERROR: Failed to link to Vercel.")
        print("  Try manually: cd <project> && vercel link")
        result["status"] = "failed"
        return result

    # 4. Pull env vars (provisions OIDC if needed)
    print("  Pulling environment variables...")
    _vercel_env_pull(path)

    # 5. Configure missing env vars
    _configure_env_vars(path, scan_report)

    # 6. Deploy preview
    print("\n  Deploying preview...")
    preview_url = _vercel_deploy(path, prod=False)
    if preview_url:
        result["preview_url"] = preview_url
        print(f"\n  Preview URL: {preview_url}")
    else:
        print("  WARNING: Preview deploy may have failed. Check Vercel dashboard.")

    # 7. Ask for production deploy
    if preview_url:
        print(f"\n  Preview is live at: {preview_url}")
        if ask_user("  Deploy to production?"):
            print("  Deploying to production...")
            prod_url = _vercel_deploy(path, prod=True)
            if prod_url:
                result["production_url"] = prod_url
                result["status"] = "deployed"
                print(f"\n  Production URL: {prod_url}")
            else:
                print("  WARNING: Production deploy may have failed.")
                result["status"] = "preview-only"
        else:
            result["status"] = "preview-only"
            print("  Skipping production deploy. Preview is still accessible.")
    else:
        result["status"] = "failed"

    return result


def _check_vercel_cli() -> bool:
    """Check if Vercel CLI is installed."""
    try:
        result = subprocess.run(
            ["vercel", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _install_dependencies(path: Path, scan_report=None):
    """Install project dependencies if node_modules doesn't exist."""
    if (path / "node_modules").is_dir():
        print("  Dependencies already installed.")
        return

    pkg_manager = "npm"
    if scan_report:
        pkg_manager = scan_report.package_manager

    cmd_map = {
        "npm": ["npm", "install"],
        "pnpm": ["pnpm", "install"],
        "yarn": ["yarn", "install"],
        "bun": ["bun", "install"],
    }
    cmd = cmd_map.get(pkg_manager, ["npm", "install"])

    print(f"  Installing dependencies with {pkg_manager}...")
    try:
        subprocess.run(
            cmd, cwd=str(path), capture_output=True, text=True, timeout=300,
        )
        print("  Dependencies installed.")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  WARNING: Dependency install failed: {e}")


def _ensure_security_headers(path: Path):
    """Add security headers to vercel.json if not present."""
    vercel_json_path = path / "vercel.json"

    config = {}
    if vercel_json_path.exists():
        try:
            config = json.loads(vercel_json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            config = {}

    # Check if headers already configured
    existing_headers = config.get("headers", [])
    has_security_headers = False
    for h in existing_headers:
        header_keys = {hh.get("key", "") for hh in h.get("headers", [])}
        if "X-Frame-Options" in header_keys or "Strict-Transport-Security" in header_keys:
            has_security_headers = True
            break

    if has_security_headers:
        print("  Security headers already configured in vercel.json.")
        return

    # Add security headers
    header_entry = {
        "source": "/(.*)",
        "headers": SECURITY_HEADERS,
    }

    if "headers" not in config:
        config["headers"] = []
    config["headers"].append(header_entry)

    vercel_json_path.write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )
    print("  Added security headers to vercel.json.")


def _vercel_link(path: Path) -> bool:
    """Link project to Vercel."""
    # Check if already linked
    if (path / ".vercel" / "project.json").exists():
        print("  Already linked to Vercel.")
        return True

    try:
        result = subprocess.run(
            ["vercel", "link", "--yes"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.error(f"vercel link failed: {e}")
        return False


def _vercel_env_pull(path: Path):
    """Pull environment variables from Vercel."""
    try:
        subprocess.run(
            ["vercel", "env", "pull", ".env.local"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("vercel env pull failed")


def _configure_env_vars(path: Path, scan_report=None):
    """Check and configure required environment variables."""
    from main import ask_user_input

    if not scan_report or not scan_report.env_vars_needed:
        return

    # Read existing .env.local
    env_local = path / ".env.local"
    existing_vars = set()
    if env_local.exists():
        try:
            for line in env_local.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.startswith("#") and "=" in line:
                    var_name = line.split("=", 1)[0].strip()
                    if line.split("=", 1)[1].strip():  # has a value
                        existing_vars.add(var_name)
        except IOError:
            pass

    # Find missing vars
    missing = [v for v in scan_report.env_vars_needed if v not in existing_vars]
    if not missing:
        print("  All environment variables are configured.")
        return

    print(f"\n  Missing environment variables ({len(missing)}):")
    for var in missing:
        print(f"    - {var}")

    print("\n  These will need to be set in Vercel Dashboard or via 'vercel env add'.")
    print("  Marketplace integrations (Clerk, Supabase) auto-provision their vars.")


def _vercel_deploy(path: Path, prod: bool = False) -> str:
    """Deploy to Vercel. Returns the deployment URL."""
    cmd = ["vercel"]
    if prod:
        cmd.append("--prod")
    cmd.append("--yes")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=600,  # 10 min for large builds
        )

        if result.returncode == 0:
            # The URL is usually the last non-empty line of stdout
            lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
            for line in reversed(lines):
                if "vercel.app" in line or "https://" in line:
                    # Clean ANSI codes
                    import re
                    clean = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
                    return clean
            return lines[-1] if lines else ""
        else:
            logger.error(f"vercel deploy failed: {result.stderr[:500]}")
            print(f"  Deploy error: {result.stderr[:200]}")
            return ""

    except FileNotFoundError:
        print("  ERROR: Vercel CLI not found.")
        return ""
    except subprocess.TimeoutExpired:
        print("  ERROR: Deploy timed out (>10 min).")
        return ""

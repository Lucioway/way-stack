"""DeployAgent — Git Repository Manager.

Handles git initialization, .gitignore setup, repo creation on GitHub,
and pushing code. GitHub owner comes from config.GITHUB_USER
(GITHUB_OWNER env var, or auto-detected from gh CLI auth).
"""

import logging
import subprocess
from pathlib import Path

from config import GITHUB_USER, GITIGNORE_REQUIRED

logger = logging.getLogger(__name__)


def setup_repo(project_path: str, repo_url: str = None, dry_run: bool = False) -> str:
    """Set up git repo and push to GitHub.

    Args:
        project_path: Path to the project directory.
        repo_url: Optional existing repo URL. If None, creates new one.
        dry_run: If True, simulate without making changes.

    Returns:
        The GitHub repo URL.
    """
    from main import ask_user, ask_user_choice, ask_user_input

    global GITHUB_USER
    if not GITHUB_USER:
        GITHUB_USER = ask_user_input(
            "  GitHub owner not detected (set GITHUB_OWNER env var to skip this). Username/org"
        )

    path = Path(project_path).resolve()
    project_name = path.name

    # Check if already a git repo
    is_git = (path / ".git").is_dir()
    if is_git:
        print(f"\n  Git repo already initialized.")
        # Check for existing remote
        existing_remote = _get_remote_url(path)
        if existing_remote:
            print(f"  Remote: {existing_remote}")
            if ask_user("  Use existing remote and push?"):
                if not dry_run:
                    _ensure_gitignore(path)
                    _commit_all(path, "Update via DeployAgent")
                    _push(path)
                return existing_remote

    # Decide: create new repo or use provided URL
    if repo_url:
        print(f"\n  Using provided repo: {repo_url}")
    else:
        choice = ask_user_choice(
            "Git repository setup:",
            [
                f"Create new private repo: github.com/{GITHUB_USER}/{project_name}",
                "I'll provide a repo URL",
                "Skip git (not recommended)",
            ],
        )

        if "Skip" in choice:
            print("  Skipping git setup.")
            return ""
        elif "provide" in choice.lower():
            repo_url = ask_user_input("  Enter repo URL (https://github.com/...)")
            if not repo_url:
                print("  No URL provided, skipping git.")
                return ""
        else:
            # Create new repo
            repo_name = ask_user_input("  Repo name", project_name)
            repo_name = _sanitize_repo_name(repo_name)

            if dry_run:
                print(f"\n  [DRY RUN] Would create: github.com/{GITHUB_USER}/{repo_name}")
                return f"https://github.com/{GITHUB_USER}/{repo_name}"

            repo_url = _create_github_repo(repo_name)
            if not repo_url:
                print("  ERROR: Failed to create GitHub repo. Do it manually and re-run with --repo-url.")
                return ""

    if dry_run:
        print(f"\n  [DRY RUN] Would push to {repo_url}")
        return repo_url

    # Ensure .gitignore is correct
    _ensure_gitignore(path)

    # Init git if needed
    if not is_git:
        _run_git(path, ["init"])
        _run_git(path, ["branch", "-M", "main"])
        print("  Git initialized.")

    # Add remote
    existing_remote = _get_remote_url(path)
    if existing_remote and existing_remote != repo_url:
        _run_git(path, ["remote", "set-url", "origin", repo_url])
        print(f"  Remote updated to {repo_url}")
    elif not existing_remote:
        _run_git(path, ["remote", "add", "origin", repo_url])
        print(f"  Remote added: {repo_url}")

    # Stage, commit, push
    _commit_all(path, "Initial commit — deployed via DeployAgent")
    _push(path)

    print(f"\n  Repository: {repo_url}")
    return repo_url


def _run_git(path: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command."""
    cmd = ["git"] + args
    try:
        return subprocess.run(
            cmd,
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=60,
            check=check,
        )
    except subprocess.CalledProcessError as e:
        logger.warning(f"git {' '.join(args)} failed: {e.stderr[:200]}")
        raise
    except subprocess.TimeoutExpired:
        logger.error(f"git {' '.join(args)} timed out")
        raise


def _get_remote_url(path: Path) -> str:
    """Get the current origin remote URL."""
    try:
        result = _run_git(path, ["remote", "get-url", "origin"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _create_github_repo(repo_name: str) -> str:
    """Create a private GitHub repo using gh CLI."""
    full_name = f"{GITHUB_USER}/{repo_name}"
    print(f"\n  Creating private repo: {full_name}")

    try:
        result = subprocess.run(
            ["gh", "repo", "create", full_name, "--private", "--confirm"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            # Try without --confirm (newer gh versions)
            result = subprocess.run(
                ["gh", "repo", "create", full_name, "--private"],
                capture_output=True,
                text=True,
                timeout=30,
            )

        if result.returncode == 0:
            url = f"https://github.com/{full_name}.git"
            print(f"  Created: {url}")
            return url
        else:
            # Check if repo already exists
            if "already exists" in result.stderr.lower():
                print(f"  Repo already exists: {full_name}")
                return f"https://github.com/{full_name}.git"
            logger.error(f"gh repo create failed: {result.stderr}")
            return ""

    except FileNotFoundError:
        print("  ERROR: 'gh' CLI not found. Install it: https://cli.github.com/")
        print("  Or create the repo manually and re-run with --repo-url.")
        return ""
    except subprocess.TimeoutExpired:
        print("  ERROR: gh command timed out.")
        return ""


def _ensure_gitignore(path: Path):
    """Ensure .gitignore exists with required entries."""
    gitignore_path = path / ".gitignore"

    existing_lines = set()
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        existing_lines = {
            line.strip() for line in content.splitlines()
            if line.strip() and not line.startswith("#")
        }
    else:
        content = ""

    missing = []
    for entry in GITIGNORE_REQUIRED:
        found = False
        for line in existing_lines:
            if entry.rstrip("/") in line:
                found = True
                break
        if not found:
            missing.append(entry)

    if missing:
        additions = "\n# Added by DeployAgent\n" + "\n".join(missing) + "\n"
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write(additions)
        print(f"  .gitignore updated: added {len(missing)} entries")
    else:
        print(f"  .gitignore is complete.")


def _commit_all(path: Path, message: str):
    """Stage all files and commit."""
    _run_git(path, ["add", "-A"])

    # Check if there's anything to commit
    result = _run_git(path, ["status", "--porcelain"], check=False)
    if not result.stdout.strip():
        print("  No changes to commit.")
        return

    try:
        _run_git(path, ["commit", "-m", message])
        print(f"  Committed: {message}")
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr.lower() or "nothing to commit" in e.stdout.lower():
            print("  No changes to commit.")
        else:
            raise


def _push(path: Path):
    """Push to remote."""
    print("  Pushing to remote...")
    try:
        _run_git(path, ["push", "-u", "origin", "main"])
        print("  Push successful!")
    except subprocess.CalledProcessError:
        # Try force push if first push (e.g., empty remote)
        try:
            _run_git(path, ["push", "-u", "origin", "main", "--force-with-lease"])
            print("  Push successful (force-with-lease)!")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: Push failed: {e.stderr[:200]}")
            print("  Try pushing manually: git push -u origin main")


def _sanitize_repo_name(name: str) -> str:
    """Sanitize a repo name for GitHub."""
    import re
    # Replace spaces and special chars with hyphens
    name = re.sub(r'[^a-zA-Z0-9._-]', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Lowercase
    name = name.lower()
    return name or "my-project"

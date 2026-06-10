"""DeployAgent — Authentication Setup.

Detects existing auth in a project and optionally integrates Clerk.
Supports: Next.js, React (Vite/CRA), Astro.
Always asks user confirmation before modifying code.
"""

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def check_and_setup_auth(project_path: str, scan_report, dry_run: bool = False) -> dict:
    """Check if auth exists; if not, offer to set up Clerk."""
    from main import ask_user, ask_user_choice

    path = Path(project_path).resolve()
    result = {"status": "unknown", "provider": "", "changes": []}

    # Check if auth already exists
    if scan_report.has_auth:
        print(f"\n  Auth already detected: {scan_report.auth_provider}")
        print(f"  No changes needed.")
        result["status"] = "existing"
        result["provider"] = scan_report.auth_provider
        return result

    # No auth found — ask user
    print("\n  No authentication found in this project.")
    print("  Options:")
    print("    1. Add Clerk (free tier, 10K MAU, native Vercel integration)")
    print("    2. Skip auth (project will be public)")

    if not ask_user("Add Clerk authentication?", "y"):
        print("  Skipping auth setup.")
        result["status"] = "skipped"
        return result

    if dry_run:
        print("\n  [DRY RUN] Would install Clerk and configure auth.")
        result["status"] = "dry-run"
        result["provider"] = "clerk"
        return result

    # Determine setup based on framework
    framework = scan_report.framework
    if framework == "nextjs":
        return _setup_clerk_nextjs(path, scan_report)
    elif framework in ("react-vite", "react-cra"):
        return _setup_clerk_react(path, scan_report)
    elif framework == "astro":
        return _setup_clerk_astro(path, scan_report)
    else:
        print(f"\n  Clerk auto-setup not available for framework: {framework}")
        print(f"  You can manually install Clerk following: https://clerk.com/docs")
        result["status"] = "manual-required"
        result["provider"] = "clerk"
        return result


def _run_install(path: Path, package: str, pkg_manager: str = "npm") -> bool:
    """Install an npm package."""
    cmd_map = {
        "npm": ["npm", "install", package],
        "pnpm": ["pnpm", "add", package],
        "yarn": ["yarn", "add", package],
        "bun": ["bun", "add", package],
    }
    cmd = cmd_map.get(pkg_manager, ["npm", "install", package])

    try:
        print(f"  Installing {package}...")
        result = subprocess.run(
            cmd, cwd=str(path), capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.warning(f"Install failed: {result.stderr[:200]}")
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Install error: {e}")
        return False


def _setup_clerk_nextjs(path: Path, scan_report) -> dict:
    """Set up Clerk for a Next.js project."""
    from main import ask_user
    result = {"status": "configured", "provider": "clerk", "changes": []}
    pkg_manager = scan_report.package_manager

    # 1. Install @clerk/nextjs
    if not _run_install(path, "@clerk/nextjs", pkg_manager):
        print("  ERROR: Failed to install @clerk/nextjs")
        result["status"] = "failed"
        return result
    result["changes"].append("Installed @clerk/nextjs")

    # 2. Create or update proxy.ts / middleware.ts
    proxy_path = _find_proxy_or_middleware(path)
    if proxy_path:
        print(f"\n  Found existing {proxy_path.name}.")
        if ask_user(f"  Add clerkMiddleware() to {proxy_path.name}?"):
            _add_clerk_to_proxy(proxy_path)
            result["changes"].append(f"Updated {proxy_path.name} with clerkMiddleware()")
    else:
        # Create proxy.ts in the right location
        src_dir = path / "src"
        if src_dir.is_dir():
            proxy_path = src_dir / "proxy.ts"
        else:
            proxy_path = path / "proxy.ts"
        _create_clerk_proxy(proxy_path)
        result["changes"].append(f"Created {proxy_path.relative_to(path)}")

    # 3. Add ClerkProvider to layout
    layout_path = _find_layout(path)
    if layout_path:
        print(f"\n  Found layout: {layout_path.relative_to(path)}")
        if ask_user("  Add <ClerkProvider> to layout?"):
            _add_clerk_provider_to_layout(layout_path)
            result["changes"].append(f"Added ClerkProvider to {layout_path.relative_to(path)}")
    else:
        print("  WARNING: No layout.tsx found. Add <ClerkProvider> manually.")
        result["changes"].append("WARNING: ClerkProvider not added — no layout found")

    # 4. Create sign-in and sign-up pages if missing
    app_dir = _find_app_dir(path)
    if app_dir:
        _create_auth_pages(app_dir, result)

    # 5. Create .env.local.example with Clerk vars
    _create_clerk_env_example(path, result)

    print(f"\n  Clerk setup complete! {len(result['changes'])} changes made.")
    print(f"\n  IMPORTANT: You must complete Clerk setup:")
    print(f"    1. Run 'vercel integration add clerk' in the terminal")
    print(f"    2. Complete setup in Vercel Dashboard")
    print(f"    3. Clerk will auto-provision CLERK_SECRET_KEY and PUBLISHABLE_KEY")

    return result


def _setup_clerk_react(path: Path, scan_report) -> dict:
    """Set up Clerk for a React (Vite/CRA) project."""
    result = {"status": "configured", "provider": "clerk", "changes": []}
    pkg_manager = scan_report.package_manager

    if not _run_install(path, "@clerk/clerk-react", pkg_manager):
        result["status"] = "failed"
        return result
    result["changes"].append("Installed @clerk/clerk-react")

    # Find main.tsx / main.jsx / index.tsx
    main_file = None
    for name in ["src/main.tsx", "src/main.jsx", "src/index.tsx", "src/index.jsx"]:
        candidate = path / name
        if candidate.exists():
            main_file = candidate
            break

    if main_file:
        _add_clerk_provider_to_react_main(main_file)
        result["changes"].append(f"Added ClerkProvider to {main_file.relative_to(path)}")
    else:
        print("  WARNING: No main.tsx found. Add <ClerkProvider> manually.")

    _create_clerk_env_example(path, result)
    print(f"\n  Clerk setup complete for React!")
    return result


def _setup_clerk_astro(path: Path, scan_report) -> dict:
    """Set up Clerk for Astro."""
    result = {"status": "configured", "provider": "clerk", "changes": []}
    if not _run_install(path, "@clerk/astro", scan_report.package_manager):
        result["status"] = "failed"
        return result
    result["changes"].append("Installed @clerk/astro")
    print("  See https://clerk.com/docs/references/astro/overview for Astro config.")
    _create_clerk_env_example(path, result)
    return result


def _find_proxy_or_middleware(path: Path) -> Path | None:
    """Find proxy.ts or middleware.ts in standard locations."""
    for loc in [path / "src", path]:
        for name in ["proxy.ts", "proxy.js", "middleware.ts", "middleware.js"]:
            candidate = loc / name
            if candidate.exists():
                return candidate
    return None


def _find_layout(path: Path) -> Path | None:
    """Find the root layout.tsx in App Router."""
    for loc in [path / "src" / "app", path / "app"]:
        for name in ["layout.tsx", "layout.jsx", "layout.js"]:
            candidate = loc / name
            if candidate.exists():
                return candidate
    return None


def _find_app_dir(path: Path) -> Path | None:
    """Find the app directory."""
    for loc in [path / "src" / "app", path / "app"]:
        if loc.is_dir():
            return loc
    return None


def _create_clerk_proxy(proxy_path: Path):
    """Create proxy.ts with clerkMiddleware."""
    content = '''import { clerkMiddleware } from "@clerk/nextjs/server";

export const proxy = clerkMiddleware();

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
'''
    proxy_path.write_text(content, encoding="utf-8")
    print(f"  Created {proxy_path.name} with clerkMiddleware()")


def _add_clerk_to_proxy(proxy_path: Path):
    """Add clerkMiddleware to existing proxy/middleware file."""
    content = proxy_path.read_text(encoding="utf-8")

    if "clerkMiddleware" in content:
        print("  clerkMiddleware already present — skipping.")
        return

    # Prepend import
    import_line = 'import { clerkMiddleware } from "@clerk/nextjs/server";\n'
    if "clerkMiddleware" not in content:
        content = import_line + content

    # Replace export if simple
    if "export const proxy" in content or "export async function proxy" in content:
        print("  WARNING: Proxy already has custom logic. Please wrap with clerkMiddleware manually.")
    else:
        content += '\n// Clerk auth middleware\nexport const proxy = clerkMiddleware();\n'

    proxy_path.write_text(content, encoding="utf-8")


def _add_clerk_provider_to_layout(layout_path: Path):
    """Add ClerkProvider wrapper to root layout."""
    content = layout_path.read_text(encoding="utf-8")

    if "ClerkProvider" in content:
        print("  ClerkProvider already present — skipping.")
        return

    # Add import at top
    import_line = 'import { ClerkProvider } from "@clerk/nextjs";\n'
    content = import_line + content

    # Wrap {children} with <ClerkProvider>
    # Simple heuristic: find {children} and wrap
    if "{children}" in content:
        content = content.replace(
            "{children}",
            "<ClerkProvider>{children}</ClerkProvider>",
            1,
        )
    else:
        print("  WARNING: Could not find {children} in layout. Add <ClerkProvider> manually.")

    layout_path.write_text(content, encoding="utf-8")


def _add_clerk_provider_to_react_main(main_path: Path):
    """Add ClerkProvider to React main entry."""
    content = main_path.read_text(encoding="utf-8")

    if "ClerkProvider" in content:
        print("  ClerkProvider already present — skipping.")
        return

    import_line = 'import { ClerkProvider } from "@clerk/clerk-react";\n'
    content = import_line + content

    # Wrap <App /> with <ClerkProvider>
    if "<App" in content:
        content = content.replace("<App", "<ClerkProvider><App", 1)
        content = content.replace("</App>", "</App></ClerkProvider>", 1)
        # Handle self-closing <App />
        if "<ClerkProvider><App />" in content:
            content = content.replace(
                "<ClerkProvider><App />",
                "<ClerkProvider><App /></ClerkProvider>",
            )

    main_path.write_text(content, encoding="utf-8")


def _create_auth_pages(app_dir: Path, result: dict):
    """Create sign-in and sign-up pages for Next.js App Router."""
    pages = {
        "sign-in/[[...sign-in]]/page.tsx": '''import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  );
}
''',
        "sign-up/[[...sign-up]]/page.tsx": '''import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp />
    </div>
  );
}
''',
    }

    for rel_path, content in pages.items():
        page_path = app_dir / rel_path
        if page_path.exists():
            print(f"  {rel_path} already exists — skipping.")
            continue
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text(content, encoding="utf-8")
        result["changes"].append(f"Created {rel_path}")
        print(f"  Created {rel_path}")


def _create_clerk_env_example(path: Path, result: dict):
    """Create or update .env.example with Clerk variables."""
    env_path = path / ".env.example"
    existing = ""
    if env_path.exists():
        existing = env_path.read_text(encoding="utf-8", errors="ignore")

    clerk_vars = """
# Clerk Authentication
# These are auto-provisioned by Vercel Marketplace (vercel integration add clerk)
CLERK_SECRET_KEY=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
"""

    if "CLERK_SECRET_KEY" not in existing:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(clerk_vars)
        result["changes"].append("Added Clerk vars to .env.example")

"""DeployAgent — Centralized configuration."""

import os
import subprocess
from pathlib import Path


def _detect_github_user() -> str:
    """Detect the authenticated GitHub user via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


# === GitHub ===
# Override with GITHUB_OWNER env var; falls back to the gh-authenticated user.
GITHUB_USER = os.environ.get("GITHUB_OWNER") or _detect_github_user()
GITHUB_DEFAULT_VISIBILITY = "private"

# === Vercel ===
VERCEL_DOMAIN_SUFFIX = ".vercel.app"

# === Framework Detection (order: most specific first) ===
FRAMEWORK_DETECTION = {
    "nextjs": {
        "deps": ["next"],
        "files": ["next.config.ts", "next.config.js", "next.config.mjs"],
    },
    "nuxt": {
        "deps": ["nuxt"],
        "files": ["nuxt.config.ts", "nuxt.config.js"],
    },
    "sveltekit": {
        "deps": ["@sveltejs/kit"],
        "files": ["svelte.config.js"],
    },
    "astro": {
        "deps": ["astro"],
        "files": ["astro.config.mjs", "astro.config.ts"],
    },
    "react-vite": {
        "deps": ["react", "vite"],
        "files": ["vite.config.ts", "vite.config.js"],
    },
    "react-cra": {
        "deps": ["react-scripts"],
        "files": [],
    },
    "vue-vite": {
        "deps": ["vue", "vite"],
        "files": ["vite.config.ts", "vite.config.js"],
    },
    "static": {
        "deps": [],
        "files": ["index.html"],
    },
}

# === Auth Detection ===
AUTH_PACKAGES = {
    "clerk": ["@clerk/nextjs", "@clerk/clerk-react", "@clerk/astro", "@clerk/remix"],
    "next-auth": ["next-auth", "@auth/core"],
    "auth0": ["@auth0/nextjs-auth0", "@auth0/auth0-react"],
    "supabase-auth": ["@supabase/auth-helpers-nextjs", "@supabase/ssr"],
}

# === Database Detection ===
DB_PACKAGES = {
    "supabase": ["@supabase/supabase-js"],
    "prisma": ["@prisma/client"],
    "drizzle": ["drizzle-orm"],
    "neon": ["@neondatabase/serverless"],
    "mongoose": ["mongoose"],
}

# === Secrets Detection Patterns ===
SECRET_PATTERNS = [
    # Generic
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}', "Hardcoded password"),
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']{8,}', "Hardcoded API key"),
    (r'(?i)(secret|token)\s*[=:]\s*["\'][^"\']{8,}', "Hardcoded secret/token"),
    # Provider-specific
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API key"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe live secret key"),
    (r'pk_live_[a-zA-Z0-9]{20,}', "Stripe live publishable key"),
    (r'ghp_[a-zA-Z0-9]{36,}', "GitHub personal access token"),
    (r'ghu_[a-zA-Z0-9]{36,}', "GitHub user token"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key ID"),
    (r'xoxb-[0-9a-zA-Z-]+', "Slack bot token"),
    (r'xoxp-[0-9a-zA-Z-]+', "Slack user token"),
    (r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}', "JWT token"),
    (r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}', "SendGrid API key"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Stripe test secret key"),
]

# === OWASP Detection Patterns ===
OWASP_PATTERNS = [
    (r'dangerouslySetInnerHTML', "XSS", "HIGH", "Use DOMPurify or sanitize input before rendering"),
    (r'\beval\s*\(', "Code Injection", "HIGH", "Avoid eval() — use safe alternatives"),
    (r'new\s+Function\s*\(', "Code Injection", "HIGH", "Avoid dynamic Function creation"),
    (r'document\.write\s*\(', "XSS", "MEDIUM", "Avoid document.write — use DOM manipulation"),
    (r'innerHTML\s*=', "XSS", "MEDIUM", "Use textContent or sanitize before setting innerHTML"),
    (r'cors\(\s*\{\s*origin\s*:\s*["\']?\*', "Permissive CORS", "MEDIUM", "Restrict CORS origin to specific domains"),
    (r'(?i)http://', "Insecure HTTP", "LOW", "Use HTTPS instead of HTTP"),
]

# === Gitignore Required Entries ===
GITIGNORE_REQUIRED = [
    ".env",
    ".env.local",
    ".env*.local",
    "node_modules/",
    ".next/",
    "dist/",
    "build/",
    ".vercel",
    "*.log",
]

# === Files/dirs to skip during scan ===
SCAN_SKIP_DIRS = {
    "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build",
    ".git", "__pycache__", ".vercel", ".turbo", "coverage", ".output",
}

SCAN_SKIP_FILES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb",
}

# === Scannable extensions ===
SCAN_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro",
    ".py", ".json", ".md", ".css", ".scss", ".html", ".env",
    ".mjs", ".cjs",
}

# === Security Headers for vercel.json ===
SECURITY_HEADERS = [
    {"key": "X-Frame-Options", "value": "DENY"},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
    {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
    {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
]

# === Clerk Setup ===
CLERK_ENV_VARS = [
    "CLERK_SECRET_KEY",
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
    "NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in",
    "NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up",
]

# === Logging ===
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

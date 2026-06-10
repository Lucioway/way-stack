#!/usr/bin/env python3
"""
Agent Network Monitor — Real-time monitoring server.
Monitors all agents via log files, launchd status, and process detection.
Serves the visualization dashboard and pushes live updates via WebSocket.

Usage:
    python3 monitor.py              # Start on port 8765
    python3 monitor.py --port 9000  # Custom port
"""

import asyncio
import json
import os
import re
import subprocess
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from http import HTTPStatus
import websockets
from websockets.legacy.server import HTTPResponse

# Root folder containing all your agent project folders.
# Override with the AGENT_WORKSPACE env var, defaults to the parent folder.
BASE_DIR = Path(os.environ.get("AGENT_WORKSPACE", Path(__file__).parent.parent))

# Prefix used to match your launchd labels (e.g. "com.myagents." matches
# com.myagents.report-agent). Override with the LAUNCHD_PREFIX env var.
LAUNCHD_PREFIX = os.environ.get("LAUNCHD_PREFIX", "com.myagents.")

# ─── Agent Definitions ───────────────────────────────────────────────────────
# Replace these examples with your own agents. Each entry:
#   dir            — agent project folder (under BASE_DIR)
#   logs           — main log files, relative to dir
#   error_logs     — error log files, relative to dir
#   launchd_label  — launchd label if scheduled via launchd, else None
#   schedule       — human-readable schedule shown in the dashboard
#   process_grep   — substring to detect the agent in `ps aux`
#   output_dir     — folder whose newest file = "last output", else None

AGENTS = {
    "reporter": {
        "id": "reporter",
        "name": "Reporter",
        "title": "Daily Report Agent",
        "dir": BASE_DIR / "ReportAgent",
        "logs": ["logs/agent.log"],
        "error_logs": ["logs/error.log"],
        "launchd_label": LAUNCHD_PREFIX + "report-agent",
        "schedule": "Daily 08:00",
        "schedule_type": "launchd",
        "process_grep": "ReportAgent",
        "output_dir": "data/reports",
    },
    "scraper": {
        "id": "scraper",
        "name": "Scraper",
        "title": "Weekly Research Agent",
        "dir": BASE_DIR / "ResearchAgent",
        "logs": ["logs/agent.log"],
        "error_logs": ["logs/error.log"],
        "launchd_label": LAUNCHD_PREFIX + "research-agent",
        "schedule": "Weekly Mon 08:00",
        "schedule_type": "launchd",
        "process_grep": "ResearchAgent",
        "output_dir": "data/output",
    },
    "ondemand": {
        "id": "ondemand",
        "name": "Helper",
        "title": "On-Demand Agent",
        "dir": BASE_DIR / "HelperAgent",
        "logs": [],
        "error_logs": [],
        "launchd_label": None,
        "schedule": "On-demand",
        "schedule_type": "manual",
        "process_grep": "HelperAgent",
        "output_dir": "data",
    },
}

# ─── Monitoring Functions ─────────────────────────────────────────────────────

def tail_file(filepath, n=15):
    """Read last n lines of a file."""
    try:
        with open(filepath, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            if size == 0:
                return []
            # Read last chunk
            chunk = min(size, 4096)
            f.seek(-chunk, 2)
            data = f.read().decode("utf-8", errors="replace")
            lines = data.strip().split("\n")
            return lines[-n:]
    except (FileNotFoundError, PermissionError):
        return []


def parse_log_timestamp(line):
    """Try to extract a timestamp from a log line."""
    # Format: 2026-03-26 07:16:38
    match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", line)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return None


def check_launchd():
    """Get status of all launchd agents matching LAUNCHD_PREFIX."""
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=5
        )
        statuses = {}
        for line in result.stdout.split("\n"):
            if LAUNCHD_PREFIX.lower() in line.lower():
                parts = line.split("\t")
                if len(parts) >= 3:
                    pid = parts[0].strip()
                    exit_code = parts[1].strip()
                    label = parts[2].strip()
                    statuses[label] = {
                        "pid": pid if pid != "-" else None,
                        "exit_code": exit_code,
                        "running": pid != "-" and pid != "",
                    }
        return statuses
    except Exception:
        return {}


def check_processes():
    """Check for running agent processes."""
    try:
        result = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except Exception:
        return ""


def get_file_mod_time(filepath):
    """Get file modification time."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(filepath))
    except (FileNotFoundError, PermissionError):
        return None


def get_latest_output(agent_cfg):
    """Get the most recent output file timestamp and name."""
    output_dir = agent_cfg.get("output_dir")
    if not output_dir:
        return None, None

    full_path = agent_cfg["dir"] / output_dir
    if not full_path.exists():
        return None, None

    latest_time = None
    latest_name = None

    try:
        for item in full_path.iterdir():
            mtime = get_file_mod_time(item)
            if mtime and (latest_time is None or mtime > latest_time):
                latest_time = mtime
                latest_name = item.name
    except PermissionError:
        pass

    return latest_time, latest_name


def get_agent_config_hash(agent_cfg):
    """Hash CLAUDE.md to detect config changes."""
    claude_md = agent_cfg["dir"] / "CLAUDE.md"
    try:
        content = claude_md.read_bytes()
        return hashlib.md5(content).hexdigest()[:8]
    except (FileNotFoundError, PermissionError):
        return None


def scan_agent(agent_id, agent_cfg, launchd_status, ps_output):
    """Scan a single agent and return its status."""
    now = datetime.now()
    status = {
        "id": agent_id,
        "name": agent_cfg["name"],
        "title": agent_cfg["title"],
        "schedule": agent_cfg["schedule"],
        "state": "idle",  # idle, running, error, completed
        "launchd": "n/a",
        "lastRun": None,
        "lastLog": None,
        "lastLogTime": None,
        "errors": [],
        "recentLogs": [],
        "outputFile": None,
        "outputTime": None,
        "configHash": get_agent_config_hash(agent_cfg),
        "dirExists": agent_cfg["dir"].exists(),
    }

    # Check launchd
    if agent_cfg["launchd_label"]:
        ld = launchd_status.get(agent_cfg["launchd_label"])
        if ld:
            status["launchd"] = "running" if ld["running"] else "loaded"
            if ld["running"]:
                status["state"] = "running"
                status["pid"] = ld["pid"]
            elif ld["exit_code"] and ld["exit_code"] != "0":
                status["launchd"] = f"exit:{ld['exit_code']}"
        else:
            status["launchd"] = "not_loaded"

    # Check processes
    grep_pattern = agent_cfg.get("process_grep", "")
    if grep_pattern and grep_pattern.lower() in ps_output.lower():
        # Filter out the grep itself and monitor.py
        for line in ps_output.split("\n"):
            if grep_pattern.lower() in line.lower() and "grep" not in line and "monitor.py" not in line:
                status["state"] = "running"
                # Try to extract PID
                parts = line.split()
                if len(parts) > 1:
                    status["pid"] = parts[1]
                break

    # Read main logs
    for log_rel in agent_cfg.get("logs", []):
        log_path = agent_cfg["dir"] / log_rel
        lines = tail_file(log_path, 10)
        if lines:
            status["recentLogs"] = lines[-5:]
            # Find last timestamp
            for line in reversed(lines):
                ts = parse_log_timestamp(line)
                if ts:
                    status["lastLogTime"] = ts.isoformat()
                    status["lastLog"] = line.strip()
                    # If log entry is within last 2 minutes, agent might be running
                    if (now - ts).total_seconds() < 120:
                        status["state"] = "running"
                    break
            # Last non-empty line as lastLog if no timestamp found
            if not status["lastLog"]:
                for line in reversed(lines):
                    if line.strip():
                        status["lastLog"] = line.strip()
                        break

    # Read error logs
    for err_rel in agent_cfg.get("error_logs", []):
        err_path = agent_cfg["dir"] / err_rel
        err_lines = tail_file(err_path, 5)
        for line in err_lines:
            line = line.strip()
            if line and len(line) > 5:
                ts = parse_log_timestamp(line)
                # Only include recent errors (last 7 days)
                if ts and (now - ts).total_seconds() > 7 * 86400:
                    continue
                status["errors"].append(line)

    if status["errors"] and status["state"] != "running":
        status["state"] = "error"

    # Check latest output
    out_time, out_name = get_latest_output(agent_cfg)
    if out_time:
        status["outputTime"] = out_time.isoformat()
        status["outputFile"] = out_name
        if not status["lastLogTime"]:
            status["lastRun"] = out_time.isoformat()

    # Determine lastRun
    if status["lastLogTime"]:
        status["lastRun"] = status["lastLogTime"]
    elif status["outputTime"]:
        status["lastRun"] = status["outputTime"]

    # If state is still idle but has a recent successful log, mark completed
    if status["state"] == "idle" and status["lastRun"]:
        try:
            last = datetime.fromisoformat(status["lastRun"])
            if (now - last).total_seconds() < 86400 and not status["errors"]:
                status["state"] = "completed"
        except ValueError:
            pass

    return status


def scan_all_agents():
    """Scan all agents and return full status."""
    launchd_status = check_launchd()
    ps_output = check_processes()

    agents_status = {}
    for agent_id, agent_cfg in AGENTS.items():
        agents_status[agent_id] = scan_agent(agent_id, agent_cfg, launchd_status, ps_output)

    return {
        "timestamp": datetime.now().isoformat(),
        "agents": agents_status,
    }


# ─── WebSocket + HTTP Server (websockets 15.x) ──────────────────────────────

CLIENTS = set()
HTML_PATH = Path(__file__).parent / "team_visualization.html"

# Track config hashes to detect changes
last_config_hashes = {}


async def broadcast(data):
    """Send data to all connected clients."""
    if CLIENTS:
        msg = json.dumps(data, default=str)
        await asyncio.gather(
            *[client.send(msg) for client in CLIENTS],
            return_exceptions=True,
        )


async def handler(websocket):
    """Handle WebSocket connections."""
    CLIENTS.add(websocket)
    print(f"[+] Client connected ({len(CLIENTS)} total)")

    try:
        # Send initial full state
        state = scan_all_agents()
        await websocket.send(json.dumps(state, default=str))

        # Keep connection alive, handle incoming messages
        async for msg in websocket:
            if msg == "refresh":
                state = scan_all_agents()
                await websocket.send(json.dumps(state, default=str))
    except websockets.ConnectionClosed:
        pass
    finally:
        CLIENTS.discard(websocket)
        print(f"[-] Client disconnected ({len(CLIENTS)} total)")


async def monitor_loop():
    """Periodically scan agents and broadcast updates."""
    global last_config_hashes

    while True:
        await asyncio.sleep(5)

        state = scan_all_agents()

        # Check for config changes
        config_changed = False
        for agent_id, agent_status in state["agents"].items():
            h = agent_status.get("configHash")
            if h and last_config_hashes.get(agent_id) != h:
                if last_config_hashes.get(agent_id) is not None:
                    config_changed = True
                    print(f"[!] Config changed: {agent_id}")
                last_config_hashes[agent_id] = h

        if config_changed:
            state["configChanged"] = True

        await broadcast(state)


def run_http_server(port):
    """Run a simple HTTP server on port+1 to serve the HTML dashboard."""
    import http.server
    import threading

    http_port = port + 1

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(HTML_PATH.parent), **kwargs)

        def do_GET(self):
            if self.path == "/" or self.path == "/index.html":
                self.path = "/team_visualization.html"
            return super().do_GET()

        def log_message(self, format, *args):
            pass  # Suppress HTTP logs

    server = http.server.HTTPServer(("localhost", http_port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return http_port


async def main(port=8765):
    """Start the monitor server."""

    # Start HTTP server for the dashboard
    http_port = run_http_server(port)

    print(f"""
╔══════════════════════════════════════════════╗
║       AI Agent Network Monitor               ║
║                                              ║
║  Dashboard:  http://localhost:{http_port}          ║
║  WebSocket:  ws://localhost:{port}             ║
║                                              ║
║  Press Ctrl+C to stop                        ║
╚══════════════════════════════════════════════╝
    """)

    # Initial scan
    state = scan_all_agents()
    for aid, ast in state["agents"].items():
        icon = {"running": "🟢", "completed": "🔵", "error": "🔴", "idle": "⚪"}.get(ast["state"], "⚪")
        print(f"  {icon} {ast['name']:8s} ({aid}) — {ast['state']} | launchd: {ast['launchd']} | last: {ast.get('lastRun', 'n/a')}")
    print()

    async with websockets.serve(handler, "localhost", port):
        await monitor_loop()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agent Network Monitor")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port (default: 8765). HTTP dashboard on port+1.")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.port))
    except KeyboardInterrupt:
        print("\n[x] Monitor stopped.")

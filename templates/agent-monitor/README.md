# Agent Network Monitor — template

Real-time 3D dashboard for your agent fleet. A Python WebSocket server scans log files, launchd status, and running processes every 5 seconds and pushes live state to a Three.js visualization.

![states] running (green) · completed (blue) · error (red) · idle (gray)

## Files

- `monitor.py` — monitoring server (WebSocket on 8765 + HTTP dashboard on 8766)
- `team_visualization.html` — 3D dashboard served by the monitor

## Setup

1. Copy this folder next to your agent project folders (e.g. `~/Workspace/agent-monitor/`)
2. `pip install websockets`
3. Edit the `AGENTS` dict in `monitor.py` — one entry per agent (dir, logs, launchd label, schedule, process grep, output dir)
4. Edit the `agents` array in `team_visualization.html` — same ids in `monitorId`, plus display info (name, role, description, color)
5. Optionally set env vars:
   - `AGENT_WORKSPACE` — root folder containing agent projects (default: parent of this folder)
   - `LAUNCHD_PREFIX` — your launchd label prefix (default: `com.myagents.`)

## Run

```bash
python3 monitor.py              # dashboard at http://localhost:8766
python3 monitor.py --port 9000  # custom WS port (HTTP on port+1)
```

## How state is detected

- **running** — launchd PID active, process matches `process_grep`, or a log line within the last 2 minutes
- **error** — recent lines (last 7 days) in any `error_logs` file
- **completed** — successful run within the last 24h, no errors
- **idle** — none of the above

The monitor also hashes each agent's `CLAUDE.md` to flag config changes live.

## Notes

- macOS-oriented (launchd). On Linux, set `launchd_label: None` and rely on `process_grep` + logs.
- Pure read-only: the monitor never touches your agents.

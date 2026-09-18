#!/bin/bash
# What does an empty chat cost? Sends "ok" headless and sums every input-side token.
# That number is paid at the start of EVERY session: CLAUDE.md + MEMORY.md + agent/skill
# descriptions + MCP tool schemas + the fixed system prompt. Run before and after a diet.
set -euo pipefail
claude -p "ok" --output-format json | python3 -c '
import json,sys
u=json.load(sys.stdin).get("usage",{})
i,cw,cr=u.get("input_tokens",0),u.get("cache_creation_input_tokens",0),u.get("cache_read_input_tokens",0)
print(f"baseline = {i+cw+cr:,} tokens  (input {i:,} + cache_write {cw:,} + cache_read {cr:,})")'

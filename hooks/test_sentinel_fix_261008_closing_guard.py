"""Sentinel 261008 regression tests for closing-guard.py.

I-46221b  a fenced code example (or a quoted passage) containing "Say go and I will fix it." made the
          Stop hook block a reply that already had the "✅ Done" closing. The real closing blockquote
          ("> **✅ Done**" / "> **👉 Now**") must stay judged: that is where a generic "say go" lands.

pytest style, stdlib only, no network. Transcripts are written under tmp_path.
Run:  python3 -m pytest hooks/test_sentinel_fix_261008_closing_guard.py -q
"""
import importlib.util
import json
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().with_name("closing-guard.py")


def load():
    spec = importlib.util.spec_from_file_location("closing_guard_under_test", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cg = load()

CLOSING = "---\n\n> **✅ Done**\n> - fixed the thing\n>\n> **👉 Now**\n> - nothing, you're set"


def write_transcript(path, final_text, tool=True):
    rows = [{"type": "user", "message": {"role": "user", "content": "please fix it"}}]
    if tool:
        rows += [
            {"type": "assistant", "message": {"role": "assistant",
                                              "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}]}},
            {"type": "user", "message": {"role": "user",
                                         "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}},
        ]
    rows.append({"type": "assistant", "message": {"role": "assistant",
                                                  "content": [{"type": "text", "text": final_text}]}})
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    return path


@pytest.fixture(autouse=True)
def not_headless(monkeypatch):
    # inside an SDK / headless session the hook (correctly) passes everything: make sure we test the real path
    monkeypatch.delenv("CLAUDE_CODE_ENTRYPOINT", raising=False)


def verdict(tmp_path, final_text):
    return cg.decide({"transcript_path": str(write_transcript(tmp_path / "t.jsonl", final_text))})


# --------------------------------------------------------------------------- I-46221b: must NOT block

def test_fenced_example_with_done_marker_is_not_an_ask(tmp_path):
    text = "Added the hook. The phrase it catches:\n\n```\nSay go and I will fix it.\n```\n\n" + CLOSING
    assert verdict(tmp_path, text) == {}


def test_fenced_example_with_language_tag_is_not_an_ask():
    assert not cg.unjustified_go_ask("```text\nWant me to proceed?\n```\n> **✅ Done**")


def test_tilde_fence_is_not_an_ask():
    assert not cg.unjustified_go_ask("~~~\nSay go and I will fix it.\n~~~\n> **✅ Done**")


def test_long_fence_is_not_closed_by_a_shorter_inner_fence():
    text = "````md\n```\nSay go and I will fix it.\n```\n````\n> **✅ Done**"
    assert not cg.unjustified_go_ask(text)


def test_unclosed_fence_runs_to_the_end_like_a_markdown_renderer():
    assert not cg.unjustified_go_ask("```\nSay go and I will fix it.\n> **✅ Done**")


def test_quoted_passage_outside_the_closing_is_not_an_ask(tmp_path):
    text = "The file says:\n\n> Say go and I will fix it.\n\nFixed anyway.\n\n" + CLOSING
    assert not cg.unjustified_go_ask(text)
    assert verdict(tmp_path, text) == {}


def test_fenced_example_inside_the_closing_blockquote_is_not_an_ask(tmp_path):
    text = ("---\n\n> **✅ Done**\n> - documented the phrase:\n> ```\n> Say go and I will fix it.\n> ```\n>\n"
            "> **👉 Now**\n> - nothing, you're set")
    assert not cg.unjustified_go_ask(text)
    assert verdict(tmp_path, text) == {}


def test_indented_fence_inside_a_list_item_is_not_an_ask():
    text = "- step one:\n  ```\n  Say go and I will fix it.\n  ```\n> **✅ Done**"
    assert not cg.unjustified_go_ask(text)


def test_tilde_fence_is_not_closed_by_a_backtick_fence():
    text = "~~~\n```\nSay go and I will fix it.\n```\n~~~\n> **✅ Done**"
    assert not cg.unjustified_go_ask(text)


def test_fence_up_to_three_spaces_indented_is_still_a_fence():
    assert not cg.unjustified_go_ask("   ```\n   Say go and I will fix it.\n   ```\n> **✅ Done**")


def test_four_space_indented_fence_line_inside_a_fence_is_content_not_a_close():
    # markdown: a closing fence has at most 3 spaces of indent; with 4 it is just a line of the code block
    text = "```\n    ```\nSay go and I will fix it.\n```\n> **✅ Done**"
    assert not cg.unjustified_go_ask(text)


def test_a_fence_between_two_quotes_keeps_them_two_quotes():
    # Codex follow-up: dropping the fence used to glue the quoted example to the real closing quote
    text = "> Say go and I will fix it.\n```text\nexample\n```\n> **✅ Done**"
    assert not cg.unjustified_go_ask(text)


def test_the_two_quotes_stay_separate_through_the_hook(tmp_path):
    text = ("The old reply said:\n> Say go and I will fix it.\n```text\nexample\n```\n"
            "> **✅ Done**\n> - fixed the thing\n>\n> **👉 Now**\n> - nothing, you're set")
    assert verdict(tmp_path, text) == {}


# --------------------------------------------------------------------------- must STILL block

def test_ask_inside_the_closing_blockquote_still_blocks(tmp_path):
    text = "Done with the code.\n\n---\n\n> **✅ Done**\n> - fixed the thing\n>\n> **👉 Now**\n> - Say go and I will fix it."
    out = verdict(tmp_path, text)
    assert out.get("decision") == "block"
    assert out["reason"] == cg.GO_REASON


def test_plain_ask_after_a_closed_fence_still_blocks(tmp_path):
    text = "```\nprint('x')\n```\nSay go and I will fix it.\n\n" + CLOSING
    assert verdict(tmp_path, text).get("decision") == "block"


def test_plain_ask_without_fence_still_blocks(tmp_path):
    assert verdict(tmp_path, "✅ Done. Want me to proceed?").get("decision") == "block"


def test_inline_code_ask_still_blocks():
    assert cg.unjustified_go_ask("Reply `go` when ready.\n> **✅ Done**")


def test_ask_in_a_done_only_blockquote_still_blocks():
    assert cg.unjustified_go_ask("Fixed.\n\n> **✅ Done**\n> - Say go and I will fix it.")


def test_ask_in_a_now_only_blockquote_still_blocks():
    assert cg.unjustified_go_ask("Fixed.\n\n> **✅ Done**\n> - fixed\n\n> **👉 Now**\n> - Say go and I will fix it.")
    assert cg.unjustified_go_ask("> **👉 Now**\n> - Say go and I will fix it.")


def test_ask_after_a_fence_inside_the_closing_blockquote_is_still_judged():
    text = "> **✅ Done**\n> ```\n> code\n> ```\n> - Say go and I will fix it."
    assert cg.unjustified_go_ask(text)


def test_four_space_indented_fence_is_code_and_swallows_nothing():
    # Codex follow-up: >=4 spaces = indented code in markdown, its ``` is not a fence; the ask below it is real
    assert cg.unjustified_go_ask("✅ Done\n\n    ```\nSay go and I will fix it.")


def test_tab_indented_fence_is_code_and_swallows_nothing():
    assert cg.unjustified_go_ask("✅ Done\n\n\t```\nSay go and I will fix it.")


def test_fence_opened_in_a_quote_ends_when_the_quote_ends(tmp_path):
    # Codex follow-up: the unclosed quoted fence used to swallow the plain text after the quote
    text = "> ```\n> example\n\n✅ Done\nSay go and I will fix it."
    assert cg.unjustified_go_ask(text)
    assert verdict(tmp_path, text).get("decision") == "block"


def test_quoted_fence_ended_by_the_quote_does_not_hide_a_later_ask():
    assert cg.unjustified_go_ask("> **✅ Done**\n> ```\n> code\n\nSay go and I will fix it.")


def test_unclosed_fence_in_the_closing_quote_still_hides_the_rest_of_that_quote():
    assert not cg.unjustified_go_ask("> **✅ Done**\n> ```\n> Say go and I will fix it.\n> - more")


def test_missing_marker_still_blocks(tmp_path):
    out = verdict(tmp_path, "All fine, nothing else to say.")
    assert out.get("decision") == "block"
    assert out["reason"] == cg.REASON


def test_real_gate_in_closing_still_passes(tmp_path):
    text = "---\n\n> **✅ Done**\n> - code ready\n>\n> **👉 Now**\n> - Say go and I will deploy to production."
    assert verdict(tmp_path, text) == {}


def test_shipped_selftest_still_passes():
    assert cg.selftest() == 0

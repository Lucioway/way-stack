"""Sentinel 261008 regression tests for vault_index.py.

I-5d3403  file symlinks vanished from the index (now listed as "symlink, not indexed")
I-02d1ab  month() crashed the whole run when the file vanished / had an absurd mtime
I-431637  overlapping runs shared one fixed temp file (FileNotFoundError on the second rename);
          follow-up: the one-time index.md.bak was also check-then-copy, so a second run could overwrite it
I-bebfcc  an unreadable subfolder was dropped silently and the parent indexes were rewritten without it

pytest style, stdlib only, no network. Everything lives under tmp_path.
Run:  python3 -m pytest skills/vault-index/scripts/test_sentinel_fix_261008_vault_index.py -q
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().with_name("vault_index.py")
# chmod 000 needs POSIX and a non-root user (root ignores it); os.geteuid does not exist on native Windows
CAN_CHMOD_000 = hasattr(os, "geteuid") and os.geteuid() != 0


def load():
    spec = importlib.util.spec_from_file_location("vault_index_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60)


def make_vault(root):
    root.mkdir(parents=True)
    (root / "a").mkdir()
    (root / "a" / "one.md").write_text("# One\n")
    (root / "top.md").write_text("# Top\n")
    return root


def apply_tree(vi, vault, dry=False):
    stats = {"changes": 0, "written": 0}
    vi.apply(vi.scan(str(vault), frozenset(), set()), str(vault), dry, stats)
    return stats


# --------------------------------------------------------------------------- I-5d3403

def test_file_symlink_is_listed_not_silently_dropped(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink("top.md", vault / "alias.md")
    r = run_cli("--vault", str(vault))
    assert r.returncode == 0, r.stderr
    idx = (vault / "index.md").read_text()
    assert "- File alias.md (symlink, not indexed)" in idx
    assert "[[top]]" in idx          # the real note stays indexed
    assert "[[alias]]" not in idx    # the alias is listed, never indexed as a note


def test_broken_file_symlink_is_listed(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink("does-not-exist.md", vault / "dead.md")
    r = run_cli("--vault", str(vault))
    assert r.returncode == 0, r.stderr
    assert "- File dead.md (symlink, not indexed)" in (vault / "index.md").read_text()


def test_file_symlink_listing_is_idempotent(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink("top.md", vault / "alias.md")
    assert run_cli("--vault", str(vault)).returncode == 0
    again = run_cli("--vault", str(vault))
    assert again.returncode == 0, again.stderr
    assert "changes=0" in again.stdout


def test_file_symlink_is_not_counted_as_a_note(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink("top.md", vault / "alias.md")
    r = run_cli("--vault", str(vault))
    assert "notes_total=2" in r.stdout    # top.md + a/one.md; the alias is not counted as a note


def test_vault_with_only_a_file_symlink_still_gets_an_index(tmp_path):
    # Codex follow-up: the "no notes = no index" gate used to hide an alias in a folder that has no real note
    vault = tmp_path / "v"
    vault.mkdir()
    os.symlink("missing.md", vault / "alias.md")
    r = run_cli("--vault", str(vault))
    assert r.returncode == 0, r.stderr
    assert "notes_total=0" in r.stdout                  # the alias is still not a note
    assert (vault / "index.md").exists(), r.stdout
    assert "- File alias.md (symlink, not indexed)" in (vault / "index.md").read_text()


def test_symlink_only_subfolder_is_indexed_and_shown_by_its_parent(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "docs").mkdir()
    os.symlink("../top.md", vault / "docs" / "alias.md")     # docs/ holds no real note, only an alias
    r = run_cli("--vault", str(vault))
    assert r.returncode == 0, r.stderr
    assert "notes_total=2" in r.stdout
    assert "- File alias.md (symlink, not indexed)" in (vault / "docs" / "index.md").read_text()
    assert "[[docs/index|docs/]]" in (vault / "index.md").read_text()
    assert "changes=0" in run_cli("--vault", str(vault)).stdout      # and a second run changes nothing


def test_symlink_only_folder_block_is_emptied_when_the_alias_goes_away(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "docs").mkdir()
    os.symlink("../top.md", vault / "docs" / "alias.md")
    assert run_cli("--vault", str(vault)).returncode == 0
    os.unlink(vault / "docs" / "alias.md")
    assert run_cli("--vault", str(vault)).returncode == 0
    assert "alias.md" not in (vault / "docs" / "index.md").read_text()
    assert "[[docs/index|docs/]]" not in (vault / "index.md").read_text()


def test_symlink_only_folder_with_a_hand_written_index_gets_the_block_appended(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "docs").mkdir()
    os.symlink("../top.md", vault / "docs" / "alias.md")
    (vault / "docs" / "index.md").write_text("# My own page\n\nhand-written text\n")       # no markers yet
    assert run_cli("--vault", str(vault)).returncode == 0
    idx = (vault / "docs" / "index.md").read_text()
    assert "hand-written text" in idx                                   # the manual text stays
    assert "- File alias.md (symlink, not indexed)" in idx              # and the alias gets its block


def test_nested_symlink_only_folders_are_indexed_all_the_way_up(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "docs" / "deep").mkdir(parents=True)
    os.symlink("../../top.md", vault / "docs" / "deep" / "alias.md")    # docs/ holds only deep/, deep/ only an alias
    r = run_cli("--vault", str(vault))
    assert r.returncode == 0, r.stderr
    assert "- File alias.md (symlink, not indexed)" in (vault / "docs" / "deep" / "index.md").read_text()
    assert "[[deep/index|deep/]]" in (vault / "docs" / "index.md").read_text()
    assert "[[docs/index|docs/]]" in (vault / "index.md").read_text()


def test_folder_with_only_a_non_markdown_symlink_still_gets_no_index(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "misc").mkdir()
    os.symlink("../top.md", vault / "misc" / "pic.png")
    assert run_cli("--vault", str(vault)).returncode == 0
    assert not (vault / "misc" / "index.md").exists()
    assert "misc" not in (vault / "index.md").read_text()


def test_folder_with_only_a_folder_symlink_still_gets_no_index(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    vault = make_vault(tmp_path / "v")
    (vault / "misc").mkdir()
    os.symlink(outside, vault / "misc" / "linkdir")           # unchanged behaviour: only .md aliases widen the gate
    assert run_cli("--vault", str(vault)).returncode == 0
    assert not (vault / "misc" / "index.md").exists()


def test_non_markdown_file_symlink_stays_invisible(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink("top.md", vault / "pic.png")    # a regular pic.png is not listed either
    assert run_cli("--vault", str(vault)).returncode == 0
    assert "pic.png" not in (vault / "index.md").read_text()


def test_folder_symlink_label_unchanged(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.md").write_text("# X\n")
    vault = make_vault(tmp_path / "v")
    os.symlink(outside, vault / "linkdir")
    assert run_cli("--vault", str(vault)).returncode == 0
    idx = (vault / "index.md").read_text()
    assert "- Folder linkdir/ (symlink, not indexed)" in idx
    assert "File linkdir" not in idx


# --------------------------------------------------------------------------- I-02d1ab

def test_month_of_vanished_file_is_unknown(tmp_path):
    vi = load()
    assert vi.month(str(tmp_path / "gone.md"), "gone.md") == "unknown"


def test_month_from_dated_name_needs_no_file(tmp_path):
    vi = load()
    assert vi.month(str(tmp_path / "gone.md"), "2026-03-05-x.md") == "2026-03"


def test_month_uses_mtime_when_file_exists(tmp_path):
    import datetime
    vi = load()
    p = tmp_path / "n.md"
    p.write_text("x")
    ts = datetime.datetime(2025, 2, 10, 12, 0).timestamp()
    os.utime(p, (ts, ts))
    assert vi.month(str(p), "n.md") == "2025-02"


def test_month_survives_absurd_mtime(tmp_path, monkeypatch):
    vi = load()
    p = tmp_path / "n.md"
    p.write_text("x")
    with monkeypatch.context() as m:
        m.setattr(vi.os.path, "getmtime", lambda _p: 1e20)
        assert vi.month(str(p), "n.md") == "unknown"


def test_big_folder_block_survives_a_note_that_vanished(tmp_path):
    vi = load()
    folder = tmp_path / "big"
    folder.mkdir()
    names = [f"n{i:03d}.md" for i in range(vi.BIG + 1)]
    for nm in names[:-1]:
        (folder / nm).write_text("x")          # the last one never exists = deleted after scan()
    n = vi.Node(str(folder))
    n.notes, n.total = names, len(names)
    out = vi.block(n)
    assert "- unknown: 1 notes" in out


# --------------------------------------------------------------------------- I-431637

def test_overlapping_runs_do_not_clobber_each_others_temp(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    real_replace = os.replace
    fired = []

    def second_run_lands_first(src, dst):
        if not fired:
            fired.append(src)
            # another process runs the same write to completion while this one sits between write and rename
            apply_tree(vi, vault)
        return real_replace(src, dst)

    monkeypatch.setattr(vi.os, "replace", second_run_lands_first)
    stats = apply_tree(vi, vault)            # must not raise FileNotFoundError
    assert fired
    assert stats["written"] >= 1
    assert "[[one]]" in (vault / "a" / "index.md").read_text()
    assert list(vault.rglob("*.tmp")) == []


OLD_INDEX = "# a\n\nhand text\n\n<!-- auto-index:start -->\nold\n<!-- auto-index:end -->\n"


def test_failed_rename_leaves_no_temp_and_keeps_the_old_index(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    (vault / "a" / "index.md").write_text(OLD_INDEX)

    def boom(src, dst):
        raise OSError("rename refused")

    monkeypatch.setattr(vi.os, "replace", boom)
    with pytest.raises(OSError):
        apply_tree(vi, vault)
    assert (vault / "a" / "index.md").read_text() == OLD_INDEX
    assert list(vault.rglob("*.tmp")) == []


def test_failed_write_leaves_no_temp_and_keeps_the_old_index(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    (vault / "a" / "index.md").write_text(OLD_INDEX)
    real_open = open

    class FullDisk:                            # the temp file really exists, but nothing can be written to it
        def __init__(self, f):
            self.f = f

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.f.close()
            return False

        def write(self, _text):
            raise OSError(28, "No space left on device")

    def open_with_full_disk(path, mode="r", *a, **k):
        f = real_open(path, mode, *a, **k)
        return FullDisk(f) if str(path).endswith(".tmp") else f

    monkeypatch.setattr(vi, "open", open_with_full_disk, raising=False)    # module-level name wins over the builtin
    with pytest.raises(OSError):
        apply_tree(vi, vault)
    assert (vault / "a" / "index.md").read_text() == OLD_INDEX
    assert list(vault.rglob("*.tmp")) == []


def test_interrupt_while_replacing_leaves_no_temp_and_keeps_the_old_index(tmp_path, monkeypatch):
    # Ctrl-C is a KeyboardInterrupt (BaseException, not OSError) landing between the write and the rename
    vi = load()
    vault = make_vault(tmp_path / "v")
    (vault / "a" / "index.md").write_text(OLD_INDEX)

    def ctrl_c(src, dst):
        raise KeyboardInterrupt

    monkeypatch.setattr(vi.os, "replace", ctrl_c)
    with pytest.raises(KeyboardInterrupt):
        apply_tree(vi, vault)
    assert (vault / "a" / "index.md").read_text() == OLD_INDEX
    assert list(vault.rglob("*.tmp")) == []


def test_temp_is_created_exclusively_and_a_foreign_file_is_never_touched(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    ip = vault / "a" / "index.md"
    ip.write_text(OLD_INDEX)
    foreign = Path(f"{ip}.{os.getpid()}.00000000.tmp")          # same name this run is about to pick
    foreign.write_text("SOMEONE ELSE'S TEMP")
    with monkeypatch.context() as m:
        m.setattr(vi.os, "urandom", lambda n: b"\x00" * n)
        with pytest.raises(FileExistsError):
            apply_tree(vi, vault)
    assert foreign.read_text() == "SOMEONE ELSE'S TEMP"          # neither overwritten nor "cleaned up"
    assert ip.read_text() == OLD_INDEX


def test_temp_lives_next_to_the_index_so_rename_stays_atomic(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    seen = []
    real_replace = os.replace

    def spy(src, dst):
        seen.append((str(src), str(dst)))
        return real_replace(src, dst)

    monkeypatch.setattr(vi.os, "replace", spy)
    apply_tree(vi, vault)
    assert seen
    for src, dst in seen:
        assert os.path.dirname(src) == os.path.dirname(dst)
        assert os.path.basename(dst) == "index.md"


def test_new_index_keeps_normal_file_permissions(tmp_path):
    vi = load()
    vault = make_vault(tmp_path / "v")
    umask = os.umask(0)
    os.umask(umask)
    apply_tree(vi, vault)
    mode = os.stat(vault / "index.md").st_mode & 0o777
    assert mode == 0o666 & ~umask            # same as open(..., "w"): not the private 0600 of mkstemp


def test_first_rewrite_saves_the_original_in_a_bak_and_never_refreshes_it(tmp_path):
    vi = load()
    vault = make_vault(tmp_path / "v")
    ip = vault / "a" / "index.md"
    ip.write_text("# a\n\nhand text\n")
    ts = 1_700_000_000
    os.utime(ip, (ts, ts))
    bak = Path(str(ip) + ".bak")
    apply_tree(vi, vault)
    assert bak.read_text() == "# a\n\nhand text\n"
    assert int(os.stat(bak).st_mtime) == ts              # still a copy2-style backup (mtime kept)
    (vault / "a" / "two.md").write_text("# Two\n")
    apply_tree(vi, vault)                                # second rewrite: the backup must stay the ORIGINAL
    assert bak.read_text() == "# a\n\nhand text\n"


def test_backup_is_not_overwritten_when_an_overlapping_run_made_it_first(tmp_path, monkeypatch):
    # Codex follow-up: run B checked "no .bak yet", run A then saved the pristine original, B copied over it
    vi = load()
    vault = make_vault(tmp_path / "v")
    ip = vault / "a" / "index.md"
    ip.write_text("# a\n\nhand text\n")
    bak = Path(str(ip) + ".bak")
    bak.write_text("PRISTINE ORIGINAL")                  # what run A saved a moment ago
    real_exists = os.path.exists
    monkeypatch.setattr(vi.os.path, "exists", lambda p: False if str(p).endswith(".bak") else real_exists(p))
    apply_tree(vi, vault)                                # run B, working from its stale "no .bak" view
    assert bak.read_text() == "PRISTINE ORIGINAL"
    assert "auto-index:start" in ip.read_text()          # B still did its own rewrite


def test_failed_backup_copy_leaves_no_half_backup_and_the_old_index(tmp_path, monkeypatch):
    # a half-written .bak would pass for "done" on every later run and hide the original for good
    vi = load()
    vault = make_vault(tmp_path / "v")
    ip = vault / "a" / "index.md"
    ip.write_text("# a\n\nhand text\n")

    def disk_full(src, dst, *a, **k):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(vi.shutil, "copy2", disk_full)
    with pytest.raises(OSError):
        apply_tree(vi, vault)
    assert not Path(str(ip) + ".bak").exists()
    assert ip.read_text() == "# a\n\nhand text\n"


# --------------------------------------------------------------------------- I-bebfcc

def test_scan_propagates_a_permission_error(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    (vault / "b").mkdir()
    (vault / "b" / "two.md").write_text("# Two\n")
    real_scandir = os.scandir

    def deny_b(path):
        if os.path.basename(str(path)) == "b":
            raise PermissionError(13, "Permission denied", str(path))
        return real_scandir(path)

    monkeypatch.setattr(vi.os, "scandir", deny_b)
    with pytest.raises(PermissionError):
        vi.scan(str(vault), frozenset(), set())


def test_folder_vanishing_between_listing_and_scan_is_skipped(tmp_path, monkeypatch):
    vi = load()
    vault = make_vault(tmp_path / "v")
    (vault / "gone").mkdir()
    (vault / "gone" / "x.md").write_text("x")
    real_scandir = os.scandir

    def vanished(path):
        if os.path.basename(str(path)) == "gone":
            raise FileNotFoundError(2, "No such file or directory", str(path))
        return real_scandir(path)

    monkeypatch.setattr(vi.os, "scandir", vanished)
    tree = vi.scan(str(vault), frozenset(), set())
    assert [name for name, _ in tree.subs] == ["a"]


@pytest.mark.skipif(not CAN_CHMOD_000, reason="needs POSIX and a non-root user: chmod 000 must really deny")
def test_unreadable_subfolder_aborts_before_any_write(tmp_path):
    vault = make_vault(tmp_path / "v")
    (vault / "b").mkdir()
    (vault / "b" / "two.md").write_text("# Two\n")
    first = run_cli("--vault", str(vault))
    assert first.returncode == 0, first.stderr
    root_index = vault / "index.md"
    assert "[[b/index|b/]]" in root_index.read_text()
    snapshot = {p: p.read_bytes() for p in vault.rglob("*") if p.is_file()}
    (vault / "a" / "three.md").write_text("# Three\n")     # a change that WOULD rewrite a/index.md
    os.chmod(vault / "b", 0o000)
    try:
        r = run_cli("--vault", str(vault))
    finally:
        os.chmod(vault / "b", 0o755)
    assert r.returncode == 2, r.stdout                                 # argparse-style stop, not a crash
    assert "Traceback" not in r.stderr
    assert str(vault / "b") in r.stderr
    assert root_index.read_bytes() == snapshot[root_index]            # not rewritten without its b/ line
    assert "[[b/index|b/]]" in root_index.read_text()
    after = {p: p.read_bytes() for p in vault.rglob("*") if p.is_file()}
    assert after == {**snapshot, vault / "a" / "three.md": b"# Three\n"}    # nothing written at all


@pytest.mark.skipif(not CAN_CHMOD_000, reason="needs POSIX and a non-root user: chmod 000 must really deny")
def test_unreadable_vault_root_still_exits_cleanly(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.chmod(vault, 0o000)
    try:
        r = run_cli("--vault", str(vault))
    finally:
        os.chmod(vault, 0o755)
    assert r.returncode != 0
    assert "cannot read" in r.stderr
    assert "Traceback" not in r.stderr


def test_symlink_cycle_when_followed_is_still_skipped(tmp_path):
    vault = make_vault(tmp_path / "v")
    os.symlink(vault, vault / "a" / "loop")                 # a/loop -> vault (cycle)
    r = run_cli("--vault", str(vault), "--follow-symlink", "loop")
    assert r.returncode == 0, r.stderr
    assert "notes_total=2" in r.stdout

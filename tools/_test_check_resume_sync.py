#!/usr/bin/env python3
"""Offline test for check_resume_sync: it must go RED on the drifts we actually had.

A gate nobody has seen fail is not a gate. Each case below is a real incident:
citation numbers disagreeing across surfaces (27 Jul, 28 Aug) and a PDF printed
from an older source (2 Aug, 28 Aug).

    python tools/_test_check_resume_sync.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = "tools/check_resume_sync.py"
FILES = ("index.html", "resume.json", "resume.html", "resume.pdf",
         "resume.pdf.sources", GATE)
FAILS = []


def sandbox():
    """A throwaway copy of the repo — the test never writes into the real tree."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="resume-sync-"))
    (tmp / "tools").mkdir()
    for f in FILES:
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, tmp / f)
    return tmp


def run(tmp):
    p = subprocess.run([sys.executable, GATE], cwd=tmp,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def case(name, mutate, want_red):
    tmp = sandbox()
    try:
        mutate(tmp)
        code, out = run(tmp)
        red = code != 0
        if red != want_red:
            FAILS.append(f"{name}: expected {'RED' if want_red else 'GREEN'}, "
                         f"got exit {code}\n{out}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def edit(tmp, name, old, new):
    p = tmp / name
    t = p.read_text(encoding="utf-8")
    assert old in t, f"fixture text not found in {name}: {old!r}"
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


# 1. Untouched copy of the real tree must pass, or every other case is meaningless.
case("clean tree is green", lambda tmp: None, want_red=False)

# 2. The 27 Jul / 28 Aug incident: one surface keeps the old number.
case("citation number drifts on one surface",
     lambda tmp: edit(tmp, "index.html", "136 citations", "137 citations"),
     want_red=True)

# 3. The same, but in the ATS copy nobody re-reads.
case("citation number drifts in resume.json",
     lambda tmp: edit(tmp, "resume.json", "136 citations", "134 citations"),
     want_red=True)

# 4. The 2 Aug / 28 Aug incident: the print source moved, the PDF did not.
case("pdf left behind by its source",
     lambda tmp: edit(tmp, "resume.html", "Summary", "Summary "),
     want_red=True)

# 5. No stamp file at all — the PDF's provenance is unknown, which is not "fine".
case("missing stamp file",
     lambda tmp: (tmp / "resume.pdf.sources").unlink(),
     want_red=True)

# 6. The claim disappearing entirely must not read as "surfaces agree".
case("claim deleted from a surface",
     lambda tmp: edit(tmp, "resume.html",
                      "(136 citations, h-index 7, verified 2026-08-28)", ""),
     want_red=True)

if FAILS:
    print("RED:", len(FAILS), "case(s) failed\n")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("GREEN: 6 cases — the gate catches every drift we have actually had")

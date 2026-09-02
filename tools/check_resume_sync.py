#!/usr/bin/env python3
"""Fail the build when the four resume surfaces stop agreeing with each other.

WHY THIS EXISTS. The same facts live in four places: index.html (the one-pager),
resume.json (ATS), resume.html (print source) and resume.pdf (printed from it).
Three of them are hand-edited, the fourth is printed by hand. Every drift found so
far was found weeks later by a human reading the page:

  2026-07-27  site said 139 citations, Google Scholar said 137
  2026-08-02  resume.pdf was printed 27 Jul, resume.json edited 01 Aug
  2026-08-28  site said 137, Scholar said 136; the PDF was ten days behind the JSON

No LLM, no network, no dependencies. The verdict is an exit code, so CI can hold it.

  python tools/check_resume_sync.py            # check
  python tools/check_resume_sync.py --stamp    # after re-printing resume.pdf

WHAT IT CANNOT DO. It does not ask Google Scholar whether the number is still true —
Scholar blocks CI. It only guarantees that one number is written once and that the
PDF was printed from the current source. Freshness of the number itself is the job
of the weekly review, which stamps a "verified <date>" next to it.
"""
import argparse
import datetime
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STAMP = ROOT / "resume.pdf.sources"

# One claim, four homes. Each entry: file -> regex with named groups n / h.
CITATION_CLAIM = {
    "index.html": re.compile(r"(?P<n>\d+) citations, h-index (?P<h>\d+)"),
    "resume.json": re.compile(r"\((?P<n>\d+) citations, h-index (?P<h>\d+)"),
    "resume.html": re.compile(r"\((?P<n>\d+) citations, h-index (?P<h>\d+)"),
}

# Open question, not a defect the machine can settle: the print surface says one
# location and the web surface says another. Anton decides which is canon. Until
# the date below it is a warning; after it, this gate goes red on purpose, so the
# question cannot quietly outlive another month.
LOCATION_DEADLINE = datetime.date(2026, 9, 30)
# Each pattern must keep matching its file. On 2026-09-01 the "Location:" label
# was dropped from resume.html and this regex quietly stopped matching, so the
# gate compared one surface against nothing and printed "surfaces agree". A
# pattern that finds nothing is now a finding, not a pass.
LOCATION_PATTERNS = {
    "resume.html": re.compile(r"Based between ([^,(]+)"),
    "index.html": re.compile(r"Based in ([^,(]+)"),
}


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def sha(name):
    """Hash the source with line endings normalised to LF.

    core.autocrlf=true hands a Windows checkout CRLF while git stores and Linux
    checks out LF, so hashing the raw bytes makes the stamp valid on exactly one
    operating system. Stamping on Windows then left the Linux CI red forever,
    and stamping on Linux would do the same to Anton's machine (2026-09-01).
    Normalising first makes one stamp true everywhere.
    """
    raw = (ROOT / name).read_bytes()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def check_citations(problems):
    seen = {}
    for name, pat in CITATION_CLAIM.items():
        m = pat.search(read(name))
        if not m:
            problems.append(f"{name}: no 'N citations, h-index M' claim found at all")
            continue
        seen[name] = (m.group("n"), m.group("h"))
    if len(set(seen.values())) > 1:
        detail = ", ".join(f"{f} says {n}/{h}" for f, (n, h) in seen.items())
        problems.append("citation claim differs between surfaces: " + detail)
    return seen


def parse_stamp(text):
    """`<sha256>  <path>` per line. Tolerant of hand-editing, because a watchdog that
    crashes on a malformed input file reports nothing at all — which reads exactly like
    'everything is fine'."""
    out, bad = {}, []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            bad.append(line)
            continue
        out[parts[1].strip()] = parts[0].strip()
    return out, bad


def check_pdf_stamp(problems):
    if not STAMP.exists():
        problems.append("resume.pdf.sources is missing — run --stamp after printing the PDF")
        return
    want, bad = parse_stamp(STAMP.read_text(encoding="utf-8"))
    for line in bad:
        problems.append(f"resume.pdf.sources has a line that is not '<sha256>  <path>': {line!r}"
                        " — do not hand-edit it, reprint the PDF and run --stamp")
    if not want and not bad:
        problems.append("resume.pdf.sources is empty — reprint the PDF and run --stamp")
    for name, recorded in want.items():
        if not (ROOT / name).exists():
            problems.append(f"resume.pdf.sources points at {name}, which does not exist")
            continue
        if sha(name) != recorded:
            problems.append(
                f"resume.pdf was printed from an older {name} — reprint it with Chrome "
                "(Edge writes a zero-byte file without saying so) and run --stamp"
            )


def normalise_place(raw):
    """'Lisbon, Portugal (CET/WET)' and 'Lisbon' are the same claim; 'Lisbon' and
    'Bay Area' are not. Compare the leading place name only, so the gate fires on a
    real contradiction and stays quiet on a longer spelling of the same one."""
    head = raw.split(",")[0].split("(")[0]
    return " ".join(head.split()).strip(" .;:·-").casefold()


def check_location(problems, warnings):
    found = {}
    for name, pat in LOCATION_PATTERNS.items():
        m = pat.search(read(name))
        if m:
            found[name] = (m.group(1).strip(), normalise_place(m.group(1)))
        else:
            problems.append(
                f"cannot read the location out of {name} any more — the wording moved "
                "and LOCATION_PATTERNS did not follow, so this surface is being "
                "compared against nothing"
            )
    if len({norm for _raw, norm in found.values()}) > 1:
        detail = ", ".join(f"{f}: {raw!r}" for f, (raw, _n) in found.items())
        msg = "the resume and the one-pager give different locations — " + detail
        if datetime.date.today() > LOCATION_DEADLINE:
            problems.append(msg + f" (unresolved past {LOCATION_DEADLINE})")
        else:
            warnings.append(msg + f" (owner's call, red after {LOCATION_DEADLINE})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stamp", action="store_true",
                    help="record the hashes of the files resume.pdf was just printed from")
    a = ap.parse_args()

    if a.stamp:
        lines = [f"{sha(n)}  {n}" for n in ("resume.html",)]
        STAMP.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("stamped:\n  " + "\n  ".join(lines))
        return 0

    problems, warnings = [], []
    seen = check_citations(problems)
    check_pdf_stamp(problems)
    check_location(problems, warnings)

    if seen and len(set(seen.values())) == 1:
        n, h = next(iter(seen.values()))
        print(f"citation claim: {n} citations, h-index {h} — identical on "
              f"{len(seen)} surfaces")
    for w in warnings:
        print("WARN  " + w)
    if problems:
        print("\nRESUME-SYNC: " + str(len(problems)) + " problem(s) -> DRIFT")
        for p in problems:
            print("  " + p)
        return 1
    print("RESUME-SYNC: surfaces agree -> OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

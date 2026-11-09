"""Checks for build_landings.py: builds pages, then asserts the contract on the output.
Machine: A-2022BAYAREA (Hub) · Agent: Claude Code · Operator: Anton · 2026-11-09
"""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
import build_landings as bl  # noqa: E402

d = json.loads((ROOT / "solutions" / "landings.json").read_text(encoding="utf-8"))
assert not bl.check(d), bl.check(d)
assert 5 <= len(d["products"]) <= 10, "between 5 and 10 landing pages"

bad = copy.deepcopy(d)
bad["products"][0]["metrics"][0]["source"] = ""
assert bl.check(bad), "metric without source must fail"
bad = copy.deepcopy(d)
bad["calendly"] = "https://calendly.com/paloaltolab"
assert bl.check(bad), "wrong booking link must fail"

assert subprocess.run([sys.executable, str(Path(__file__).parent / "build_landings.py")]).returncode == 0
for p in d["products"]:
    h = (ROOT / "solutions" / p["slug"] / "index.html").read_text(encoding="utf-8")
    assert d["calendly"] in h, p["slug"]
    assert "—" not in h and "–" not in h, f"{p['slug']}: long dash"
    assert not re.search(r"(?<!co)founder", h, re.I), f"{p['slug']}: 'founder' about Anton"
    assert h.count("class=ours") >= 1, f"{p['slug']}: our row not highlighted"
print("ok", len(d["products"]))

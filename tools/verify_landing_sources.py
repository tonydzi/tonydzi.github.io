"""Check that every number on the landing pages is present at its linked source.

Passport
  in:   solutions/landings.json; fetches each metric source (HTML, GitHub blob -> raw, PDF via pypdf)
  out:  one line per metric: OK / MISS <numbers not found> / BLIND <why>; exit 1 if any MISS, 2 if any BLIND
  who:  landings-benchmark-refresh routine before every rebuild; by hand after editing numbers
  limit: matches numbers as text, so "0.883" present anywhere on the page counts; it proves presence, not context
  rail: local + HTTP, 0 LLM
Machine: A-2022BAYAREA (Hub) · Agent: Claude Code · Operator: Anton · 2026-11-10
"""
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers(value):
    out = []
    for n in NUM.findall(value):
        n = n.replace(",", "")
        if n not in ("1", "0") or "/" in value or "of" in value:
            out.append(n)
    return out


def fetch(url):
    if "github.com/" in url and "/blob/" in url:
        url = url.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/", "/")
    req = urllib.request.Request(url, headers={"User-Agent": "landing-verify"})
    data = urllib.request.urlopen(req, timeout=60).read()
    if url.endswith(".pdf"):
        import pypdf
        return " ".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(data)).pages)
    if url.rstrip("/").count("/") == 4 and "github.com/" in url:  # repo root -> README
        owner_repo = url.split("github.com/")[1].split("#")[0].strip("/")
        for br in ("main", "master"):
            try:
                return fetch(f"https://raw.githubusercontent.com/{owner_repo}/{br}/README.md")
            except Exception:
                pass
    return data.decode("utf-8", "replace")


def main():
    d = json.loads((ROOT / "solutions" / "landings.json").read_text(encoding="utf-8"))
    cache, miss, blind, total = {}, 0, 0, 0
    for p in d["products"]:
        for m in p["metrics"]:
            total += 1
            src = m["source"]
            if src not in cache:
                try:
                    cache[src] = fetch(src).replace(",", "")
                except Exception as e:
                    cache[src] = None
                    cache[src + "#err"] = str(e)[:80]
            text = cache[src]
            if text is None:
                blind += 1
                print(f"BLIND {p['slug']} · {m['bench'][:50]} · {cache[src + '#err']}")
                continue
            lost = [n for r in m["rows"] for n in numbers(r[1]) if n not in text]
            if lost:
                miss += 1
                print(f"MISS  {p['slug']} · {m['bench'][:50]} · not at source: {sorted(set(lost))}")
            else:
                print(f"OK    {p['slug']} · {m['bench'][:50]}")
    print(f"СЛЕПАЯ ЗОНА: не смог прочитать {blind} из {total} источников; совпадение = число есть на странице, контекст не проверяется")
    return 1 if miss else (2 if blind else 0)


if __name__ == "__main__":
    sys.exit(main())

"""Build /solutions/ landing pages from solutions/landings.json.

Passport
  in:   solutions/landings.json (single source of truth: products, metrics, dates, sources)
  out:  solutions/index.html and solutions/<slug>/index.html
  who:  run by hand after editing numbers, and by the biweekly refresh routine
  fails loud: a metric without date or source, a page without the booking link
  rail: local, 0 LLM
Machine: A-2022BAYAREA (Hub) · Agent: Claude Code · Operator: Anton · 2026-11-09
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOL = ROOT / "solutions"
E = html.escape

CSS = """
:root{--bg:#fbfaf7;--fg:#1b1b1a;--mut:#5d5b55;--line:#e3e0d8;--card:#ffffff;--acc:#1f5f4a;--acc-fg:#fff;--hi:#e7f2ec}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121312;--fg:#ecebe6;--mut:#a3a19a;--line:#2c2e2b;--card:#1a1c1a;--acc:#6cc7a1;--acc-fg:#0d1a14;--hi:#1d2e26}}
:root[data-theme=dark]{--bg:#121312;--fg:#ecebe6;--mut:#a3a19a;--line:#2c2e2b;--card:#1a1c1a;--acc:#6cc7a1;--acc-fg:#0d1a14;--hi:#1d2e26}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:760px;margin:0 auto;padding:40px 16px 80px}
a{color:var(--acc)}h1{font-size:2.1rem;line-height:1.2;margin:.3em 0 .4em}h2{font-size:1.25rem;margin:2.2em 0 .6em}
.eyebrow{font:600 .8rem/1 ui-monospace,Consolas,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.lead{font-size:1.1rem;color:var(--mut)}
.cta{display:inline-block;background:var(--acc);color:var(--acc-fg);padding:.75em 1.3em;border-radius:8px;font-weight:600;text-decoration:none;margin:.6em .6em .6em 0}
.ghost{display:inline-block;padding:.75em 1.1em;border:1px solid var(--line);border-radius:8px;text-decoration:none}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.bench{font-weight:600}.meta{font-size:.85rem;color:var(--mut)}
table{width:100%;border-collapse:collapse;margin:.5em 0;font-variant-numeric:tabular-nums}
td{padding:.35em .4em;border-top:1px solid var(--line)}td.v{text-align:right;white-space:nowrap}
tr.ours td{background:var(--hi);font-weight:600}
ul{padding-left:1.2em}.win{border-left:4px solid var(--acc)}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.grid a{text-decoration:none;color:inherit}.grid .card{height:100%;margin:0}
footer{margin-top:3em;font-size:.85rem;color:var(--mut)}
"""


def page(title, desc, body):
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{E(title)}</title><meta name=description content=\"{E(desc)}\">"
        f"<style>{CSS}</style></head><body><main>{body}</main></body></html>\n"
    )


def check(d):
    errs = []
    if not d.get("calendly", "").startswith("https://calendly.com/paloaltolab/1-on-1"):
        errs.append("booking link must be calendly.com/paloaltolab/1-on-1")
    for p in d["products"]:
        for m in p["metrics"]:
            if not m.get("date") or not m.get("source", "").startswith("https://"):
                errs.append(f"{p['slug']}: metric '{m.get('bench')}' lacks date or source")
    return errs


def author_block(d):
    a = d["author"]
    return (
        "<h2>Who built it, and why you can check</h2><div class=card>"
        f"<p><b>{E(a['name'])}</b>, {E(a['role'])}. {E(a['merged'])} "
        f"(<a href='{E(a['merged_source'])}'>list, as of {E(a['merged_as_of'])}</a>).</p>"
        f"<p class=meta>{E(a['ai'])}</p></div>"
    )


def product_page(d, p, others):
    cal = d["calendly"]
    b = [f"<div class=eyebrow>{E(p['family'])}</div><h1>{E(p['headline'])}</h1>",
         f"<p class=lead>{E(p['pain'])}</p>",
         f"<a class=cta href='{E(cal)}'>Book a 15-minute Google Meet</a>",
         f"<a class=ghost href='{E(p['repo'])}'>Read the code</a>",
         "<h2>Is this for you</h2><ul>" + "".join(f"<li>{E(x)}</li>" for x in p["for_whom"]) + "</ul>",
         f"<div class='card win'><b>The first win we aim for:</b> {E(p['first_win'])}</div>",
         "<h2>The numbers</h2>"]
    for m in p["metrics"]:
        rows = "".join(
            f"<tr class={'ours' if len(r) > 2 and r[2] else ''}><td>{E(r[0])}</td><td class=v>{E(r[1])}</td></tr>"
            for r in m["rows"])
        b.append(f"<div class=card><div class=bench>{E(m['bench'])}</div>"
                 f"<div class=meta>{E(m['metric'])} · measured {E(m['date'])} · <a href='{E(m['source'])}'>source</a></div>"
                 f"<table>{rows}</table></div>")
    b.append("<h2>What we do not claim</h2><ul>" + "".join(f"<li>{E(x)}</li>" for x in p["limits"]) + "</ul>")
    b.append("<h2>How we start</h2><ol><li>A 15-minute call: your setup, your data, what a first win means for you.</li>"
             "<li>We agree on a test for your setup and show the numbers, including where we lose.</li>"
             "<li>You decide with the numbers in hand: adopt the open-source tool yourself, or work with us.</li></ol>"
             f"<a class=cta href='{E(cal)}'>Book a 15-minute Google Meet</a>")
    links = [(f"Source code: {p['repo'].split('github.com/')[-1]}", p["repo"])] + [tuple(x) for x in p["extra_links"]]
    b.append("<h2>Go deeper</h2><ul>" + "".join(f"<li><a href='{E(u)}'>{E(t)}</a></li>" for t, u in links) + "</ul>")
    b.append(author_block(d))
    b.append("<h2>Other things we build</h2><ul>" + "".join(
        f"<li><a href='../{E(o['slug'])}/'>{E(o['name'])}</a>: {E(o['headline'])}</li>" for o in others) + "</ul>")
    b.append(f"<footer>Numbers refreshed {E(d['refreshed'])}, {E(d['cadence'])}. "
             "<a href='../'>All solutions</a> · <a href='../../'>tonydzi.github.io</a></footer>")
    return page(f"{p['name']} · Palo Alto AI Research Lab", p["headline"], "".join(b))


def index_page(d):
    cards = "".join(
        f"<a href='{E(p['slug'])}/'><div class=card><div class=eyebrow>{E(p['family'])}</div>"
        f"<p><b>{E(p['headline'])}</b></p><p class=meta>{E(p['metrics'][0]['bench'])}</p></div></a>"
        for p in d["products"])
    body = ("<div class=eyebrow>Palo Alto AI Research Lab</div><h1>Agent infrastructure, measured in public</h1>"
            "<p class=lead>Small open-source tools we built to run our own AI agent fleet. Each one stands on dated measurements with a public test or source, "
            "including the runs where we lose.</p>"
            f"<a class=cta href='{E(d['calendly'])}'>Book a 15-minute Google Meet</a>"
            f"<h2>Pick your problem</h2><div class=grid>{cards}</div>" + author_block(d) +
            f"<footer>Numbers refreshed {E(d['refreshed'])}, {E(d['cadence'])}. <a href='../'>tonydzi.github.io</a></footer>")
    return page("Solutions · Palo Alto AI Research Lab", "Open-source agent infrastructure tools, each with a public benchmark.", body)


def main():
    d = json.loads((SOL / "landings.json").read_text(encoding="utf-8"))
    errs = check(d)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    for p in d["products"]:
        others = [o for o in d["products"] if o is not p]
        out = SOL / p["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(product_page(d, p, others), encoding="utf-8")
    (SOL / "index.html").write_text(index_page(d), encoding="utf-8")
    print(f"built {len(d['products'])} landing pages + index")
    return 0


if __name__ == "__main__":
    sys.exit(main())

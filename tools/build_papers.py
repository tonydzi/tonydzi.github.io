"""Render /papers/: one Google-Scholar-indexable page per preprint, plus an index.

WHY. Zenodo is the version of record for our preprints, but Google Scholar does not
index Zenodo and Semantic Scholar did not pick the records up either. Scholar does crawl
personal sites if each paper has its own page with Highwire Press meta tags
(citation_title / citation_author / citation_publication_date / citation_pdf_url) and the
PDF sits on the same host. Rules: https://scholar.google.com/intl/en/scholar/inclusion.html

INPUT.  papers/papers.json  -- one entry per paper (slug, doi, title, short, date,
        keywords, abstract_html, code, pages, pdf_bytes, zenodo_id). The abstract and
        metadata are copied from the Zenodo record; the PDF next to the page is the
        Zenodo file byte for byte (same md5), so both copies are the same version.
OUTPUT. papers/<slug>.html for every entry, and papers/index.html. Nothing else.
        sitemap.xml and the footer nav are owned by build_site.py (entries in OWN_PAGES
        and PAGES there).

RUN.    python tools/build_papers.py          # write pages, then check
        python tools/build_papers.py --check  # verify only, exit 1 on any defect

ADD A PAPER. Put its PDF at papers/<slug>.pdf, add one entry to papers.json, add the page
to OWN_PAGES and PAGES in build_site.py, run both generators.

WHAT BREAKS. PDF over 5 MB (Scholar may skip it) or missing -> --check FAILs and names it.
A page whose citation_title differs from the PDF's own title will be ignored by Scholar:
take the title from Zenodo, which was taken from the PDF.
"""
import html, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://tonydzi.github.io"
DATA = os.path.join(ROOT, "papers", "papers.json")
AUTHOR_CIT = "Dziatkovskii, Anton"
AUTHOR = "Anton Dziatkovskii"
ORCID = "0000-0001-7408-3054"
MAX_PDF = 5 * 1024 * 1024
REQUIRED_META = ["citation_title", "citation_author", "citation_publication_date",
                 "citation_pdf_url", "citation_doi"]

CSS = """<style>
  body{background:#fdfdfd;color:#111;
    font-family:"Bitstream Charter","Iowan Old Style",Palatino,Georgia,"Times New Roman",serif;
    font-size:18px;line-height:1.55;max-width:47rem;margin:0 auto;padding:3rem 1rem 6rem;}
  .crumb{font-size:.9rem;color:#666;margin-bottom:2rem}
  h1{font-size:1.6rem;line-height:1.2;margin:0 0 .6rem;font-weight:600}
  a{color:#0000ee;text-decoration:none;border-bottom:1px solid transparent}
  a:hover{border-bottom-color:#0000ee}
  h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.14em;color:#666;font-weight:600;margin:2.2rem 0 .7rem;padding-bottom:.35rem;border-bottom:1px solid #e2ded3}
  p{margin:0 0 1rem;max-width:65ch}
  .by{margin:0 0 .3rem}
  .note{color:#666;font-size:.9rem}
  .lk a{display:inline-block;margin:.2rem .9rem .2rem 0;text-decoration:underline;text-underline-offset:2px;border-bottom:none}
  .item{padding:.6rem 0;border-bottom:1px solid #eee9dd}
  .it-t{font-weight:600}
  pre{background:#f4f2ec;padding:.8rem;overflow-x:auto;font-size:.8rem;white-space:pre-wrap;word-break:break-word}
  .foot{margin-top:3rem;padding-top:1rem;border-top:1px solid #e2ded3;color:#666;font-size:.85rem}
</style>"""


def esc(s):
    return html.escape(s, quote=True)


def plain(abstract_html):
    t = re.sub(r"<[^>]+>", " ", abstract_html)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return re.sub(r"^Abstract\.\s*", "", t)


def long_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def bibtex(p):
    key = "dziatkovskii%s%s" % (p["date"][:4], re.sub(r"[^a-z]", "", p["slug"])[:12])
    return ("@misc{%s,\n  author    = {Dziatkovskii, Anton},\n  title     = {%s},\n"
            "  year      = {%s},\n  publisher = {Zenodo},\n  doi       = {%s},\n"
            "  url       = {https://doi.org/%s},\n  note      = {Preprint, CC BY 4.0}\n}"
            % (key, p["title"], p["date"][:4], p["doi"], p["doi"]))


def page(p):
    url = "%s/papers/%s.html" % (SITE, p["slug"])
    pdf = "%s/papers/%s.pdf" % (SITE, p["slug"])
    desc = plain(p["abstract_html"])
    meta = [("citation_title", p["title"]), ("citation_author", AUTHOR_CIT),
            ("citation_author_orcid", ORCID),
            ("citation_publication_date", p["date"].replace("-", "/")),
            ("citation_online_date", p["date"].replace("-", "/")),
            ("citation_doi", p["doi"]), ("citation_pdf_url", pdf),
            ("citation_abstract_html_url", url), ("citation_language", "en")]
    meta += [("citation_keywords", k) for k in p["keywords"]]
    ld = {"@context": "https://schema.org", "@type": "ScholarlyArticle",
          "headline": p["title"][:110], "name": p["title"], "datePublished": p["date"],
          "author": {"@type": "Person", "name": AUTHOR, "sameAs": "https://orcid.org/" + ORCID},
          "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": p["doi"]},
          "sameAs": ["https://doi.org/" + p["doi"], "https://zenodo.org/records/%s" % p["zenodo_id"]],
          "url": url, "encoding": {"@type": "MediaObject", "contentUrl": pdf, "encodingFormat": "application/pdf"},
          "license": "https://creativecommons.org/licenses/by/4.0/", "keywords": p["keywords"],
          "abstract": desc}
    code = "".join('<a href="%s">Code: %s</a>' % (esc(c), esc(c.rsplit("/", 1)[-1])) for c in p["code"])
    kb = round(p["pdf_bytes"] / 1024)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(meta)s
<link rel="canonical" href="%(url)s">
<link rel="alternate" type="application/pdf" href="%(pdf)s">
<script type="application/ld+json">%(ld)s</script>
%(css)s
</head>
<body>

<div class="crumb"><a href="/">Anton Dziatkovskii</a> &rsaquo; <a href="/papers/">Papers</a></div>
<h1>%(title_h)s</h1>
<p class="by"><b>%(author)s</b> &middot; <a href="https://orcid.org/%(orcid)s">ORCID %(orcid)s</a></p>
<p class="note">Preprint, %(long)s. Version of record: Zenodo, DOI <a href="https://doi.org/%(doi)s">%(doi)s</a>. License CC BY 4.0.</p>
<p class="lk"><a href="%(slug)s.pdf">Full text (PDF, %(pages)d pages, %(kb)d KB)</a><a href="https://doi.org/%(doi)s">DOI</a>%(code)s</p>

<h2>Abstract</h2>
%(abstract)s

<h2>Keywords</h2>
<p class="note">%(kw)s</p>

<h2>How to cite</h2>
<p>Dziatkovskii, A. (%(year)s). %(title_h)s. Preprint. Zenodo. https://doi.org/%(doi)s</p>
<pre>%(bib)s</pre>
<p class="note">One text, one DOI: the PDF on this page is the Zenodo file byte for byte. Please cite the DOI.</p>

<div class="foot">Anton Dziatkovskii &middot; Palo Alto AI Research Lab &middot; <a href="/papers/">All 2026 preprints</a> &middot; <a href="/scholar/publications/">Full publication list</a></div>

</body>
</html>
""" % dict(title=esc(p["title"]), desc=esc(desc[:300]),
           meta="\n".join('<meta name="%s" content="%s">' % (k, esc(v)) for k, v in meta),
           url=url, pdf=pdf, ld=json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"), css=CSS,
           title_h=esc(p["title"]), author=AUTHOR, orcid=ORCID, long=long_date(p["date"]),
           doi=p["doi"], slug=p["slug"], pages=p["pages"], kb=kb, code=code,
           abstract=p["abstract_html"], kw=esc(" · ".join(p["keywords"])), year=p["date"][:4],
           bib=esc(bibtex(p)))


def index(papers):
    items = "\n".join(
        '<div class="item"><div><a class="it-t" href="%s.html">%s</a></div>'
        '<div class="note">%s &middot; %d pages &middot; DOI <a href="https://doi.org/%s">%s</a> &middot; <a href="%s.pdf">PDF</a></div></div>'
        % (p["slug"], esc(p["title"]), long_date(p["date"]), p["pages"], p["doi"], p["doi"], p["slug"])
        for p in sorted(papers, key=lambda x: x["date"], reverse=True))
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preprints 2026 — Anton Dziatkovskii</title>
<meta name="description" content="%(n)d preprints by Anton Dziatkovskii (2026) on LLM agent fleets, agent governance and control, retrieval, and homeostatic system design. Full text PDF and DOI for each.">
<link rel="canonical" href="%(site)s/papers/">
%(css)s
</head>
<body>

<div class="crumb"><a href="/">&larr; Anton Dziatkovskii</a></div>
<h1>Preprints, 2026</h1>
<p class="note">%(n)d papers. Each has its own page with the abstract, the full-text PDF and a citation. The version of record of every paper is its Zenodo DOI (CC BY 4.0); the PDF here is the same file. Older journal and conference work: <a href="/scholar/publications/">full publication list</a>.</p>

%(items)s

<div class="foot">Anton Dziatkovskii &middot; <a href="https://orcid.org/%(orcid)s">ORCID %(orcid)s</a></div>

</body>
</html>
""" % dict(n=len(papers), site=SITE, css=CSS, items=items, orcid=ORCID)


def check(papers):
    bad = []
    for p in papers:
        f = os.path.join(ROOT, "papers", p["slug"] + ".html")
        pdf = os.path.join(ROOT, "papers", p["slug"] + ".pdf")
        if not os.path.exists(pdf):
            bad.append((p["slug"], "PDF missing"))
        elif os.path.getsize(pdf) > MAX_PDF:
            bad.append((p["slug"], "PDF over 5 MB"))
        if not os.path.exists(f):
            bad.append((p["slug"], "page missing")); continue
        s = io.open(f, encoding="utf-8").read()
        for k in REQUIRED_META:
            if s.count('<meta name="%s"' % k) != 1:
                bad.append((p["slug"], "meta %s count != 1" % k))
        if 'content="%s"' % esc(p["title"]) not in s:
            bad.append((p["slug"], "citation_title differs from papers.json"))
    if not os.path.exists(os.path.join(ROOT, "papers", "index.html")):
        bad.append(("index", "papers/index.html missing"))
    for who, why in bad:
        print("  FAIL %s: %s" % (who, why))
    if not bad:
        print("  OK   papers: %d pages, all with Highwire meta and a PDF under 5 MB" % len(papers))
    return not bad


def main():
    papers = json.load(io.open(DATA, encoding="utf-8"))
    if "--check" not in sys.argv:
        for p in papers:
            io.open(os.path.join(ROOT, "papers", p["slug"] + ".html"), "w", encoding="utf-8",
                    newline="\n").write(page(p))
        io.open(os.path.join(ROOT, "papers", "index.html"), "w", encoding="utf-8",
                newline="\n").write(index(papers))
        print("wrote %d paper pages + index" % len(papers))
    sys.exit(0 if check(papers) else 1)


if __name__ == "__main__":
    main()

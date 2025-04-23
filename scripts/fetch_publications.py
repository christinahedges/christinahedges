import requests
import numpy as np
import os
from datetime import datetime

AUTHOR_QUERY = "Hedges, Christina"
ADS_TOKEN = os.environ.get("ADS_API_TOKEN")
START_YEAR = 2007

OUTPUT_MD = "publications.md"
ADS_API_URL = "https://api.adsabs.harvard.edu/v1/search/query"

HEADERS = {"Authorization": f"Bearer {ADS_TOKEN}"}
PARAMS = {
    "q": f'author:"{AUTHOR_QUERY}" pubdate:[{START_YEAR}-01-01 TO *]',
    "fl": "title,bibcode,author,pubdate,citation_count,journal,doi,doctype,publisher",
    "rows": 200,
    "sort": "pubdate desc",
}

EXCLUDE_PUBLISHER = ["zenodo"]
EXCLUDE_DOCTYPES = [
    "abstract",
    "dataset",
    "eprint",
    "erratum",
    "inproceedings",
    "thesis",
    "newsletter",
    "proposal",
    "software",
]


def fetch_pubs():
    response = requests.get(ADS_API_URL, headers=HEADERS, params=PARAMS)
    response.raise_for_status()
    all_pubs = response.json()["response"]["docs"]

    filtered = []
    for pub in all_pubs:
        title = pub.get("title", ["Untitled"])[0].lower()
        doctype = pub.get("doctype", "")
        publisher = pub.get("publisher", "").lower()

        if doctype in EXCLUDE_DOCTYPES:
            continue
        if publisher in EXCLUDE_PUBLISHER:
            continue

        filtered.append(pub)
    return filtered


def bold_me(authors):
    for name in [
        "Hedges, Christina L.",
        "Hedges, Christina",
        "Hedges, Christina Louise",
        "Hedges, C",
        "Hedges, C.",
    ]:
        if (np.asarray(authors, dtype=str) == name).any():
            authors = [a if a != name else f"**{name}**" for a in authors]
    return authors


def format_pub_entry(pub):
    entry = []
    title = pub.get("title", ["Untitled"])[0]
    year = pub.get("pubdate", "")[:4]
    authors_list = bold_me(pub.get("author", []))

    if len(authors_list) > 5:
        authors = ", ".join(authors_list[:5]) + ", et al."
    else:
        authors = ", ".join(authors_list)
    journal = pub.get("journal", "")
    citations = pub.get("citation_count", 0)
    doi = pub.get("doi", [None])[0]
    bibcode = pub.get("bibcode")

    link = f"https://ui.adsabs.harvard.edu/abs/{bibcode}/abstract"
    if doi:
        doi_link = f"https://doi.org/{doi}"
        link += f" ([DOI]({doi_link}))"

    entry.append(f"### {title}")
    entry.append(f"{authors}")
    if journal:
        entry.append(f"*{journal}, {year}*  ")
    else:
        entry.append(f"*{year}*  ")
    entry.append(f"Citations: {citations}  ")
    entry.append(f"[View on ADS]({link})")
    entry.append("")
    return entry


def format_md(pubs):
    total_citations = sum(p.get("citation_count", 0) for p in pubs)
    pub_count = len(pubs)

    first_author_pubs = [
        p for p in pubs if p.get("author", [""])[0].lower().startswith("hedges")
    ]
    first_author_count = len(first_author_pubs)

    notable_pubs = [
        p
        for p in first_author_pubs
        if not any(j in p.get("bibcode", "").lower() for j in ["rnaas", "soft"])
        and int(p.get("pubdate", "0000")[:4]) >= 2012
    ]

    # # Sort with first-author pubs at the top, then others by pubdate
    # pubs_sorted = sorted(
    #     first_author_pubs, key=lambda p: p.get("pubdate", ""), reverse=True
    # ) + sorted(
    #     [p for p in pubs if p not in first_author_pubs],
    #     key=lambda p: p.get("pubdate", ""),
    #     reverse=True,
    # )

    md = [
        """

```
▗▄▄▖ ▗▖ ▗▖▗▄▄▖ ▗▖   ▗▄▄▄▖ ▗▄▄▖ ▗▄▖▗▄▄▄▖▗▄▄▄▖ ▗▄▖ ▗▖  ▗▖ ▗▄▄▖
▐▌ ▐▌▐▌ ▐▌▐▌ ▐▌▐▌     █  ▐▌   ▐▌ ▐▌ █    █  ▐▌ ▐▌▐▛▚▖▐▌▐▌   
▐▛▀▘ ▐▌ ▐▌▐▛▀▚▖▐▌     █  ▐▌   ▐▛▀▜▌ █    █  ▐▌ ▐▌▐▌ ▝▜▌ ▝▀▚▖
▐▌   ▝▚▄▞▘▐▙▄▞▘▐▙▄▄▖▗▄█▄▖▝▚▄▄▖▐▌ ▐▌ █  ▗▄█▄▖▝▚▄▞▘▐▌  ▐▌▗▄▄▞▘
          
============================================================
```
""",
        "",
    ]
    md.append(f"### Total Publications: {pub_count}")
    md.append(f"### First-Author Publications: {first_author_count}")
    md.append(f"### Total Citations: {total_citations}")
    md.append("")
    md.append(f"*Updated: {datetime.now().strftime('%Y-%m-%d')}*")
    md.append("")

    if notable_pubs:
        md.append("# Notable Publications\n")
        for pub in notable_pubs:
            md.extend(format_pub_entry(pub))

    # md.append("## Full List\n")
    # for pub in pubs_sorted:
    #     md.extend(format_pub_entry(pub))

    return "\n".join(md)


def main():
    pubs = fetch_pubs()
    md = format_md(pubs)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    main()

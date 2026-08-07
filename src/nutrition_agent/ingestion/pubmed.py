"""Search PubMed and fetch abstracts via NCBI's E-utilities REST API.

Abstracts only for now -- full text is often paywalled and would need a
PDF parser; abstracts are enough to ground the "related studies" side of
the corpus. See docs/wiki/Sources/PubMed.md.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# NCBI asks for no more than ~3 requests/sec without an API key.
_MIN_REQUEST_INTERVAL_S = 0.4
_last_request_at = 0.0


@dataclass
class PubMedRecord:
    pmid: str
    title: str
    abstract: str
    journal: str
    year: str | None
    authors: list[str] = field(default_factory=list)
    url: str = ""


def _throttled_get(url: str) -> bytes:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < _MIN_REQUEST_INTERVAL_S:
        time.sleep(_MIN_REQUEST_INTERVAL_S - elapsed)
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = resp.read()
    finally:
        _last_request_at = time.monotonic()
    return data


def search_pubmed(query: str, retmax: int = 20) -> list[str]:
    """Return PubMed IDs matching a free-text query, ranked by relevance."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(retmax),
        "retmode": "json",
        "sort": "relevance",
    }
    url = f"{ESEARCH_URL}?{urllib.parse.urlencode(params)}"
    data = json.loads(_throttled_get(url))
    return data["esearchresult"]["idlist"]


def _text_or_empty(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def _parse_abstract(article: ET.Element) -> str:
    parts = []
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.get("Label")
        text = "".join(abstract_text.itertext()).strip()
        if not text:
            continue
        parts.append(f"{label}: {text}" if label else text)
    return "\n".join(parts)


def _parse_authors(article: ET.Element) -> list[str]:
    authors = []
    for author in article.findall(".//AuthorList/Author"):
        last = _text_or_empty(author.find("LastName"))
        initials = _text_or_empty(author.find("Initials"))
        if last:
            authors.append(f"{last} {initials}".strip())
    return authors


def _parse_year(article: ET.Element) -> str | None:
    year = _text_or_empty(article.find(".//Journal/JournalIssue/PubDate/Year"))
    if year:
        return year
    medline_date = _text_or_empty(article.find(".//Journal/JournalIssue/PubDate/MedlineDate"))
    return medline_date[:4] if medline_date else None


def fetch_abstracts(pmids: list[str]) -> list[PubMedRecord]:
    """Batch-fetch abstracts for a list of PubMed IDs in a single efetch call."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
    }
    url = f"{EFETCH_URL}?{urllib.parse.urlencode(params)}"
    xml_bytes = _throttled_get(url)
    root = ET.fromstring(xml_bytes)

    records = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text_or_empty(article.find(".//PMID"))
        if not pmid:
            continue
        title = _text_or_empty(article.find(".//ArticleTitle"))
        abstract = _parse_abstract(article)
        if not abstract:
            # Skip records with no abstract text (e.g. editorials, letters) --
            # nothing for the chunker to work with.
            continue
        records.append(
            PubMedRecord(
                pmid=pmid,
                title=title,
                abstract=abstract,
                journal=_text_or_empty(article.find(".//Journal/Title")),
                year=_parse_year(article),
                authors=_parse_authors(article),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            )
        )
    return records

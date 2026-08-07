from nutrition_agent.ingestion import pubmed

SAMPLE_XML = b"""<?xml version="1.0" ?>
<PubmedArticleSet>
<PubmedArticle>
  <MedlineCitation>
    <PMID>111</PMID>
    <Article>
      <Journal><Title>Nutrients</Title><JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
      <ArticleTitle>Seed oils and <i>inflammation</i>: a review.</ArticleTitle>
      <Abstract>
        <AbstractText Label="BACKGROUND">Seed oil intake has risen.</AbstractText>
        <AbstractText Label="CONCLUSION">More research is needed.</AbstractText>
      </Abstract>
      <AuthorList>
        <Author><LastName>Lee</LastName><Initials>K</Initials></Author>
        <Author><LastName>Kurniawan</LastName><Initials>K</Initials></Author>
      </AuthorList>
    </Article>
  </MedlineCitation>
</PubmedArticle>
<PubmedArticle>
  <MedlineCitation>
    <PMID>222</PMID>
    <Article>
      <Journal><Title>Old Journal</Title><JournalIssue><PubDate><MedlineDate>1987 Jan-Feb</MedlineDate></PubDate></JournalIssue></Journal>
      <ArticleTitle>Dietary cholesterol re-evaluated.</ArticleTitle>
      <Abstract>
        <AbstractText>No label here.</AbstractText>
      </Abstract>
    </Article>
  </MedlineCitation>
</PubmedArticle>
<PubmedArticle>
  <MedlineCitation>
    <PMID>333</PMID>
    <Article>
      <Journal><Title>Letters</Title><JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue></Journal>
      <ArticleTitle>An editorial with no abstract.</ArticleTitle>
    </Article>
  </MedlineCitation>
</PubmedArticle>
</PubmedArticleSet>
"""


def test_fetch_abstracts_parses_title_authors_and_labeled_abstract(monkeypatch):
    monkeypatch.setattr(pubmed, "_throttled_get", lambda url: SAMPLE_XML)

    records = pubmed.fetch_abstracts(["111", "222", "333"])
    by_pmid = {r.pmid: r for r in records}

    assert set(by_pmid) == {"111", "222"}  # 333 has no abstract, skipped

    r = by_pmid["111"]
    assert r.title == "Seed oils and inflammation: a review."
    assert r.journal == "Nutrients"
    assert r.year == "2024"
    assert r.authors == ["Lee K", "Kurniawan K"]
    assert "BACKGROUND: Seed oil intake has risen." in r.abstract
    assert "CONCLUSION: More research is needed." in r.abstract
    assert r.url == "https://pubmed.ncbi.nlm.nih.gov/111/"


def test_fetch_abstracts_falls_back_to_medline_date_year(monkeypatch):
    # The mock ignores the requested id list and always returns the full
    # SAMPLE_XML fixture, same as the labeled-abstract test above -- look up
    # PMID 222 by id rather than assuming it's first in the result list.
    monkeypatch.setattr(pubmed, "_throttled_get", lambda url: SAMPLE_XML)

    records = pubmed.fetch_abstracts(["222"])
    record = next(r for r in records if r.pmid == "222")

    assert record.year == "1987"
    assert record.abstract == "No label here."


def test_fetch_abstracts_empty_input_makes_no_request(monkeypatch):
    def boom(url):
        raise AssertionError("should not be called for empty pmid list")

    monkeypatch.setattr(pubmed, "_throttled_get", boom)

    assert pubmed.fetch_abstracts([]) == []

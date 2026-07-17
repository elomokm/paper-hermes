"""Tests for ArxivScraper."""

from paper_hermes.arxiv_scraper import ArxivScraper


def test_search_basic():
    scraper = ArxivScraper(max_results=3)
    papers = scraper.search("composite materials machine learning", max_results=3)

    assert len(papers) > 0, "Should find at least one paper"
    assert len(papers) <= 3

    paper = papers[0]
    assert paper.title
    assert paper.abstract
    assert paper.arxiv_id
    assert paper.url


def test_search_with_sort():
    scraper = ArxivScraper(max_results=2)
    papers = scraper.search("graph neural network", max_results=2, sort_by="relevance")

    assert len(papers) > 0


def test_get_paper():
    scraper = ArxivScraper()
    # Use a known arXiv paper ID
    paper = scraper.get_paper("1706.03762")  # Attention Is All You Need

    assert paper is not None
    assert "Attention" in paper.title
    assert len(paper.authors) > 0
    assert paper.arxiv_id == "1706.03762"


def test_get_paper_not_found():
    scraper = ArxivScraper()
    paper = scraper.get_paper("0000.00000")
    assert paper is None

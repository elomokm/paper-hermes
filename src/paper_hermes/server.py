"""Paper Hermes MCP Server — exposes paper search + summarization as MCP tools.

Usage:
    uv run python -m paper_hermes.server          # stdio transport (for Hermes ACP/CLI)
    uv run python -m paper_hermes.server --sse    # SSE transport (for remote clients)
"""

import json

from mcp.server.fastmcp import FastMCP

from paper_hermes.arxiv_scraper import ArxivScraper
from paper_hermes.summarizer import PaperSummarizer

mcp = FastMCP("Paper Hermes", dependencies=["arxiv", "openai"])
scraper = ArxivScraper(max_results=10)
summarizer = PaperSummarizer()


@mcp.tool()
def search_papers(query: str, max_results: int = 5, sort_by: str = "relevance") -> str:
    """Search arXiv for scientific papers. Returns paper list as JSON.

    Args:
        query: Search query. Use arXiv syntax: AND, OR, quotes for exact phrases.
               Examples: 'composite materials machine learning',
               '\"graph neural network\" AND polymer',
               'cat:cond-mat.mtrl-sci AND machine learning'
        max_results: Number of results (1-20, default 5)
        sort_by: 'relevance', 'lastUpdatedDate', 'submittedDate'
    """
    papers = scraper.search(query, max_results=max_results, sort_by=sort_by)
    result = [
        {
            "id": p.arxiv_id,
            "title": p.title,
            "authors": p.authors[:5],
            "n_authors": len(p.authors),
            "abstract_snippet": p.abstract[:300],
            "url": p.url,
            "pdf_url": p.pdf_url,
            "categories": p.categories,
            "published": p.published.isoformat() if p.published else None,
        }
        for p in papers
    ]
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_paper(arxiv_id: str, include_summary: bool = False) -> str:
    """Fetch a specific paper by arXiv ID with full details.

    Args:
        arxiv_id: arXiv paper ID (e.g., '1706.03762', '2303.06871')
        include_summary: If True, also generate an AI summary (uses LLM credits)
    """
    paper = scraper.get_paper(arxiv_id)
    if not paper:
        return json.dumps({"error": f"Paper {arxiv_id} not found"})

    result = {
        "id": paper.arxiv_id,
        "title": paper.title,
        "authors": paper.authors,
        "n_authors": len(paper.authors),
        "abstract": paper.abstract,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
        "categories": paper.categories,
        "published": paper.published.isoformat() if paper.published else None,
    }

    if include_summary:
        summary = summarizer.summarize(paper)
        result["summary"] = {
            "tl_dr": summary.tl_dr,
            "key_contributions": summary.key_contributions,
            "method": summary.method,
            "results": summary.results,
            "relevance_materials": summary.relevance_materials,
        }

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def summarize(arxiv_id: str) -> str:
    """Generate a structured summary of a paper in French.

    Args:
        arxiv_id: arXiv paper ID (e.g., '2510.26100')
    """
    paper = scraper.get_paper(arxiv_id)
    if not paper:
        return json.dumps({"error": f"Paper {arxiv_id} not found"})

    summary = summarizer.summarize(paper)
    result = {
        "paper_id": summary.paper_id,
        "title": summary.title,
        "tl_dr": summary.tl_dr,
        "key_contributions": summary.key_contributions,
        "method": summary.method,
        "results": summary.results,
        "relevance_materials": summary.relevance_materials,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    import sys

    if "--sse" in sys.argv:
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

"""Paper Hermes MCP Server — exposes paper search + summarization as MCP tools.

Usage:
    uv run python -m paper_hermes.server          # stdio transport (for Hermes ACP/CLI)
    uv run python -m paper_hermes.server --sse    # SSE transport (for remote clients)
"""

import json

from mcp.server.fastmcp import FastMCP

from paper_hermes.arxiv_scraper import ArxivScraper
from paper_hermes.summarizer import PaperSummarizer
from paper_hermes.subscriptions import (
    add_subscription as _add_sub,
    load_subscriptions,
    remove_subscription as _remove_sub,
    update_last_run,
)

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


@mcp.tool()
def daily_digest(topic: str, since_days: int = 1) -> str:
    """Get new papers for a subscribed topic since last check. Searches + summarizes.

    Args:
        topic: Topic key (e.g., 'safran-veille', 'ml-maths'). Must be subscribed first.
        since_days: Search papers from last N days (default 1 = today's new papers)
    """
    from datetime import datetime, timedelta, timezone

    subs = {s["topic"]: s for s in load_subscriptions()}
    if topic not in subs:
        return json.dumps({"error": f"Topic '{topic}' not subscribed. Use subscribe() first."})

    query = subs[topic]["query"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    papers = scraper.search(query, max_results=5, sort_by="submittedDate")

    # Filter by recency
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
    recent = [p for p in papers if p.published and p.published.replace(tzinfo=None) > cutoff]

    if not recent:
        update_last_run(topic, today)
        return json.dumps({"digest": [], "message": "Aucun nouveau papier aujourd'hui."})

    digest = []
    for p in recent:
        summary = summarizer.summarize(p)
        digest.append({
            "id": p.arxiv_id,
            "title": p.title,
            "authors": p.authors[:5],
            "url": p.url,
            "tl_dr": summary.tl_dr,
            "key_contributions": summary.key_contributions,
            "relevance_materials": summary.relevance_materials,
        })

    update_last_run(topic, today)
    return json.dumps({"digest": digest, "n_papers": len(digest), "topic": topic, "date": today}, ensure_ascii=False, indent=2)


@mcp.tool()
def subscribe(topic: str, query: str) -> str:
    """Subscribe to a topic for daily paper digests.

    Args:
        topic: Short topic key (e.g., 'safran-veille', 'ml-gnn', 'composite-ml')
        query: arXiv search query. Examples:
               '\"composite materials\" AND \"machine learning\"',
               'cat:cond-mat.mtrl-sci AND polymer',
               'equivariant AND \"neural network\" AND materials'
    """
    sub = _add_sub(topic, query)
    return json.dumps({"subscribed": topic, "query": query, "frequency": sub["frequency"]}, ensure_ascii=False)


@mcp.tool()
def subscriptions() -> str:
    """List all active subscriptions."""
    subs = load_subscriptions()
    return json.dumps(subs, ensure_ascii=False, indent=2)


@mcp.tool()
def unsubscribe(topic: str) -> str:
    """Remove a subscription."""
    ok = _remove_sub(topic)
    return json.dumps({"unsubscribed": topic if ok else None, "success": ok})


def main():
    import sys

    if "--sse" in sys.argv:
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

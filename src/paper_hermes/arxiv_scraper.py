"""arXiv API scraper for Paper Hermes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import arxiv


@dataclass
class Paper:
    """Scientific paper metadata."""
    id: str
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None
    url: str = ""
    pdf_url: str = ""
    categories: list[str] = field(default_factory=list)

    @property
    def arxiv_id(self) -> str:
        raw = self.id.split("/")[-1] if "/" in self.id else self.id
        # Strip version suffix (e.g., "1706.03762v7" -> "1706.03762")
        return raw.rsplit("v", 1)[0] if "v" in raw else raw


class ArxivScraper:
    """Search and fetch papers from arXiv."""

    def __init__(self, max_results: int = 10):
        self.client = arxiv.Client()
        self.max_results = max_results

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: str = "submittedDate",
    ) -> list[Paper]:
        """Search arXiv papers.

        Args:
            query: Search query (arXiv syntax supported)
            max_results: Max results (default: self.max_results)
            sort_by: 'relevance', 'lastUpdatedDate', 'submittedDate'
        """
        sort_map = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate,
        }
        sort = sort_map.get(sort_by, arxiv.SortCriterion.SubmittedDate)

        search = arxiv.Search(
            query=query,
            max_results=max_results or self.max_results,
            sort_by=sort,
        )

        papers = []
        for result in self.client.results(search):
            papers.append(self._to_paper(result))

        return papers

    def get_paper(self, arxiv_id: str) -> Optional[Paper]:
        """Fetch a single paper by arXiv ID."""
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(self.client.results(search), None)
        return self._to_paper(result) if result else None

    def _to_paper(self, result: arxiv.Result) -> Paper:
        return Paper(
            id=result.entry_id,
            title=result.title,
            authors=[str(a) for a in result.authors],
            abstract=result.summary.replace("\n", " "),
            published=result.published,
            updated=result.updated,
            url=result.entry_id,
            pdf_url=result.pdf_url or "",
            categories=result.categories,
        )

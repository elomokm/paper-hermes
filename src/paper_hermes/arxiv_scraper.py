"""arXiv API scraper using shared models."""

from typing import Optional

import arxiv

from paper_hermes.models import Paper


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

        return [self._to_paper(r) for r in self.client.results(search)]

    def get_paper(self, arxiv_id: str) -> Optional[Paper]:
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

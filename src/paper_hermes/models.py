"""Data models for Paper Hermes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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
        return raw.rsplit("v", 1)[0] if "v" in raw else raw


@dataclass
class SummarizeResult:
    """Structured summary of a paper."""
    paper_id: str
    title: str
    tl_dr: str  # one-line takeaway
    key_contributions: list[str] = field(default_factory=list)
    method: str = ""
    results: str = ""
    relevance_materials: str = ""  # specific to composite/material ML domain
    translated_abstract: str = ""  # abstract in French

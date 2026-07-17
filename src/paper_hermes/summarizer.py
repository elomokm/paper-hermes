"""Paper summarizer using LLM via OpenRouter."""

import json
import os

from openai import OpenAI

from paper_hermes.models import Paper, SummarizeResult

SUMMARY_PROMPT = """You are a scientific paper summarizer specialized in materials science,
composite materials, and applied ML. Summarize this paper in a structured way.

Paper title: {title}
Authors: {authors}
Abstract: {abstract}

Return ONLY valid JSON with these fields:
- tl_dr: one-sentence takeaway in French (max 100 chars)
- key_contributions: array of 2-3 key contributions in French
- method: one paragraph describing the method/approach in French (max 300 chars)
- results: key results or findings in French (max 300 chars)
- relevance_materials: why this matters for materials science / composite ML (max 200 chars), empty string if not relevant

Do not include markdown code fences, just raw JSON."""


class PaperSummarizer:
    """Summarize papers using an LLM."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str = "deepseek/deepseek-v4-flash",
    ):
        self.client = OpenAI(
            base_url=base_url or "https://openrouter.ai/api/v1",
            api_key=api_key or os.getenv("OPENROUTER_API_KEY", ""),
        )
        self.model = model

    def summarize(self, paper: Paper) -> SummarizeResult:
        prompt = SUMMARY_PROMPT.format(
            title=paper.title,
            authors=", ".join(paper.authors[:5]),
            abstract=paper.abstract[:4000],
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )

        raw = response.choices[0].message.content or "{}"
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}

        return SummarizeResult(
            paper_id=paper.arxiv_id,
            title=paper.title,
            tl_dr=data.get("tl_dr", "")[:200],
            key_contributions=data.get("key_contributions", [])[:3],
            method=data.get("method", "")[:500],
            results=data.get("results", "")[:500],
            relevance_materials=data.get("relevance_materials", "")[:300],
            translated_abstract="",
        )

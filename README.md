# Paper Hermes

MCP Server de veille scientifique.
arXiv + ChemRxiv → DeepSeek → Brain Obsidian → Telegram.

## Quick start

```bash
git clone https://github.com/elomokm/paper-hermes
cd paper-hermes
uv sync
export DEEPSEEK_API_KEY=sk-...
```

## MCP Tools

| Tool | Args | Description |
|---|---|---|
| `search_papers` | query, max_results, sort_by | Search arXiv |
| `get_paper` | arxiv_id, include_summary | Fetch paper details |
| `summarize` | arxiv_id | Structured summary in French |
| `translate` | arxiv_id | Translate abstract to French |
| `daily_digest` | topic, since_days | Get new papers for a topic |
| `subscribe` | topic, query | Subscribe to daily digests |
| `subscriptions` | — | List active subscriptions |
| `unsubscribe` | topic | Remove a subscription |

## Architecture

```
arXiv API ──→ ArxivScraper ──→ PaperSummarizer (DeepSeek) ──→ MCP Tools
ChemRxiv ──→ (Phase 4)                                           │
                                                                  ├── Obsidian Vault
                                                                  ├── Telegram (@Kadjogbe_bot)
                                                                  └── Hermes Agent / tout client MCP
```

## Usage with Hermes Agent

```bash
hermes mcp add paper-hermes --command "uv run --directory ~/DEV/paper-hermes python -m paper_hermes.server"
```

Then in Hermes:
- "cherche les derniers papiers sur les composites"
- "resume le papier 2510.26100"
- "abonne-moi a safran-veille"

## Cron

Un cron Hermes tourne chaque matin a 08:00:
- daily_digest pour tous les topics abonnes
- ecrit dans `~/Documents/Brain/Projects/Safran/veille/YYYY-MM-DD-digest.md`
- livre un resume sur Telegram

## Development

```bash
uv sync           # Install
uv run pytest -q  # Tests
uv run ruff check .  # Lint
```

## Subscriptions

Gerer dans `subscriptions.json` ou via les MCP tools.

Topics actifs par defaut:
- `safran-veille`: composites + polymeres + ML
- `ml-materials`: cond-mat + ML/equivariant/GNN

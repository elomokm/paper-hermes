# Paper Hermes

Hermes: projet Python 3.11+, package manager uv. Tests avec pytest. Pas de LangChain. Direct, pas de filler.

## Commandes
- Install: `uv sync`
- Tests: `uv run pytest -q`
- Lint: `uv run ruff check .`
- Run MCP server: `uv run python -m paper_hermes`

## Conventions
- Conventional Commits (feat:, fix:, refactor:)
- Branches: feat/nom, fix/nom
- PR avant merge sur main
- Pas de commit de secrets
- Français pour les docs/commits, anglais pour le code

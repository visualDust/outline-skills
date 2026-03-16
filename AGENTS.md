# Agent Instructions

Use the `outline-skills` skill for requests about Outline documents, collections, search, users, groups, comments, attachments, shares, stars, revisions, events, views, or file operations.

This is the only root-level agent instruction file for the repository. It applies to Claude Code, Codex, Cursor, Windsurf, and similar tools.

## Trigger

Typical triggers:
- Outline
- knowledge base
- document
- collection
- wiki
- search

Invoke with:
```text
$outline-skills
```

## Primary references

- [skills/outline-skills/SKILL.md](skills/outline-skills/SKILL.md) - complete agent-facing workflow and common operations
- [README.md](README.md) - concise human-facing install and project overview

## Configuration

Supported configuration sources, highest priority first:
1. CLI flags (`--api-key`, `--base-url`, `--timeout`)
2. Environment variables
3. Project config: `.outline-skills/config.json`
4. User config: `~/.outline-skills/config.json`

Environment variables:
```bash
export OUTLINE_API_KEY="ol_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OUTLINE_BASE_URL="https://app.getoutline.com/api"
```

## Project guidelines

- Follow PEP 8 for Python
- Keep code comments in English
- Keep docs consistent with the actual CLI
- Prefer `--text-file` / `--data-file` over embedding long Markdown/comment bodies directly in shell arguments
- When producing Outline document content, actively use Outline-supported rich formats when they improve readability, such as math, Mermaid diagrams, tables, and structured Markdown sections
- Outline math formatting differs slightly from the more common single-dollar convention:
  - Inline math should use double-dollar inline form, for example `$$E = mc^2$$`
  - Math blocks should start with `$$` followed by a newline, then the formula body, then a closing `$$`
  - Do not assume the usual `$...$` inline math syntax will render correctly in Outline
- Prefer native Outline-renderable content over plain-text fallbacks when appropriate; for example, use Mermaid for diagrams and proper math formatting for formulas instead of ASCII approximations
- Never commit secrets
- Run lint, type check, and tests after changes

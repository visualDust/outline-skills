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
- Never commit secrets
- Run lint, type check, and tests after changes

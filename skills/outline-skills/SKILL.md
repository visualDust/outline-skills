---
name: outline-skills
description: Operate Outline knowledge base - manage documents, collections, search, users, groups, comments, attachments, shares, stars, revisions, events, views, and file operations.
allowed-tools: Bash(outline-cli *)
---

# Outline Skills

## Purpose

Use this skill when the user asks to operate an Outline knowledge base via API/CLI.

## Outline Content Guidance

Outline documents support rich, structured content — not just plain paragraphs. When creating or updating documents, actively choose formatting that fits the task: headings, bullet/numbered lists, task lists, tables, quotes, code fences, callouts, links, attachments, and Mermaid diagrams when helpful.

Prefer readable structure over large walls of text. For example:
- use headings for sections
- use lists for steps, options, and summaries
- use tables for comparisons
- use code fences for commands/snippets
- use Mermaid for flows, architecture, or state diagrams

## When to Trigger

Trigger this skill when requests involve:
- Outline documents or collections
- knowledge base search
- users/groups/comments/attachments/file operations
- share links, stars, revisions, events, or views

## Agent Execution Checklist

Before running commands:
1. Confirm the user intent (read vs write vs destructive action).
2. Confirm required identifiers (`document-id`, `collection-id`, etc.).
3. Ensure auth is configured.
4. For destructive actions (`delete`, `archive`, `revoke`), confirm scope with user if ambiguous.

After running commands:
1. Report the key result in plain language.
2. Include IDs/URLs returned by Outline when useful.
3. If command fails, provide likely cause + exact next command to retry.

## Prerequisites

- Install CLI: `pip install outline-kb-cli`
- API key format: `ol_api_...`
- CLI command: `outline-cli`

## Configuration

### Supported Sources (highest priority first)
1. CLI flags: `--api-key`, `--base-url`, `--timeout`
2. Environment variables
3. Project config: `.outline-skills/config.json`
4. User config: `~/.outline-skills/config.json`

### Important Notes

**Parameter Order**: Global parameters (`--api-key`, `--base-url`, `--timeout`) MUST be placed BEFORE the subcommand:
```bash
# ✓ Correct
outline-cli --api-key "..." --base-url "..." collections list

# ✗ Wrong
outline-cli collections list --api-key "..." --base-url "..."
```

**Base URL Format**: The base URL usually include the `/api` suffix:
```bash
# ✓ Correct
https://app.getoutline.com/api
https://outline.example.com/api

# ✗ Wrong
https://app.getoutline.com
https://outline.example.com
```

### Environment Variables

```bash
export OUTLINE_API_KEY="ol_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export OUTLINE_BASE_URL="https://app.getoutline.com/api"  # Must include /api suffix
```

### Config File Example

```json
{
  "api_key": "ol_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "base_url": "https://app.getoutline.com/api",
  "timeout": 30
}
```

## Quick Command Reference

### Documents

```bash
outline-cli documents create --title "Title" --text "Content" --collection-id "collection-id"
outline-cli documents info --id "document-id"
outline-cli documents list --collection-id "collection-id"
outline-cli documents update --id "document-id" --title "New Title"
outline-cli documents archive --id "document-id"
outline-cli documents restore --id "document-id"
outline-cli documents delete --id "document-id"
outline-cli documents move --id "document-id" --collection-id "collection-id"
outline-cli documents duplicate --id "document-id"
outline-cli documents templatize --id "document-id"
outline-cli documents export --id "document-id"
outline-cli documents import --file "./doc.md"
outline-cli documents drafts --collection-id "collection-id"
outline-cli documents archived --limit 25 --offset 0
outline-cli documents deleted --limit 25 --offset 0
outline-cli documents viewed --limit 25 --offset 0
outline-cli documents empty-trash
outline-cli documents unpublish --id "document-id"
outline-cli documents add-user --id "document-id" --user-id "user-id"
outline-cli documents remove-user --id "document-id" --user-id "user-id"
outline-cli documents memberships --id "document-id"
outline-cli documents users --id "document-id"
outline-cli documents add-group --id "document-id" --group-id "group-id"
outline-cli documents remove-group --id "document-id" --group-id "group-id"
outline-cli documents group-memberships --id "document-id"
```

### Collections

```bash
outline-cli collections list
outline-cli collections info --id "collection-id"
outline-cli collections create --name "Collection Name"
outline-cli collections update --id "collection-id" --name "New Name"
outline-cli collections delete --id "collection-id"
outline-cli collections documents --id "collection-id"
outline-cli collections add-user --id "collection-id" --user-id "user-id"
outline-cli collections remove-user --id "collection-id" --user-id "user-id"
outline-cli collections memberships --id "collection-id"
outline-cli collections add-group --id "collection-id" --group-id "group-id"
outline-cli collections remove-group --id "collection-id" --group-id "group-id"
outline-cli collections group-memberships --id "collection-id"
outline-cli collections export --id "collection-id" --format "markdown"
outline-cli collections export-all --format "markdown"
```

### Search

```bash
outline-cli search "query"
outline-cli search "query" --titles-only
outline-cli search "query" --collection-id "collection-id" --limit 10
```

### Authentication

```bash
outline-cli auth info  # Get current user and team information
```

**Returns:**
- Current user details (id, name, email, role, preferences)
- Team/workspace information
- User's groups and permissions
- Available teams

**Use cases:**
- Verify API key is working and check which user it belongs to
- Get current user's ID for permission operations
- Check user's role and permissions
- Troubleshoot authentication issues

### Users / Groups

```bash
outline-cli users list --limit 25
outline-cli users info --id "user-id"
outline-cli users invite --email "new-user@example.com" --name "New User"
outline-cli users update --id "user-id" --name "Updated Name"
outline-cli users update-role --id "user-id" --role member
outline-cli users suspend --id "user-id"
outline-cli users activate --id "user-id"
outline-cli users delete --id "user-id"

outline-cli groups list
outline-cli groups info --id "group-id"
outline-cli groups create --name "Group Name"
outline-cli groups update --id "group-id" --name "New Name"
outline-cli groups delete --id "group-id"
outline-cli groups add-user --id "group-id" --user-id "user-id"
outline-cli groups remove-user --id "group-id" --user-id "user-id"
outline-cli groups memberships --id "group-id"
```

### Comments / Attachments

**Comment Features:**
- Comments support plain text only (no Markdown rendering)
- Maximum length: 1000 characters per comment
- For longer content, split into multiple comments
- Comments can be threaded (replies), resolved/unresolved, and reacted to with emojis

**Comment Operations:**
```bash
outline-cli comments list --document-id "document-id"
outline-cli comments create --document-id "document-id" --data "Comment text"
outline-cli comments create --document-id "document-id" --data "Reply text" --parent-id "parent-comment-id"
outline-cli comments update --id "comment-id" --data "Updated comment"
outline-cli comments delete --id "comment-id"
outline-cli comments resolve --id "comment-id"
outline-cli comments unresolve --id "comment-id"
outline-cli comments add-reaction --id "comment-id" --emoji "👍"
outline-cli comments remove-reaction --id "comment-id" --emoji "👍"
```

**When to use comment features:**
- Use `resolve` to mark discussions/issues as completed
- Use `unresolve` to reopen discussions that need more attention
- Use reactions for quick feedback (👍, ❤️, 😊, etc.)
- Use `--parent-id` to reply to specific comments and create threaded discussions
- When listing comments on documents with many comments, use `--limit` and `--offset` for pagination

**Attachment Operations:**
```bash
outline-cli attachments create --name "file.pdf" --document-id "document-id" --content-type "application/pdf" --size 1024
outline-cli attachments redirect --id "attachment-id"
outline-cli attachments delete --id "attachment-id"
```

### Shares / Stars / Revisions / Events

```bash
outline-cli shares create --document-id "document-id"
outline-cli shares list --document-id "document-id"
outline-cli shares info --id "share-id"
outline-cli shares revoke --id "share-id"
outline-cli shares update --id "share-id" --published

outline-cli stars create --document-id "document-id"
outline-cli stars list
outline-cli stars delete --id "star-id"
outline-cli stars update --id "star-id" --index 0

outline-cli revisions list --document-id "document-id"
outline-cli revisions info --id "revision-id"

outline-cli events list --limit 25
outline-cli events list --document-id "document-id"
```

### File Operations / Views

```bash
outline-cli file-operations list --type export
outline-cli file-operations info --id "file-operation-id"
outline-cli file-operations redirect --id "file-operation-id"
outline-cli file-operations delete --id "file-operation-id"

outline-cli views create --document-id "document-id"
outline-cli views list --document-id "document-id" --limit 25
```

## Useful Aliases

- `outline-cli docs` / `outline-cli doc` -> `outline-cli documents`
- `outline-cli colls` / `outline-cli coll` -> `outline-cli collections`

## Troubleshooting

### Authentication Errors

**401 Unauthorized:**
- Check API key exists and starts with `ol_api_`
- **Key may have expired** - Ask user to verify the key is still valid in Outline settings
- Guide user to create a new key: Settings → API → Create new API key
- Ensure the key hasn't been revoked or deleted

**403 Forbidden:**
- **Permission scope issue** - The API key may not have sufficient permissions
- **Resource access denied** - The user account associated with the key may not have access to the requested collection or document
- Ask user to verify:
  - The API key has the required scopes (read, write, admin)
  - Their account has access to the specific collection/document
  - They are not trying to access archived or deleted resources

### Connection and URL Errors

**404 Not Found:**
- If specific resource (document/collection): Resource may not exist or has been deleted
- **If basic operations fail** (e.g., `collections list`, `users list`):
  - **Base URL is likely incorrect**
  - Ask user to confirm the base URL includes `/api` suffix
  - Example: `https://outline.example.com/api` (not `https://outline.example.com`)
  - Verify the Outline instance URL is correct

**Connection errors:**
- Verify `OUTLINE_BASE_URL` is set correctly
- Verify instance is reachable (not behind firewall/VPN)
- Check for typos in the URL

### Comment-Specific Issues

**400 Bad Request - "Comment must be less than 1000 characters":**
- Single comment is limited to 1000 characters
- **Solution**: Split long content into multiple comments
- Consider using document content for longer text instead of comments

**Comment not rendering Markdown:**
- Comments only support plain text, not Markdown
- Use document content for formatted text

### Command not found
```bash
pip install --upgrade outline-kb-cli
```

## Safety Notes

- Never hardcode API keys
- Prefer env vars or config files
- For local config files on Unix:

```bash
chmod 600 ~/.outline-skills/config.json
```

- Confirm destructive actions before execution when user intent is unclear

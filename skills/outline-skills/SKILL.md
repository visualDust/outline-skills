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

For math, use dollar-sign delimiters so Outline renders it correctly: `$x^2 + y^2$` for inline math and `$$\int_0^1 x^2\,dx$$` for display math. Avoid LaTeX-style `\(...\)` and `\[...\]` delimiters because they may remain plain text in Outline.

Prefer readable structure over large walls of text. For example:
- use headings for sections
- use lists for steps, options, and summaries
- use tables for comparisons
- use code fences for commands/snippets
- use `$...$` or `$$...$$` for math expressions
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
4. Do not publish or share documents/collections unless the user asked for it.

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

**Output mode**: By default, `outline-cli` prints compact, agent-friendly JSON summaries rather than the complete raw Outline API response. The summary preserves practical fields like IDs, names, URLs, counts, pagination, and bounded text previews while omitting noisy nested fields such as policies and collaboration tokens. Use `--raw` when you need exact API JSON, and use `--max-text-chars` to control summary previews:
```bash
outline-cli auth info                         # compact identity/team summary
outline-cli search "deployment guide" --limit 5
outline-cli documents info --id "document-id" --max-text-chars 1000
outline-cli documents info --id "document-id" --max-text-chars 0  # metadata only
outline-cli auth info --raw                   # complete API response
```

`--raw` and `--max-text-chars` may be placed after the nested command, as shown above. API errors and config warnings are written to stderr, so stdout stays valid JSON on successful commands.

**Base URL Format**: The base URL usually include the `/api` suffix:
```bash
# ✓ Correct
https://app.getoutline.com/api
https://outline.example.com/api

# ✗ Wrong
https://app.getoutline.com
https://outline.example.com
```

**Large Content Input**: Prefer file-backed inputs for longer Markdown/comment bodies instead of very large shell arguments:
```bash
outline-cli documents create --title "Title" --collection-id "collection-id" --text-file ./doc.md
outline-cli documents update --id "document-id" --text-file ./doc.md
outline-cli comments create --document-id "document-id" --data-file ./comment.md
outline-cli comments update --id "comment-id" --data-file ./comment.md
```

**Local Markdown with images/assets**: Use the higher-level `documents create-from-file` workflow instead of plain `documents create --text-file` when the Markdown contains local image references. It preflights assets, uploads each unique local file as an Outline attachment, rewrites Markdown links, and rolls back temporary resources on upload/update failures.

Recommended safe sequence:
```bash
outline-cli documents create-from-file --file ./report.md --collection-id "collection-id" --dry-run
outline-cli documents create-from-file --file ./report.md --collection-id "collection-id" --title "Report" --save-rewritten ./report.outline.md
```

If the user asks for real testing, create/use an empty test collection first so existing Outline content is not polluted.

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
outline-cli documents create --title "Title" --text-file "./doc.md" --collection-id "collection-id"
outline-cli documents info --id "document-id"
outline-cli documents list --collection-id "collection-id"
outline-cli documents update --id "document-id" --title "New Title"
outline-cli documents update --id "document-id" --text-file "./doc.md"
outline-cli documents archive --id "document-id"
outline-cli documents restore --id "document-id"
outline-cli documents delete --id "document-id"
outline-cli documents move --id "document-id" --collection-id "collection-id"
outline-cli documents duplicate --id "document-id"
outline-cli documents templatize --id "document-id"
outline-cli documents export --id "document-id"
outline-cli documents import --file "./doc.md"   # local file; Markdown/text is imported directly, other files use Outline import flow (supported formats depend on server)
outline-cli documents create-from-file --file "./report.md" --collection-id "collection-id"  # local Markdown with local images/assets
outline-cli documents create-from-file --file "./report.md" --collection-id "collection-id" --dry-run
outline-cli documents create-from-file --file "./report.md" --collection-id "collection-id" --upload-local-links --save-rewritten "./report.outline.md"
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

**Sharing workflow for collections:**
- To share a collection with a specific person, use `collections add-user`.
- This requires `user-id`, so first find the user with `users list --query`, usually by email or name.
- After creating a collection/document, if sharing may be needed, ask the user whether it should be shared before the next interaction.
- If sharing with the user you are talking to, `admin` is usually the right default.
- If `auth info` shows the API key already belongs to the same person the user wants to share with, no extra sharing is needed.
- If sharing with someone else, ask whether they should get read-only access or edit/manage access.
- If the target person is ambiguous, confirm identity before sharing.

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
- `outline-cli comments create` accepts Markdown text through Outline's `text` field, so common formatting like paragraphs, lists, bold, italics, and inline code renders as rich text in Outline comments
- Maximum length is still about 1000 characters per posted comment
- Longer `comments create` replies are auto-split into numbered threaded comments like `[1/3]`, `[2/3]`, `[3/3]`
- Auto-splitting tries to preserve Markdown block boundaries such as paragraphs, lists, and fenced code blocks
- Comments can be threaded (replies), resolved/unresolved, and reacted to with emojis

**Comment Operations:**
```bash
outline-cli comments list --document-id "document-id"
outline-cli comments create --document-id "document-id" --data "Comment text"
outline-cli comments create --document-id "document-id" --data-file "./comment.md"
outline-cli comments create --document-id "document-id" --data "Reply text" --parent-id "parent-comment-id"
outline-cli comments update --id "comment-id" --data "Updated comment"
outline-cli comments update --id "comment-id" --data-file "./comment.md"
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
- `comments create` is the preferred path for rich-text replies from Markdown input
- For very long replies, let the CLI auto-split them instead of manually guessing chunk sizes
- When listing comments on documents with many comments, use `--limit` and `--offset` for pagination

**IMPORTANT - Comment Threading Limitation:**
- Outline only supports ONE level of threading (replies to top-level comments)
- When replying to a comment that already has a `parentCommentId`, you MUST use that comment's parent as your `--parent-id`, NOT the comment itself
- Example:
  - Top-level comment A (parentCommentId: null)
  - Reply B to A (parentCommentId: A's ID)
  - To reply to B, use `--parent-id A's ID`, NOT B's ID
- If you try to reply to a reply (nested 2+ levels), the comment will be created but won't display correctly in the UI

**Attachment Operations:**
```bash
outline-cli attachments create --name "file.pdf" --document-id "document-id" --content-type "application/pdf" --size 1024
outline-cli attachments upload --file "./figure.png" --document-id "document-id"
outline-cli attachments redirect --id "attachment-id"
outline-cli attachments delete --id "attachment-id"
```

**Local Markdown publishing details:**
- `documents create-from-file` supports inline Markdown images (`![alt](path.png)`), reference-style images, and HTML `<img src="path.png">` outside fenced/indented code blocks.
- Remote URLs, anchors, and `data:` URLs are left unchanged.
- By default, local asset paths must stay under the Markdown file directory. Use `--asset-root` to restrict the allowed tree, or `--allow-outside-assets` only when intentionally uploading files outside it.
- Use `--upload-local-links` to upload local non-image links such as PDFs.
- Broken local asset references are reported before any Outline API write happens, including line/column, resolved path, and reason.
- If an upload/update fails after temporary resources were created, the error includes best-effort cleanup results for uploaded attachments and the temporary document.

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

The CLI prints a `Hint:` line for common API errors. Follow it first — for example, a 404 hint that mentions `/api` usually means `OUTLINE_BASE_URL` is missing the `/api` suffix, while a resource-specific 404 usually means the ID is wrong or inaccessible to the API-key user.

**429 Rate Limited:**
- Wait briefly and retry.
- Reduce `--limit` for list/search commands.
- Avoid rapid loops that issue many Outline API calls.

**5xx Server Error:**
- Retry once in case the server/transient upload path recovered.
- If it persists, reduce payload size or split very large writes.
- For self-hosted Outline, check server logs around the printed endpoint/URL.

**Connection errors:**
- Verify `OUTLINE_BASE_URL` is set correctly
- Verify instance is reachable (not behind firewall/VPN)
- Check for typos in the URL

**Config warnings:**
- Invalid `.outline-skills/config.json` or `~/.outline-skills/config.json` files produce `Warning:` messages on stderr and are ignored.
- Fix malformed JSON or remove stale config files if the CLI appears to be using unexpected credentials/base URL.

### Comment-Specific Issues

**400 Bad Request - "Comment must be less than 1000 characters":**
- Single comment is limited to 1000 characters
- **Solution**: Split long content into multiple comments
- Consider using document content for longer text instead of comments

**Comment not rendering Markdown as expected:**
- `comments create` sends Markdown through Outline's `text` field and supports common formatting, but comments use a smaller rich-text schema than documents.
- Complex document-only blocks may not render inside comments; use document content for large or complex formatted output.
- If a long comment renders strangely, prefer `--data-file` and let the CLI's Markdown-aware splitter preserve block boundaries.

### Created content is not visible to the user

- Ask which Outline account the user is logged in with.
- The configured API key may belong to a different account than the one the user is using in the web UI.
- In that case, the created collection/document may need to be shared with the user's account before they can see it.

### Sharing and privacy safety

- Do not publish or share content unless the user explicitly asked.
- Prefer email for identity matching when available; users usually will not know their `user-id`.
- If the user asks to share with another person and permission level is unclear, ask before granting access.
- If you are not sure whether the target account is the user's own account, confirm first.

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

"""Helpers for Outline comment markdown handling and chunking."""

from __future__ import annotations

import textwrap
from typing import Any

MarkdownItClass: Any | None
try:
    from markdown_it import MarkdownIt as MarkdownItClass
except ImportError:  # pragma: no cover - optional fallback for local dev without dependency installed
    MarkdownItClass = None

OUTLINE_COMMENT_MAX_CHARS = 1000
MARKDOWN_PARSER = MarkdownItClass("commonmark") if MarkdownItClass is not None else None


def build_comment_data(text: str) -> dict[str, Any]:
    """Build a simple ProseMirror comment payload from plain text."""
    normalized = text.strip()
    lines = [line.strip() for line in normalized.splitlines() if line.strip()] if normalized else []
    content: list[dict[str, Any]] = []

    for line in lines:
        content.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})

    if not content:
        content.append({"type": "paragraph", "content": [{"type": "text", "text": normalized}]})

    return {"type": "doc", "content": content}


def split_comment_text(text: str, max_chars: int = OUTLINE_COMMENT_MAX_CHARS) -> list[str]:
    """Split comment text into chunks that fit Outline's size limit."""
    normalized = text.strip()
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1")
    if not normalized:
        return [normalized]
    if len(normalized) <= max_chars:
        return [normalized]

    markdown_chunks = _split_markdown_blocks(normalized, max_chars=max_chars)
    if markdown_chunks:
        return markdown_chunks

    return _split_comment_text_lines(normalized, max_chars=max_chars)


def prepare_comment_chunks(text: str, max_chars: int = OUTLINE_COMMENT_MAX_CHARS) -> list[str]:
    """Split long comment text and add numbered chunk markers when needed."""
    chunks = split_comment_text(text, max_chars=max_chars)
    if len(chunks) <= 1:
        return chunks

    total_chunks = len(chunks)
    while True:
        marker_max_length = len(_chunk_marker(total_chunks, total_chunks))
        available_chars = max_chars - marker_max_length
        if available_chars < 1:
            raise ValueError("max_chars is too small to fit numbered comment chunks")

        adjusted_chunks = split_comment_text(text, max_chars=available_chars)
        if len(adjusted_chunks) == total_chunks:
            return [
                f"{_chunk_marker(index, total_chunks)}{chunk}" for index, chunk in enumerate(adjusted_chunks, start=1)
            ]
        total_chunks = len(adjusted_chunks)


def is_comment_too_long_error(message: str) -> bool:
    """Return True if an error message indicates the comment exceeded Outline's limit."""
    lowered = message.lower()
    return "comment must be less than 1000 characters" in lowered or "less than 1000 characters" in lowered


def _split_comment_text_lines(text: str, *, max_chars: int) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return [normalized]

    lines = normalized.splitlines()
    if not lines:
        return [normalized]

    chunks: list[str] = []
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines
        if current_lines:
            chunks.append("\n".join(current_lines))
            current_lines = []

    for line in lines:
        for segment in _split_long_comment_line(line, max_chars=max_chars):
            if current_lines and _joined_comment_length(current_lines + [segment]) > max_chars:
                flush()
            current_lines.append(segment)
            if _joined_comment_length(current_lines) >= max_chars:
                flush()

    flush()
    return chunks or [normalized]


def _split_markdown_blocks(text: str, *, max_chars: int) -> list[str]:
    blocks = _extract_markdown_blocks(text)
    if not blocks:
        return []

    expanded_blocks: list[str] = []
    for block in blocks:
        if len(block) <= max_chars:
            expanded_blocks.append(block)
            continue

        nested = _split_large_markdown_block(block, max_chars=max_chars)
        if not nested:
            return []
        expanded_blocks.extend(nested)

    merged = _merge_markdown_blocks(expanded_blocks, max_chars=max_chars)
    return merged if len(merged) > 1 else []


def _extract_markdown_blocks(text: str) -> list[str]:
    if MARKDOWN_PARSER is None:
        return []

    lines = text.splitlines()
    tokens = MARKDOWN_PARSER.parse(text)
    blocks: list[str] = []
    seen_ranges: set[tuple[int, int]] = set()
    for token in tokens:
        if token.level != 0 or token.map is None or token.type.endswith("_close"):
            continue
        token_range = (token.map[0], token.map[1])
        if token_range in seen_ranges:
            continue
        seen_ranges.add(token_range)
        block = "\n".join(lines[token_range[0] : token_range[1]]).strip()
        if block:
            blocks.append(block)
    return blocks


def _split_large_markdown_block(block: str, *, max_chars: int) -> list[str]:
    if MARKDOWN_PARSER is None:
        return []

    lines = block.splitlines()
    tokens = MARKDOWN_PARSER.parse(block)
    top_level_tokens = [
        token for token in tokens if token.level == 0 and token.map is not None and not token.type.endswith("_close")
    ]
    if not top_level_tokens:
        return _split_comment_text_lines(block, max_chars=max_chars)

    first_type = top_level_tokens[0].type
    if first_type in {"ordered_list_open", "bullet_list_open"}:
        items = _extract_list_item_blocks(lines, tokens)
        if items:
            expanded_items: list[str] = []
            for item in items:
                if len(item) <= max_chars:
                    expanded_items.append(item)
                else:
                    expanded_items.extend(_split_comment_text_lines(item, max_chars=max_chars))
            return expanded_items

    if first_type == "fence":
        fenced_chunks = _split_fenced_code_block(block, max_chars=max_chars)
        if fenced_chunks:
            return fenced_chunks

    return _split_comment_text_lines(block, max_chars=max_chars)


def _extract_list_item_blocks(lines: list[str], tokens: list[Any]) -> list[str]:
    items: list[str] = []
    for token in tokens:
        if token.type != "list_item_open" or token.level != 1 or token.map is None:
            continue
        item = "\n".join(lines[token.map[0] : token.map[1]]).strip()
        if item:
            items.append(item)
    return items


def _split_fenced_code_block(block: str, *, max_chars: int) -> list[str]:
    lines = block.splitlines()
    if len(lines) < 3:
        return []

    opening = lines[0]
    closing = lines[-1]
    is_backtick_fence = opening.startswith("```") and closing.startswith("```")
    is_tilde_fence = opening.startswith("~~~") and closing.startswith("~~~")
    if not (is_backtick_fence or is_tilde_fence):
        return []

    wrapper_overhead = len(opening) + len(closing) + 2
    available_chars = max_chars - wrapper_overhead
    if available_chars < 1:
        return []

    inner_chunks = _split_comment_text_lines("\n".join(lines[1:-1]), max_chars=available_chars)
    return [f"{opening}\n{chunk}\n{closing}" for chunk in inner_chunks if chunk]


def _merge_markdown_blocks(blocks: list[str], *, max_chars: int) -> list[str]:
    chunks: list[str] = []
    current_blocks: list[str] = []

    def flush() -> None:
        nonlocal current_blocks
        if current_blocks:
            chunks.append("\n\n".join(current_blocks).strip())
            current_blocks = []

    for block in blocks:
        candidate = current_blocks + [block]
        if current_blocks and _joined_markdown_blocks_length(candidate) > max_chars:
            flush()
        current_blocks.append(block)
        if _joined_markdown_blocks_length(current_blocks) >= max_chars:
            flush()

    flush()
    return chunks


def _split_long_comment_line(line: str, *, max_chars: int) -> list[str]:
    if len(line) <= max_chars:
        return [line]

    wrapped = textwrap.wrap(
        line,
        width=max_chars,
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=True,
    )
    if not wrapped:
        return [line[:max_chars], *_split_comment_text_lines(line[max_chars:], max_chars=max_chars)]

    segments: list[str] = []
    for item in wrapped:
        stripped = item.strip()
        if not stripped:
            continue
        if len(stripped) <= max_chars:
            segments.append(stripped)
            continue
        for index in range(0, len(stripped), max_chars):
            segments.append(stripped[index : index + max_chars])
    return segments or [line[:max_chars]]


def _joined_comment_length(lines: list[str]) -> int:
    if not lines:
        return 0
    return sum(len(line) for line in lines) + max(0, len(lines) - 1)


def _joined_markdown_blocks_length(blocks: list[str]) -> int:
    if not blocks:
        return 0
    return sum(len(block) for block in blocks) + max(0, 2 * (len(blocks) - 1))


def _chunk_marker(index: int, total: int) -> str:
    return f"[{index}/{total}]\n\n"

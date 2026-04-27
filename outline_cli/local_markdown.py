"""Local Markdown publishing helpers for Outline.

This module contains the local-file side of the high-level Markdown publish
workflow.  It intentionally does not call the Outline API; it only scans a
Markdown document for local asset references, validates that those assets are
safe and readable, and later rewrites the exact URL spans after the caller has
uploaded each unique asset.

Keeping this logic independent from :mod:`outline_cli.client` makes the asset
scanner easy to test and extend (for example, adding Mermaid-exported images,
frontmatter cover images, or local PDF link publishing later).
"""

from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote, urlparse

from markdown_it import MarkdownIt

from .exceptions import OutlineValidationError


class AssetKind(str, Enum):
    """Kinds of local references that can become Outline attachments."""

    MARKDOWN_IMAGE = "markdown_image"
    MARKDOWN_REFERENCE_DEFINITION = "markdown_reference_definition"
    HTML_IMAGE = "html_image"
    MARKDOWN_LINK = "markdown_link"


class UrlCategory(str, Enum):
    """URL categories relevant to local publishing."""

    LOCAL = "local"
    REMOTE = "remote"
    DATA = "data"
    ANCHOR = "anchor"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class SourceSpan:
    """A character span in the original Markdown source."""

    start: int
    end: int
    line: int
    column: int

    def as_dict(self) -> dict[str, int]:
        return {
            "start": self.start,
            "end": self.end,
            "line": self.line,
            "column": self.column,
        }


@dataclass(frozen=True)
class LocalAssetReference:
    """One exact local URL occurrence in a Markdown document."""

    original_url: str
    replacement_span: SourceSpan
    kind: AssetKind
    resolved_path: Path
    content_type: str

    def as_dict(self) -> dict[str, object]:
        return {
            "originalUrl": self.original_url,
            "kind": self.kind.value,
            "resolvedPath": str(self.resolved_path),
            "contentType": self.content_type,
            "line": self.replacement_span.line,
            "column": self.replacement_span.column,
        }


@dataclass(frozen=True)
class IgnoredUrlReference:
    """A Markdown URL occurrence that does not require local upload."""

    url: str
    category: UrlCategory
    kind: AssetKind
    span: SourceSpan

    def as_dict(self) -> dict[str, object]:
        return {
            "url": self.url,
            "category": self.category.value,
            "kind": self.kind.value,
            "line": self.span.line,
            "column": self.span.column,
        }


@dataclass(frozen=True)
class LocalAssetProblem:
    """A preflight problem that should block publishing."""

    original_url: str
    kind: AssetKind
    span: SourceSpan
    reason: str
    resolved_path: Path | None = None

    def format(self) -> str:
        resolved = f"\n    resolved path: {self.resolved_path}" if self.resolved_path else ""
        return (
            f"line {self.span.line}, column {self.span.column}: {self.original_url}\n"
            f"    kind: {self.kind.value}{resolved}\n"
            f"    reason: {self.reason}"
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "originalUrl": self.original_url,
            "kind": self.kind.value,
            "line": self.span.line,
            "column": self.span.column,
            "reason": self.reason,
            "resolvedPath": str(self.resolved_path) if self.resolved_path else None,
        }


@dataclass
class LocalAsset:
    """A unique local asset path and all Markdown references to it."""

    path: Path
    content_type: str
    references: list[LocalAssetReference] = field(default_factory=list)

    @property
    def size(self) -> int:
        """Return the current file size in bytes."""
        return self.path.stat().st_size

    def as_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "name": self.path.name,
            "contentType": self.content_type,
            "size": self.size,
            "references": [reference.as_dict() for reference in self.references],
        }


@dataclass
class LocalMarkdownPublishPlan:
    """Validated local Markdown publish plan."""

    source_file: Path
    asset_root: Path
    title: str
    text: str
    assets: list[LocalAsset]
    ignored_urls: list[IgnoredUrlReference] = field(default_factory=list)

    def rewrite(self, uploaded_urls: dict[Path, str]) -> str:
        """Rewrite local asset URL spans using uploaded Outline URLs.

        Args:
            uploaded_urls: Mapping from resolved local asset path to final URL.

        Returns:
            Markdown text with exact asset URL spans replaced.

        Raises:
            OutlineValidationError: If a referenced asset has no uploaded URL.
        """
        replacements: list[tuple[int, int, str]] = []
        for asset in self.assets:
            try:
                replacement_url = uploaded_urls[asset.path]
            except KeyError as exc:
                raise OutlineValidationError(f"Missing uploaded URL for local asset: {asset.path}") from exc
            for reference in asset.references:
                replacements.append((reference.replacement_span.start, reference.replacement_span.end, replacement_url))

        rewritten = self.text
        for start, end, value in sorted(replacements, key=lambda item: item[0], reverse=True):
            rewritten = rewritten[:start] + value + rewritten[end:]
        return rewritten

    def as_dict(self) -> dict[str, object]:
        return {
            "sourceFile": str(self.source_file),
            "assetRoot": str(self.asset_root),
            "title": self.title,
            "assetCount": len(self.assets),
            "referenceCount": sum(len(asset.references) for asset in self.assets),
            "assets": [asset.as_dict() for asset in self.assets],
            "ignoredUrls": [ignored.as_dict() for ignored in self.ignored_urls],
        }


@dataclass(frozen=True)
class RawUrlReference:
    """A raw Markdown URL occurrence before URL classification/validation."""

    original_url: str
    replacement_span: SourceSpan
    kind: AssetKind
    requires_image: bool


_INLINE_LINK_RE = re.compile(
    r"(?P<bang>!?)"
    r"\[(?P<label>(?:\\.|[^\]\\])*)\]"
    r"\("
    r"(?P<dest><[^>\n]*>|[^\s)\n]+)"
    r"(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?"
    r"\)",
    re.MULTILINE,
)

_REFERENCE_DEF_RE = re.compile(
    r"^(?P<prefix>[ \t]{0,3}\[[^\]\n]+\]:[ \t]*)"
    r"(?P<dest><[^>\n]*>|[^\s\n]+)"
    r"(?P<suffix>[^\n]*)$",
    re.MULTILINE,
)

_REFERENCE_IMAGE_USAGE_RE = re.compile(
    r"!\[(?P<alt>(?:\\.|[^\]\\])*)\]"
    r"(?:\[(?P<label>[^\]\n]*)\])?",
    re.MULTILINE,
)

_REFERENCE_LABEL_RE = re.compile(r"^[ \t]{0,3}\[(?P<label>[^\]\n]+)\]:", re.MULTILINE)

_HTML_IMG_QUOTED_SRC_RE = re.compile(
    r"<img\b[^>]*?\bsrc\s*=\s*(?P<quote>['\"])(?P<src>.*?)(?P=quote)[^>]*>",
    re.IGNORECASE | re.DOTALL,
)

_HTML_IMG_UNQUOTED_SRC_RE = re.compile(
    r"<img\b[^>]*?\bsrc\s*=\s*(?P<src>[^'\"\s>]+)[^>]*>",
    re.IGNORECASE | re.DOTALL,
)

_IMAGE_EXTENSIONS = {
    ".apng",
    ".avif",
    ".bmp",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
}


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for match in re.finditer("\n", text):
        starts.append(match.end())
    return starts


def _line_col_for_offset(line_starts: Sequence[int], offset: int) -> tuple[int, int]:
    # Avoid importing bisect in hot paths? It is small but this keeps the function explicit.
    low = 0
    high = len(line_starts)
    while low + 1 < high:
        mid = (low + high) // 2
        if line_starts[mid] <= offset:
            low = mid
        else:
            high = mid
    return low + 1, offset - line_starts[low] + 1


def _span(line_starts: Sequence[int], start: int, end: int) -> SourceSpan:
    line, column = _line_col_for_offset(line_starts, start)
    return SourceSpan(start=start, end=end, line=line, column=column)


def _code_spans(text: str) -> list[tuple[int, int]]:
    """Return character spans for fenced/indented block code."""
    markdown = MarkdownIt("commonmark")
    tokens = markdown.parse(text)
    starts = _line_starts(text)
    spans: list[tuple[int, int]] = []
    for token in tokens:
        if token.type not in {"fence", "code_block"} or token.map is None:
            continue
        start_line, end_line = token.map
        start = starts[start_line] if start_line < len(starts) else len(text)
        end = starts[end_line] if end_line < len(starts) else len(text)
        spans.append((start, end))
    return spans


def _is_inside_any_span(start: int, end: int, spans: Sequence[tuple[int, int]]) -> bool:
    return any(start >= span_start and end <= span_end for span_start, span_end in spans)


def _strip_markdown_destination(destination: str) -> str:
    if destination.startswith("<") and destination.endswith(">"):
        return destination[1:-1]
    return destination


def _normalize_reference_label(label: str) -> str:
    """Normalize a Markdown reference label using CommonMark-style whitespace folding."""
    return " ".join(label.strip().casefold().split())


def _image_reference_labels(text: str, code_spans: Sequence[tuple[int, int]]) -> set[str]:
    """Return normalized labels used by reference-style Markdown images."""
    labels: set[str] = set()
    for match in _REFERENCE_IMAGE_USAGE_RE.finditer(text):
        if _is_inside_any_span(match.start(), match.end(), code_spans):
            continue
        # Inline images ``![alt](url)`` are handled separately.  In that case
        # this regex sees the ``![alt]`` prefix with no label, so skip when the
        # next source character is the inline destination opener.
        if match.end() < len(text) and text[match.end()] == "(":
            continue
        raw_label = match.group("label")
        if raw_label is None or raw_label == "":
            raw_label = match.group("alt")
        labels.add(_normalize_reference_label(raw_label))
    return labels


def _raw_references(text: str, *, upload_local_links: bool) -> list[RawUrlReference]:
    """Collect raw URL spans from Markdown/HTML constructs we know how to rewrite."""
    line_starts = _line_starts(text)
    code_spans = _code_spans(text)
    image_reference_labels = _image_reference_labels(text, code_spans)
    references: list[RawUrlReference] = []

    for match in _INLINE_LINK_RE.finditer(text):
        if _is_inside_any_span(match.start(), match.end(), code_spans):
            continue
        is_image = bool(match.group("bang"))
        if not is_image and not upload_local_links:
            continue
        dest_start, dest_end = match.span("dest")
        destination = match.group("dest")
        references.append(
            RawUrlReference(
                original_url=_strip_markdown_destination(destination),
                replacement_span=_span(line_starts, dest_start, dest_end),
                kind=AssetKind.MARKDOWN_IMAGE if is_image else AssetKind.MARKDOWN_LINK,
                requires_image=is_image,
            )
        )

    for match in _REFERENCE_DEF_RE.finditer(text):
        if _is_inside_any_span(match.start(), match.end(), code_spans):
            continue
        label_match = _REFERENCE_LABEL_RE.match(match.group(0))
        normalized_label = _normalize_reference_label(label_match.group("label")) if label_match else ""
        dest_start, dest_end = match.span("dest")
        destination = match.group("dest")
        original_url = _strip_markdown_destination(destination)
        is_image_reference = normalized_label in image_reference_labels
        if not upload_local_links and not is_image_reference:
            continue
        references.append(
            RawUrlReference(
                original_url=original_url,
                replacement_span=_span(line_starts, dest_start, dest_end),
                kind=AssetKind.MARKDOWN_REFERENCE_DEFINITION,
                requires_image=is_image_reference,
            )
        )

    seen_html_spans: set[tuple[int, int]] = set()
    for pattern in (_HTML_IMG_QUOTED_SRC_RE, _HTML_IMG_UNQUOTED_SRC_RE):
        for match in pattern.finditer(text):
            if _is_inside_any_span(match.start(), match.end(), code_spans):
                continue
            src_start, src_end = match.span("src")
            if (src_start, src_end) in seen_html_spans:
                continue
            seen_html_spans.add((src_start, src_end))
            references.append(
                RawUrlReference(
                    original_url=match.group("src"),
                    replacement_span=_span(line_starts, src_start, src_end),
                    kind=AssetKind.HTML_IMAGE,
                    requires_image=True,
                )
            )

    references.sort(key=lambda reference: reference.replacement_span.start)
    return references


def _classify_url(url: str) -> UrlCategory:
    stripped = url.strip()
    if not stripped:
        return UrlCategory.UNSUPPORTED
    if stripped.startswith("#"):
        return UrlCategory.ANCHOR

    parsed = urlparse(stripped)
    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"} or stripped.startswith("//"):
        return UrlCategory.REMOTE
    if scheme == "data":
        return UrlCategory.DATA
    if scheme in {"mailto", "tel", "javascript"}:
        return UrlCategory.UNSUPPORTED
    if scheme == "file" or not scheme:
        return UrlCategory.LOCAL
    return UrlCategory.UNSUPPORTED


def _local_path_from_url(url: str, *, base_dir: Path) -> Path:
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() == "file":
        raw_path = parsed.path
        if parsed.netloc and parsed.netloc not in {"", "localhost"}:
            # ``file://host/path`` is not portable; keep the host to make the error actionable.
            raw_path = f"//{parsed.netloc}{parsed.path}"
    else:
        raw_path = parsed.path or url
    decoded_path = unquote(raw_path)
    candidate = Path(decoded_path).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve(strict=False)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _looks_like_image_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    suffix = Path(unquote(parsed.path)).suffix.lower()
    if suffix in _IMAGE_EXTENSIONS:
        return True
    guessed = mimetypes.guess_type(parsed.path)[0]
    return bool(guessed and guessed.startswith("image/"))


def _guess_content_type(path: Path) -> str:
    return mimetypes.guess_type(str(path))[0] or "application/octet-stream"


def _requires_image(reference: RawUrlReference) -> bool:
    return reference.requires_image


def _default_title(path: Path) -> str:
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    return title or path.stem or path.name


def prepare_local_markdown_publish_plan(
    file: str | Path,
    *,
    title: str | None = None,
    asset_root: str | Path | None = None,
    allow_outside_assets: bool = False,
    upload_local_links: bool = False,
) -> LocalMarkdownPublishPlan:
    """Read and validate a local Markdown file for Outline publishing.

    Args:
        file: Markdown file path.
        title: Optional document title. Defaults to a normalized file stem.
        asset_root: Directory that local assets must live under. Defaults to the
            Markdown file's directory.
        allow_outside_assets: Allow local assets outside ``asset_root``.
        upload_local_links: Also upload local non-image Markdown links.

    Returns:
        A validated publish plan.

    Raises:
        OutlineValidationError: If the source file or any local asset reference
            is invalid.  All local failures are reported together so the caller
            can fix them in one pass.
    """
    source_path = Path(file).expanduser().resolve(strict=False)
    if not source_path.is_file():
        raise OutlineValidationError(f"create-from-file expects a local Markdown file, but '{file}' was not found.")
    if source_path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise OutlineValidationError(
            f"create-from-file currently expects a Markdown/text file (.md, .markdown, .txt), got '{source_path.name}'."
        )

    try:
        text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise OutlineValidationError(f"Unable to decode '{file}' as UTF-8 text.") from exc

    base_dir = source_path.parent
    root = Path(asset_root).expanduser() if asset_root is not None else base_dir
    root = root.resolve(strict=False)
    if not root.exists():
        raise OutlineValidationError(f"Asset root does not exist: {root}")
    if not root.is_dir():
        raise OutlineValidationError(f"Asset root is not a directory: {root}")

    assets_by_path: dict[Path, LocalAsset] = {}
    ignored_urls: list[IgnoredUrlReference] = []
    problems: list[LocalAssetProblem] = []

    for reference in _raw_references(text, upload_local_links=upload_local_links):
        category = _classify_url(reference.original_url)
        if category is not UrlCategory.LOCAL:
            ignored_urls.append(
                IgnoredUrlReference(
                    url=reference.original_url,
                    category=category,
                    kind=reference.kind,
                    span=reference.replacement_span,
                )
            )
            continue

        resolved_path = _local_path_from_url(reference.original_url, base_dir=base_dir)
        if not allow_outside_assets and not _is_relative_to(resolved_path, root):
            problems.append(
                LocalAssetProblem(
                    original_url=reference.original_url,
                    kind=reference.kind,
                    span=reference.replacement_span,
                    resolved_path=resolved_path,
                    reason=f"local asset is outside the allowed asset root ({root})",
                )
            )
            continue
        if not resolved_path.exists():
            problems.append(
                LocalAssetProblem(
                    original_url=reference.original_url,
                    kind=reference.kind,
                    span=reference.replacement_span,
                    resolved_path=resolved_path,
                    reason="file not found",
                )
            )
            continue
        if not resolved_path.is_file():
            problems.append(
                LocalAssetProblem(
                    original_url=reference.original_url,
                    kind=reference.kind,
                    span=reference.replacement_span,
                    resolved_path=resolved_path,
                    reason="path is not a regular file",
                )
            )
            continue

        content_type = _guess_content_type(resolved_path)
        if _requires_image(reference) and not content_type.startswith("image/"):
            problems.append(
                LocalAssetProblem(
                    original_url=reference.original_url,
                    kind=reference.kind,
                    span=reference.replacement_span,
                    resolved_path=resolved_path,
                    reason=f"image reference points to a non-image file (detected content type: {content_type})",
                )
            )
            continue

        asset = assets_by_path.setdefault(
            resolved_path,
            LocalAsset(path=resolved_path, content_type=content_type, references=[]),
        )
        asset.references.append(
            LocalAssetReference(
                original_url=reference.original_url,
                replacement_span=reference.replacement_span,
                kind=reference.kind,
                resolved_path=resolved_path,
                content_type=content_type,
            )
        )

    if problems:
        formatted = "\n\n".join(problem.format() for problem in problems)
        raise OutlineValidationError(
            f"Local Markdown asset preflight failed. No Outline document or attachment was created.\n\n{formatted}"
        )

    return LocalMarkdownPublishPlan(
        source_file=source_path,
        asset_root=root,
        title=title or _default_title(source_path),
        text=text,
        assets=list(assets_by_path.values()),
        ignored_urls=ignored_urls,
    )


def write_rewritten_markdown(path: str | Path, text: str) -> None:
    """Write rewritten Markdown to a UTF-8 file, creating parents as needed."""
    output_path = Path(path).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def local_markdown_problems_for_display(problems: Iterable[LocalAssetProblem]) -> str:
    """Format preflight problems for human-facing CLI output."""
    return "\n\n".join(problem.format() for problem in problems)

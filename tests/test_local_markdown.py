"""Local Markdown publish-plan tests."""

from pathlib import Path

import pytest

from outline_cli import OutlineValidationError
from outline_cli.local_markdown import prepare_local_markdown_publish_plan


def _write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n")


def test_prepare_local_markdown_collects_deduplicates_and_rewrites_assets(tmp_path):
    """Local image references should be validated, deduplicated, and rewritten by exact spans."""
    _write_png(tmp_path / "images" / "chart.png")
    _write_png(tmp_path / "images" / "logo.png")
    _write_png(tmp_path / "images" / "ref.png")
    _write_png(tmp_path / "images" / "shortcut.png")

    source = tmp_path / "release-notes.md"
    source.write_text(
        "# Release Notes\n\n"
        "![Chart](images/chart.png)\n\n"
        'Again: ![Chart again](./images/chart.png "same file")\n\n'
        "HTML: <img alt='Logo' src='images/logo.png'>\n\n"
        "Reference: ![Ref image][ref-image]\n\n"
        "Shortcut: ![shortcut image]\n\n"
        "Remote stays: ![Remote](https://example.com/remote.png)\n\n"
        "```md\n![Ignored](images/missing.png)\n```\n\n"
        "[ref-image]: images/ref.png\n"
        "[shortcut image]: images/shortcut.png\n",
        encoding="utf-8",
    )

    plan = prepare_local_markdown_publish_plan(source)

    assert plan.title == "release notes"
    assert {asset.path.name for asset in plan.assets} == {"chart.png", "logo.png", "ref.png", "shortcut.png"}
    chart = next(asset for asset in plan.assets if asset.path.name == "chart.png")
    assert len(chart.references) == 2
    assert len(plan.ignored_urls) == 1
    assert plan.ignored_urls[0].url == "https://example.com/remote.png"

    rewritten = plan.rewrite({asset.path: f"https://outline.test/{asset.path.name}" for asset in plan.assets})
    assert "![Chart](https://outline.test/chart.png)" in rewritten
    assert '![Chart again](https://outline.test/chart.png "same file")' in rewritten
    assert "<img alt='Logo' src='https://outline.test/logo.png'>" in rewritten
    assert "[ref-image]: https://outline.test/ref.png" in rewritten
    assert "[shortcut image]: https://outline.test/shortcut.png" in rewritten
    assert "https://example.com/remote.png" in rewritten
    assert "![Ignored](images/missing.png)" in rewritten


def test_prepare_local_markdown_reports_all_missing_assets(tmp_path):
    """Broken local asset links should block publishing with actionable diagnostics."""
    source = tmp_path / "doc.md"
    source.write_text(
        '![Missing one](missing-one.png)\n\n<img src="missing-two.png">\n',
        encoding="utf-8",
    )

    with pytest.raises(OutlineValidationError) as exc_info:
        prepare_local_markdown_publish_plan(source)

    message = str(exc_info.value)
    assert "Local Markdown asset preflight failed" in message
    assert "No Outline document or attachment was created" in message
    assert "missing-one.png" in message
    assert "missing-two.png" in message
    assert "file not found" in message
    assert "line 1" in message
    assert "line 3" in message


def test_prepare_local_markdown_blocks_assets_outside_root(tmp_path):
    """Asset-root confinement should prevent accidental uploads from unrelated directories."""
    source_dir = tmp_path / "docs"
    asset_dir = source_dir / "assets"
    outside_dir = tmp_path / "outside"
    _write_png(outside_dir / "secret.png")
    source_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    source = source_dir / "doc.md"
    source.write_text("![Secret](../outside/secret.png)\n", encoding="utf-8")

    with pytest.raises(OutlineValidationError) as exc_info:
        prepare_local_markdown_publish_plan(source, asset_root=asset_dir)

    assert "outside the allowed asset root" in str(exc_info.value)

    plan = prepare_local_markdown_publish_plan(source, asset_root=asset_dir, allow_outside_assets=True)
    assert [asset.path.name for asset in plan.assets] == ["secret.png"]


def test_prepare_local_markdown_can_upload_local_non_image_links_when_requested(tmp_path):
    """The scanner is extensible beyond images for explicit local attachment links."""
    report = tmp_path / "report.pdf"
    report.write_bytes(b"%PDF-1.7")
    source = tmp_path / "doc.md"
    source.write_text("[Download report](report.pdf)\n", encoding="utf-8")

    default_plan = prepare_local_markdown_publish_plan(source)
    assert default_plan.assets == []

    link_plan = prepare_local_markdown_publish_plan(source, upload_local_links=True)
    assert len(link_plan.assets) == 1
    assert link_plan.assets[0].content_type == "application/pdf"
    rewritten = link_plan.rewrite({link_plan.assets[0].path: "https://outline.test/report.pdf"})
    assert "[Download report](https://outline.test/report.pdf)" in rewritten


def test_prepare_local_markdown_rejects_non_image_file_in_image_reference(tmp_path):
    """A Markdown image syntax pointing at a PDF should be treated as author error."""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    source = tmp_path / "doc.md"
    source.write_text("![Not really an image](paper.pdf)\n", encoding="utf-8")

    with pytest.raises(OutlineValidationError) as exc_info:
        prepare_local_markdown_publish_plan(source)

    assert "non-image file" in str(exc_info.value)
    assert "application/pdf" in str(exc_info.value)

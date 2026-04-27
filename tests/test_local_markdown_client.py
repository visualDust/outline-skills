"""High-level local Markdown client workflow tests."""

from pathlib import Path

import pytest

from outline_cli import OutlineAPIError, OutlineClient, OutlineValidationError


def _write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n")


def test_documents_create_from_file_dry_run_preflights_without_api_calls(tmp_path):
    """Dry-run should return a rich local plan and avoid Outline API calls."""
    _write_png(tmp_path / "figure.png")
    source = tmp_path / "doc.md"
    source.write_text("![Figure](figure.png)\n", encoding="utf-8")
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")

    def fail_if_called(*args, **kwargs):  # pragma: no cover - assertion helper
        raise AssertionError("API should not be called during dry-run")

    client.documents_create = fail_if_called
    result = client.documents_create_from_file(
        file=str(source),
        collection_id="coll-1",
        dry_run=True,
    )

    assert result["data"]["dryRun"] is True
    assert result["data"]["plan"]["assetCount"] == 1
    assert result["data"]["plan"]["referenceCount"] == 1


def test_documents_create_from_file_uploads_rewrites_and_updates_placeholder(tmp_path):
    """The full workflow should create placeholder, upload assets, rewrite Markdown, and update/publish."""
    _write_png(tmp_path / "figure.png")
    source = tmp_path / "doc.md"
    source.write_text("# Demo\n\n![Figure](figure.png)\n", encoding="utf-8")
    rewritten_path = tmp_path / "out" / "rewritten.md"
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    calls = []

    def fake_documents_create(**kwargs):
        calls.append(("documents_create", kwargs))
        return {"ok": True, "data": {"id": "doc-placeholder", "title": kwargs["title"]}}

    def fake_attachments_upload_file(**kwargs):
        calls.append(("attachments_upload_file", kwargs))
        return {
            "attachment": {"id": "att-1", "name": "figure.png"},
            "upload": {"ok": True},
            "url": "https://outline.test/api/attachments.redirect?id=att-1",
        }

    def fake_documents_update(**kwargs):
        calls.append(("documents_update", kwargs))
        return {"ok": True, "data": {"id": kwargs["id"], "title": kwargs["title"], "text": kwargs["text"]}}

    client.documents_create = fake_documents_create
    client.attachments_upload_file = fake_attachments_upload_file
    client.documents_update = fake_documents_update

    result = client.documents_create_from_file(
        file=str(source),
        collection_id="coll-1",
        title="Demo Title",
        publish=True,
        save_rewritten=str(rewritten_path),
    )

    assert [name for name, _ in calls] == ["documents_create", "attachments_upload_file", "documents_update"]
    assert calls[0][1]["publish"] is False
    assert calls[1][1]["document_id"] == "doc-placeholder"
    assert calls[1][1]["file_path"].name == "figure.png"
    update_payload = calls[2][1]
    assert update_payload["id"] == "doc-placeholder"
    assert update_payload["title"] == "Demo Title"
    assert update_payload["publish"] is True
    assert "https://outline.test/api/attachments.redirect?id=att-1" in update_payload["text"]
    assert rewritten_path.read_text(encoding="utf-8") == update_payload["text"]
    assert result["data"]["attachments"][0]["attachmentId"] == "att-1"


def test_documents_create_from_file_preflight_failure_blocks_all_api_calls(tmp_path):
    """Broken local references should fail before creating temporary Outline resources."""
    source = tmp_path / "doc.md"
    source.write_text("![Missing](missing.png)\n", encoding="utf-8")
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")

    def fail_if_called(*args, **kwargs):  # pragma: no cover - assertion helper
        raise AssertionError("No API call should happen after failed local preflight")

    client.documents_create = fail_if_called

    with pytest.raises(OutlineValidationError) as exc_info:
        client.documents_create_from_file(file=str(source), collection_id="coll-1")

    assert "No Outline document or attachment was created" in str(exc_info.value)
    assert "missing.png" in str(exc_info.value)


def test_documents_create_from_file_rolls_back_on_final_update_error(tmp_path):
    """If final document update fails, uploaded attachments and placeholder doc should be cleaned up."""
    _write_png(tmp_path / "figure.png")
    source = tmp_path / "doc.md"
    source.write_text("![Figure](figure.png)\n", encoding="utf-8")
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    deleted = []

    client.documents_create = lambda **kwargs: {"ok": True, "data": {"id": "doc-placeholder"}}
    client.attachments_upload_file = lambda **kwargs: {
        "attachment": {"id": "att-1"},
        "upload": {"ok": True},
        "url": "https://outline.test/api/attachments.redirect?id=att-1",
    }

    def fake_documents_update(**kwargs):
        raise OutlineAPIError("Outline refused update", status_code=500)

    client.documents_update = fake_documents_update
    client.attachments_delete = lambda attachment_id: deleted.append(("attachment", attachment_id)) or {"ok": True}

    def fake_documents_delete(document_id, permanent=False):
        deleted.append(("document", document_id))
        return {"ok": True}

    client.documents_delete = fake_documents_delete

    with pytest.raises(OutlineAPIError) as exc_info:
        client.documents_create_from_file(file=str(source), collection_id="coll-1")

    message = str(exc_info.value)
    assert "Failed to create Outline document from local Markdown file" in message
    assert "cleanup:" in message
    assert "deleted attachment att-1" in message
    assert "deleted temporary document doc-placeholder" in message
    assert deleted == [("attachment", "att-1"), ("document", "doc-placeholder")]


def test_attachments_upload_file_rolls_back_created_attachment_on_upload_error(tmp_path):
    """Low-level upload helper should produce contextual errors and clean failed attachment records."""
    file_path = tmp_path / "figure.png"
    _write_png(file_path)
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    deleted = []

    client.attachments_create = lambda **kwargs: {
        "ok": True,
        "data": {
            "attachment": {"id": "att-1", "url": "/api/attachments.redirect?id=att-1"},
            "uploadUrl": "/api/files.create",
            "form": {"key": "uploads/figure.png"},
        },
    }
    client._upload_file = lambda **kwargs: (_ for _ in ()).throw(OutlineAPIError("storage unavailable"))
    client.attachments_delete = lambda attachment_id: deleted.append(attachment_id) or {"ok": True}

    with pytest.raises(OutlineAPIError) as exc_info:
        client.attachments_upload_file(document_id="doc-1", file_path=file_path)

    message = str(exc_info.value)
    assert "Failed to upload local file bytes" in message
    assert "local_file:" in message
    assert "storage unavailable" in message
    assert deleted == ["att-1"]

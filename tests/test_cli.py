"""CLI smoke tests."""

import outline_cli.cli as cli
from outline_cli import OutlineClient, OutlineValidationError


def test_main_passes_publish_flag(monkeypatch):
    """`--publish` should set args.publish to True."""
    captured = {}

    class DummyClient:
        pass

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())

    def fake_update_document(client, args):
        captured["publish"] = args.publish
        return 0

    monkeypatch.setattr(cli, "update_document", fake_update_document)
    monkeypatch.setattr(
        "sys.argv",
        ["outline-cli", "--api-key", "ol_api_test", "documents", "update", "--id", "doc-1", "--publish"],
    )

    assert cli.main() == 0
    assert captured["publish"] is True


def test_main_passes_unpublish_flag(monkeypatch):
    """`--unpublish` should set args.publish to False."""
    captured = {}

    class DummyClient:
        pass

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())

    def fake_update_document(client, args):
        captured["publish"] = args.publish
        return 0

    monkeypatch.setattr(cli, "update_document", fake_update_document)
    monkeypatch.setattr(
        "sys.argv",
        ["outline-cli", "--api-key", "ol_api_test", "documents", "update", "--id", "doc-1", "--unpublish"],
    )

    assert cli.main() == 0
    assert captured["publish"] is False


def test_documents_import_reads_markdown_file(tmp_path, monkeypatch):
    """`documents import` should read a local Markdown file and delegate to create."""
    source = tmp_path / "camera-ready-notes.md"
    source.write_text("# Notes\n\nHello Outline\n", encoding="utf-8")

    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    captured = {}

    def fake_documents_create(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(client, "documents_create", fake_documents_create)

    result = client.documents_import(
        file=str(source),
        collection_id="coll-1",
        parent_document_id="parent-1",
        publish=False,
    )

    assert result == {"ok": True}
    assert captured == {
        "title": "camera ready notes",
        "text": "# Notes\n\nHello Outline\n",
        "collection_id": "coll-1",
        "parent_document_id": "parent-1",
        "publish": False,
    }


def test_documents_import_rejects_missing_file():
    """`documents import` should fail clearly for missing paths."""
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")

    try:
        client.documents_import(file="/tmp/does-not-exist.md", collection_id="coll-1")
    except OutlineValidationError as exc:
        assert "was not found" in str(exc)
    else:
        raise AssertionError("Expected OutlineValidationError")


def test_documents_import_rejects_binary_extension(tmp_path):
    """Binary imports should upload an attachment and then call documents.import."""
    source = tmp_path / "slides.pdf"
    source.write_bytes(b"%PDF-1.7")
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    captured = {}

    def fake_documents_create(**kwargs):
        captured["documents_create"] = kwargs
        return {"data": {"id": "placeholder-1"}}

    def fake_attachments_create(**kwargs):
        captured["attachments_create"] = kwargs
        return {
            "data": {
                "uploadUrl": "/api/files.create",
                "form": {"key": "uploads/test/slides.pdf"},
                "attachment": {"id": "attachment-1"},
            }
        }

    def fake_upload_file(**kwargs):
        captured["upload_file"] = kwargs
        return {"ok": True}

    def fake_request(method, endpoint, data=None):
        captured["request"] = {"method": method, "endpoint": endpoint, "data": data}
        return {"ok": True}

    def fake_attachments_delete(attachment_id):
        captured["attachments_delete"] = attachment_id
        return {"ok": True}

    def fake_documents_delete(document_id, permanent=False):
        captured["documents_delete"] = {"id": document_id, "permanent": permanent}
        return {"ok": True}

    client.documents_create = fake_documents_create
    client.attachments_create = fake_attachments_create
    client._upload_file = fake_upload_file
    client._request = fake_request
    client.attachments_delete = fake_attachments_delete
    client.documents_delete = fake_documents_delete

    result = client.documents_import(file=str(source), collection_id="coll-1", publish=False)

    assert result == {"ok": True}
    assert captured["documents_create"]["publish"] is False
    assert captured["attachments_create"]["name"] == "slides.pdf"
    assert captured["attachments_create"]["document_id"] == "placeholder-1"
    assert captured["upload_file"]["file_path"] == source
    assert captured["request"] == {
        "method": "POST",
        "endpoint": "documents.import",
        "data": {
            "attachmentId": "attachment-1",
            "collectionId": "coll-1",
            "publish": False,
        },
    }
    assert captured["attachments_delete"] == "attachment-1"
    assert captured["documents_delete"] == {"id": "placeholder-1", "permanent": False}


def test_documents_import_wraps_unsupported_attachment_import(tmp_path):
    """Unsupported attachment-backed imports should raise a clear validation error."""
    source = tmp_path / "slides.csv"
    source.write_text("a,b\n1,2\n", encoding="utf-8")
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")

    client.documents_create = lambda **kwargs: {"data": {"id": "placeholder-1"}}
    client.attachments_create = lambda **kwargs: {
        "data": {
            "uploadUrl": "/api/files.create",
            "form": {"key": "uploads/test/slides.csv"},
            "attachment": {"id": "attachment-1"},
        }
    }
    client._upload_file = lambda **kwargs: {"ok": True}
    client.attachments_delete = lambda attachment_id: {"ok": True}
    client.documents_delete = lambda document_id, permanent=False: {"ok": True}

    def fake_request(method, endpoint, data=None):
        raise cli.OutlineAPIError("Resource not found", status_code=404)

    client._request = fake_request

    try:
        client.documents_import(file=str(source), collection_id="coll-1")
    except OutlineValidationError as exc:
        assert "supported by the server" in str(exc)
    else:
        raise AssertionError("Expected OutlineValidationError")

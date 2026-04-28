"""CLI smoke tests."""

import json

import pytest

import outline_cli.cli as cli
from outline_cli import OutlineClient, OutlineValidationError
from outline_cli.comment_utils import build_comment_data
from outline_cli.config import ConfigManager


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


def test_main_reads_text_file_for_documents_create(tmp_path, monkeypatch, capsys):
    """`documents create --text-file` should read local text before calling the client."""
    source = tmp_path / "doc.md"
    source.write_text("# Hello\n\nOutline\n", encoding="utf-8")
    captured = {}

    class DummyClient:
        def documents_create(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "documents",
            "create",
            "--title",
            "Doc",
            "--collection-id",
            "coll-1",
            "--text-file",
            str(source),
        ],
    )

    assert cli.main() == 0
    assert captured["text"] == "# Hello\n\nOutline\n"
    capsys.readouterr()


def test_main_rejects_text_and_text_file_together(tmp_path, monkeypatch):
    """`documents create` should reject `--text` together with `--text-file`."""
    source = tmp_path / "doc.md"
    source.write_text("hello\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "documents",
            "create",
            "--title",
            "Doc",
            "--collection-id",
            "coll-1",
            "--text",
            "inline",
            "--text-file",
            str(source),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 2


def test_main_reads_text_file_for_documents_update(tmp_path, monkeypatch, capsys):
    """`documents update --text-file` should read local text before calling the client."""
    source = tmp_path / "doc.md"
    source.write_text("# Updated\n\nOutline\n", encoding="utf-8")
    captured = {}

    class DummyClient:
        def documents_update(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "documents",
            "update",
            "--id",
            "doc-1",
            "--text-file",
            str(source),
        ],
    )

    assert cli.main() == 0
    assert captured["text"] == "# Updated\n\nOutline\n"
    capsys.readouterr()


def test_main_dispatches_documents_create_from_file(monkeypatch, capsys):
    """`documents create-from-file` should pass workflow options to the client."""
    captured = {}

    class DummyClient:
        def documents_create_from_file(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True, "data": {"dryRun": True}}

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "documents",
            "create-from-file",
            "--file",
            "report.md",
            "--collection-id",
            "coll-1",
            "--title",
            "Report",
            "--parent-id",
            "parent-1",
            "--draft",
            "--asset-root",
            "assets",
            "--allow-outside-assets",
            "--upload-local-links",
            "--dry-run",
            "--save-rewritten",
            "rewritten.md",
        ],
    )

    assert cli.main() == 0
    assert captured == {
        "file": "report.md",
        "collection_id": "coll-1",
        "title": "Report",
        "parent_document_id": "parent-1",
        "publish": False,
        "asset_root": "assets",
        "allow_outside_assets": True,
        "upload_local_links": True,
        "dry_run": True,
        "save_rewritten": "rewritten.md",
    }
    capsys.readouterr()


def test_main_dispatches_attachments_upload(monkeypatch, capsys):
    """`attachments upload` should create/upload a local file through the high-level helper."""
    captured = {}

    class DummyClient:
        def attachments_upload_file(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True, "data": {"url": "https://outline.test/file.png"}}

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "attachments",
            "upload",
            "--file",
            "figure.png",
            "--document-id",
            "doc-1",
            "--name",
            "Figure.png",
            "--content-type",
            "image/png",
            "--preset",
            "documentAttachment",
        ],
    )

    assert cli.main() == 0
    assert captured == {
        "document_id": "doc-1",
        "file_path": "figure.png",
        "name": "Figure.png",
        "content_type": "image/png",
        "preset": "documentAttachment",
    }
    capsys.readouterr()


def test_main_reads_data_file_for_comments_create(tmp_path, monkeypatch, capsys):
    """`comments create --data-file` should read Markdown text from a local file."""
    source = tmp_path / "comment.md"
    source.write_text("Comment from file\n", encoding="utf-8")
    captured = {}

    class DummyClient:
        def comments_create_markdown(self, **kwargs):
            captured.update(kwargs)
            return [{"ok": True}]

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "comments",
            "create",
            "--document-id",
            "doc-1",
            "--data-file",
            str(source),
        ],
    )

    assert cli.main() == 0
    assert captured["text"] == "Comment from file\n"
    capsys.readouterr()


def test_main_reads_data_file_for_comments_update(tmp_path, monkeypatch, capsys):
    """`comments update --data-file` should read Markdown text from a local file."""
    source = tmp_path / "comment.md"
    source.write_text("Updated comment\n", encoding="utf-8")
    captured = {}

    class DummyClient:
        def comments_update(self, **kwargs):
            captured.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "comments",
            "update",
            "--id",
            "comment-1",
            "--data-file",
            str(source),
        ],
    )

    assert cli.main() == 0
    assert captured["data"] == build_comment_data("Updated comment\n")
    capsys.readouterr()


def test_default_output_summarizes_noisy_auth_info(monkeypatch, capsys):
    """Default CLI output should be compact, structured JSON with raw-output guidance."""

    class DummyClient:
        def auth_info(self):
            return {
                "ok": True,
                "data": {
                    "user": {
                        "id": "user-1",
                        "name": "Agent",
                        "email": "agent@example.com",
                        "role": "member",
                        "preferences": {"very": "large"},
                    },
                    "team": {"id": "team-1", "name": "Team", "url": "https://outline.test"},
                    "collaborationToken": "secret-token",
                    "groups": [{"id": "group-1", "name": "Engineering", "memberships": ["large"]}],
                },
                "policies": [{"id": "policy-1"}],
            }

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr("sys.argv", ["outline-cli", "--api-key", "ol_api_test", "auth", "info"])

    assert cli.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["_meta"]["output"] == "summary"
    assert "--raw" in output["_meta"]["rawHint"]
    assert output["user"] == {
        "id": "user-1",
        "name": "Agent",
        "email": "agent@example.com",
        "role": "member",
    }
    assert output["team"]["name"] == "Team"
    assert "collaborationToken" not in output
    assert "policies" not in output


def test_raw_output_passthrough_after_subcommand(monkeypatch, capsys):
    """`--raw` should work after nested subcommands and preserve the API response."""
    raw_result = {"ok": True, "data": {"collaborationToken": "secret-token"}, "policies": [{"id": "p1"}]}

    class DummyClient:
        def auth_info(self):
            return raw_result

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr("sys.argv", ["outline-cli", "--api-key", "ol_api_test", "auth", "info", "--raw"])

    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out) == raw_result


def test_document_info_summary_truncates_text_with_limit(monkeypatch, capsys):
    """Document summaries should include bounded text previews by default."""

    class DummyClient:
        def documents_info(self, id):
            return {
                "ok": True,
                "data": {
                    "id": id,
                    "title": "Long Doc",
                    "url": "/doc/long",
                    "collectionId": "coll-1",
                    "text": "abcdefghijklmnopqrstuvwxyz",
                },
            }

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        [
            "outline-cli",
            "--api-key",
            "ol_api_test",
            "documents",
            "info",
            "--id",
            "doc-1",
            "--max-text-chars",
            "5",
        ],
    )

    assert cli.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["document"]["textPreview"] == "abcde"
    assert output["document"]["textLength"] == 26
    assert output["document"]["textTruncated"] is True


def test_api_error_output_includes_hint_and_context(monkeypatch, capsys):
    """API failures should print actionable diagnostics to stderr."""

    class DummyClient:
        def documents_info(self, id):
            raise cli.OutlineAPIError(
                "HTTP 404: Not Found",
                status_code=404,
                endpoint="documents.info",
                url="https://outline.test/documents.info",
                hint="The configured base URL does not end with /api.",
            )

    monkeypatch.setattr(cli, "OutlineClient", lambda **kwargs: DummyClient())
    monkeypatch.setattr(
        "sys.argv",
        ["outline-cli", "--api-key", "ol_api_test", "documents", "info", "--id", "doc-1"],
    )

    assert cli.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Outline API request failed" in captured.err
    assert "HTTP: 404" in captured.err
    assert "Endpoint: documents.info" in captured.err
    assert "Hint: The configured base URL" in captured.err


def test_invalid_config_warning_goes_to_stderr(tmp_path, capsys):
    """Malformed config warnings must not corrupt JSON stdout."""
    path = tmp_path / "config.json"
    path.write_text("not json", encoding="utf-8")

    assert ConfigManager._load_from_file(path) is None
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Warning: Failed to load config" in captured.err

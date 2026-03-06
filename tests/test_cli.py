"""CLI smoke tests."""

import outline_cli.cli as cli


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

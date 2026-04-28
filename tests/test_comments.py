"""Tests for comment markdown rendering and chunking helpers."""

from __future__ import annotations

import argparse
import json

import outline_cli.cli as cli
from outline_cli import OutlineClient
from outline_cli.comment_utils import build_comment_data, prepare_comment_chunks, split_comment_text


def test_build_comment_data_uses_paragraphs_for_multiple_lines() -> None:
    result = build_comment_data("First line\n\nSecond line")

    assert result == {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "First line"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": "Second line"}]},
        ],
    }


def test_split_comment_text_keeps_ordered_list_items_intact_when_splitting_markdown() -> None:
    points = [
        (
            f"{index}. **Point{index}** Boundary {index} keeps agent tool execution scoped and safe. "
            "It prevents unsafe retries."
        )
        for index in range(1, 13)
    ]
    text = "Sure, here is a numbered summary:\n\n" + "\n".join(points)

    chunks = split_comment_text(text, max_chars=1000)

    assert len(chunks) == 2
    assert chunks[0].startswith("Sure, here is a numbered summary:\n\n1. **Point1**")
    assert "\n9. **Point9**" in chunks[0]
    assert "\n10. **Point10**" not in chunks[0]
    assert chunks[1].startswith("10. **Point10**")
    assert "\n12. **Point12**" in chunks[1]
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_prepare_comment_chunks_numbers_split_markdown_reply() -> None:
    points = [
        (
            f"{index}. **Point{index}** Boundary {index} keeps agent tool execution scoped and safe. "
            "It prevents unsafe retries."
        )
        for index in range(1, 13)
    ]
    text = "Sure, here is a numbered summary:\n\n" + "\n".join(points)

    chunks = prepare_comment_chunks(text, max_chars=1000)

    assert len(chunks) == 2
    assert chunks[0].startswith("[1/2]\n\nSure, here is a numbered summary:\n\n1. **Point1**")
    assert chunks[1].startswith("[2/2]\n\n10. **Point10**")
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_comments_create_markdown_uses_text_payload_and_auto_splits() -> None:
    client = OutlineClient(api_key="ol_api_test", base_url="https://example.com/api")
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    def fake_request(method: str, endpoint: str, data=None):
        calls.append((method, endpoint, data))
        return {"ok": True, "data": {"id": f"comment-{len(calls)}"}}

    client._request = fake_request  # type: ignore[method-assign]

    points = [
        (
            f"{index}. **Point{index}** Boundary {index} keeps agent tool execution scoped and safe. "
            "It prevents unsafe retries."
        )
        for index in range(1, 13)
    ]
    text = "Sure, here is a numbered summary:\n\n" + "\n".join(points)

    results = client.comments_create_markdown(document_id="doc-1", text=text, parent_comment_id="root-1")

    assert [result["data"]["id"] for result in results] == ["comment-1", "comment-2"]
    assert len(calls) == 2
    for method, endpoint, payload in calls:
        assert method == "POST"
        assert endpoint == "comments.create"
        assert payload is not None
        assert payload["documentId"] == "doc-1"
        assert payload["parentCommentId"] == "root-1"
        assert "text" in payload
        assert "data" not in payload
    assert calls[0][2]["text"].startswith("[1/2]\n\nSure, here is a numbered summary:")
    assert calls[1][2]["text"].startswith("[2/2]\n\n10. **Point10**")


def test_cli_create_comment_prints_split_summary(capsys) -> None:
    class DummyClient:
        def comments_create_markdown(self, document_id: str, text: str, parent_comment_id: str | None = None):
            assert document_id == "doc-1"
            assert text == "hello"
            assert parent_comment_id == "root-1"
            return [{"data": {"id": "comment-1"}}, {"data": {"id": "comment-2"}}]

    args = argparse.Namespace(
        document_id="doc-1",
        data="hello",
        parent_id="root-1",
        command="comments",
        subcommand="create",
    )

    assert cli.create_comment(DummyClient(), args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["_meta"]["command"] == "comments.create"
    assert payload["split"] is True
    assert payload["chunkCount"] == 2
    assert payload["results"] == [{"id": "comment-1"}, {"id": "comment-2"}]

"""Test incremental syncs."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from tap_meltano_cloud.tap import TapMeltanoCloud

if TYPE_CHECKING:
    import pytest


def test_jobs_since_bookmark() -> None:
    """Request only the jobs changed since the bookmark, by last status change."""
    queries: list[dict[str, list[str]]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            queries.append(parse_qs(urlparse(self.path).query))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"page": {"number": 0, "totalPages": 1}}).encode())

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        tap = TapMeltanoCloud(
            config={
                "auth_token": "token",
                "api_url": f"http://127.0.0.1:{server.server_port}",
                "workspace_ids": ["workspace"],
            },
            state={
                "bookmarks": {
                    "jobs": {
                        "partitions": [
                            {
                                "context": {"workspaceId": "workspace"},
                                "replication_key": "lastStatusChange",
                                "replication_key_value": "2026-10-01T00:00:00",
                            },
                        ],
                    },
                },
            },
        )
        tap.streams["jobs"].sync()
    finally:
        server.shutdown()
        server.server_close()

    assert queries == [
        {
            "size": ["50"],
            "since": ["2026-10-01T00:00:00+00:00"],
            "sort": ["lastStatusChange,asc"],
        },
    ]


def test_pipeline_jobs_since_last_status_change(capsys: pytest.CaptureFixture[str]) -> None:
    """Request pipeline jobs by last status change, and bookmark the latest change."""
    queries: dict[str, dict[str, list[str]]] = {}
    jobs = [
        {"id": "job-1", "lastStatusChange": "2026-10-02T00:00:00"},
        {"id": "job-2", "lastStatusChange": "2026-10-03T00:00:00"},
    ]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlparse(self.path)
            queries[url.path] = parse_qs(url.query)
            if url.path.endswith("/metrics"):
                self.send_response(204)
                self.end_headers()
                return
            embedded = {"pipelines": [{"id": "pipeline"}], "jobs": jobs}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            body = {"_embedded": embedded, "page": {"number": 0, "totalPages": 1}}
            self.wfile.write(json.dumps(body).encode())

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        tap = TapMeltanoCloud(
            config={
                "auth_token": "token",
                "api_url": f"http://127.0.0.1:{server.server_port}",
                "workspace_ids": ["workspace"],
            },
            state={
                "bookmarks": {
                    "pipeline_jobs": {
                        "partitions": [
                            {
                                "context": {"pipelineId": "pipeline", "workspaceId": "workspace"},
                                "replication_key": "lastStatusChange",
                                "replication_key_value": "2026-10-01T00:00:00",
                            },
                        ],
                    },
                },
            },
        )
        tap.streams["pipelines"].sync()
    finally:
        server.shutdown()
        server.server_close()

    assert queries["/pipelines/pipeline/jobs"] == {
        "size": ["50"],
        "since": ["2026-10-01T00:00:00+00:00"],
        "sort": ["lastStatusChange,asc"],
    }
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    state = next(m for m in reversed(messages) if m["type"] == "STATE")["value"]
    [partition] = state["bookmarks"]["pipeline_jobs"]["partitions"]
    assert partition["replication_key"] == "lastStatusChange"
    assert partition["replication_key_value"] == "2026-10-03T00:00:00"

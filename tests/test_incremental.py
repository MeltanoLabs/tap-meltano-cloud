"""Test incremental syncs."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from tap_meltano_cloud.tap import TapMeltanoCloud


def test_jobs_since_bookmark() -> None:
    """Request only the jobs created since the bookmark."""
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
                                "replication_key": "created",
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

    assert queries == [{"size": ["50"], "since": ["2026-10-01T00:00:00+00:00"]}]

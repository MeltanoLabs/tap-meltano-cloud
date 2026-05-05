"""Test schema evolution."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from syrupy.extensions.json import JSONSnapshotExtension

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from syrupy.assertion import SnapshotAssertion


def test_catalog_changes(
    pytester: pytest.Pytester,
    snapshot: SnapshotAssertion,
    subtests: pytest.Subtests,
    tmp_path: Path,
) -> None:
    """Fail if the catalog has changed."""
    snapshot_json = snapshot.with_defaults(extension_class=JSONSnapshotExtension)
    config = tmp_path / "config.json"
    config.write_text('{"workspace_ids": ["123"]}')
    result = pytester.run(
        "tap-meltano-cloud",
        "--discover",
        "--config",
        config.as_posix(),
    )
    assert result.ret == 0, "Tap discovery failed"

    catalog = json.loads("".join(result.outlines))
    for stream in catalog["streams"]:
        stream_id = stream["tap_stream_id"]
        with subtests.test(stream_id):
            assert snapshot_json(name=stream_id) == stream

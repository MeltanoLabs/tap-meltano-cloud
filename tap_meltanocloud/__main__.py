"""MeltanoCloud entry point."""

from __future__ import annotations

from tap_meltanocloud.tap import TapMeltanoCloud

TapMeltanoCloud.cli()

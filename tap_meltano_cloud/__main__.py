"""MeltanoCloud entry point."""

from __future__ import annotations

from tap_meltano_cloud.tap import TapMeltanoCloud

TapMeltanoCloud.cli()

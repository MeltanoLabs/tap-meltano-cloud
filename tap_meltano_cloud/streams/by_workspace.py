"""Streams for accessing data for one or more specific workspaces."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from . import base

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class _ByWorkspaceStream(base.MeltanoCloudStream):
    """Base class for workspace-scoped streams driven by explicit workspace IDs.

    Each workspace ID becomes a partition, so one request is made per workspace
    without requiring the workspaces list endpoint.
    """

    def __init__(self, *args: Any, workspace_ids: list[str], **kwargs: Any) -> None:
        """Initialize the stream with workspace ID partitions."""
        super().__init__(*args, **kwargs)
        self._partitions = [{"workspaceId": wid} for wid in workspace_ids]

    @property
    @override
    def partitions(self) -> list[dict]:
        return self._partitions


class WorkspacesStream(_ByWorkspaceStream):
    """Fetches individual workspaces by ID."""

    name = "workspaces"
    path = "/workspaces/{workspaceId}"
    records_jsonpath = "$"
    schema = base.WorkspaceSchema(base.OPENAPI_SCHEMA, key="WorkspaceResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("deploymentSecret", None)
        row.pop("sshPrivateKey", None)
        return super().post_process(row, context)


class PipelinesStream(base.PipelinesMixin, _ByWorkspaceStream):
    """Pipelines stream."""


class PipelineJobsStream(base.PipelineJobsMixin, _ByWorkspaceStream):
    """Pipeline jobs stream."""

    parent_stream_type = PipelinesStream


class PipelineMetricsStream(base.PipelineMetricsMixin, _ByWorkspaceStream):
    """Pipeline metrics stream."""

    parent_stream_type = PipelinesStream


class DatasetsStream(base.DatasetsMixin, _ByWorkspaceStream):
    """Datasets stream."""


class JobsStream(base.JobsMixin, _ByWorkspaceStream):
    """Jobs stream."""


class ChannelsStream(base.ChannelsMixin, _ByWorkspaceStream):
    """Channels stream."""


class DataStoresStream(base.DataStoresMixin, _ByWorkspaceStream):
    """Data stores stream."""


class DataComponentsStream(base.DataComponentsMixin, _ByWorkspaceStream):
    """Data components stream."""

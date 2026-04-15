"""Streams for accessing data for one or more specific workspaces."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from singer_sdk import StreamSchema

from .base import OPENAPI_SCHEMA, MeltanoCloudStream, _PipelineSchema, _WorkspaceChildSchema

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class _ByWorkspaceStream(MeltanoCloudStream):
    """Base class for workspace-scoped streams driven by explicit workspace IDs.

    Each workspace ID becomes a partition, so one request is made per workspace
    without requiring the workspaces list endpoint.
    """

    def __init__(self, *args: Any, workspace_ids: list[str], **kwargs: Any) -> None:
        """Initialize the stream with workspace ID partitions."""
        super().__init__(*args, **kwargs)
        self._partitions = [{"workspaceId": wid} for wid in workspace_ids]


class WorkspacesStream(_ByWorkspaceStream):
    """Fetches individual workspaces by ID."""

    name = "workspaces"
    path = "/workspaces/{workspaceId}"
    records_jsonpath = "$"
    schema = StreamSchema(OPENAPI_SCHEMA, key="WorkspaceResource")


class PipelinesStream(_ByWorkspaceStream):
    """Pipelines stream."""

    name = "pipelines"
    path = "/workspaces/{workspaceId}/pipelines"
    records_jsonpath = "$._embedded.pipelines[*]"
    schema = _PipelineSchema(OPENAPI_SCHEMA, key="PipelineResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("properties", None)
        return super().post_process(row, context)


class DatasetsStream(_ByWorkspaceStream):
    """Datasets stream."""

    name = "datasets"
    path = "/workspaces/{workspaceId}/datasets"
    records_jsonpath = "$._embedded.datasets[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DatasetResource")


class JobsStream(_ByWorkspaceStream):
    """Jobs stream."""

    name = "jobs"
    path = "/workspaces/{workspaceId}/jobs"
    records_jsonpath = "$._embedded.jobs[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="JobResource")


class ChannelsStream(_ByWorkspaceStream):
    """Channels stream."""

    name = "channels"
    path = "/workspaces/{workspaceId}/channels"
    records_jsonpath = "$._embedded.channels[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="ChannelResource")


class DataStoresStream(_ByWorkspaceStream):
    """Data stores stream."""

    name = "datastores"
    path = "/workspaces/{workspaceId}/datastores"
    records_jsonpath = "$._embedded.datastores[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DataStoreResource")


class DataComponentsStream(_ByWorkspaceStream):
    """Data components stream."""

    name = "datacomponents"
    path = "/workspaces/{workspaceId}/datacomponents"
    records_jsonpath = "$._embedded.datacomponents[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DataComponentResource")

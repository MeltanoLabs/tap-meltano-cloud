"""Streams for accessing all data the token owner has access to."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from .base import (
    OPENAPI_SCHEMA,
    MeltanoCloudStream,
    _DataComponentSchema,
    _DataStoreSchema,
    _PipelineSchema,
    _WorkspaceChildSchema,
    _WorkspaceSchema,
)

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator

    from singer_sdk.helpers.types import Context


class WorkspacesStream(MeltanoCloudStream):
    """Workspaces stream."""

    name = "workspaces"
    path = "/workspaces"
    records_jsonpath = "$._embedded.workspaces[*]"
    schema = _WorkspaceSchema(OPENAPI_SCHEMA, key="WorkspaceResource")

    @override
    def generate_child_contexts(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> Generator[Context | None, None, None]:
        """Generate child contexts for workspace-scoped streams."""
        yield {"workspaceId": record["id"]}

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("deploymentSecret", None)
        row.pop("sshPrivateKey", None)
        return super().post_process(row, context)


class _WorkspaceChildStream(MeltanoCloudStream):
    """Base class for workspace-child streams driven by the me WorkspacesStream."""

    parent_stream_type = WorkspacesStream


class PipelinesStream(_WorkspaceChildStream):
    """Pipelines stream."""

    name = "pipelines"
    path = "/workspaces/{workspaceId}/pipelines"
    records_jsonpath = "$._embedded.pipelines[*]"
    schema = _PipelineSchema(OPENAPI_SCHEMA, key="PipelineResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("properties", None)
        return super().post_process(row, context)


class DatasetsStream(_WorkspaceChildStream):
    """Datasets stream."""

    name = "datasets"
    path = "/workspaces/{workspaceId}/datasets"
    records_jsonpath = "$._embedded.datasets[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DatasetResource")


class JobsStream(_WorkspaceChildStream):
    """Jobs stream."""

    name = "jobs"
    path = "/workspaces/{workspaceId}/jobs"
    records_jsonpath = "$._embedded.jobs[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="JobResource")


class ChannelsStream(_WorkspaceChildStream):
    """Channels stream."""

    name = "channels"
    path = "/workspaces/{workspaceId}/channels"
    records_jsonpath = "$._embedded.channels[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="ChannelResource")


class DataStoresStream(_WorkspaceChildStream):
    """Data stores stream."""

    name = "datastores"
    path = "/workspaces/{workspaceId}/datastores"
    records_jsonpath = "$._embedded.datastores[*]"
    schema = _DataStoreSchema(OPENAPI_SCHEMA, key="DataStoreResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("jdbcUrl", None)
        row.pop("properties", None)
        return super().post_process(row, context)


class DataComponentsStream(_WorkspaceChildStream):
    """Data components stream."""

    name = "datacomponents"
    path = "/workspaces/{workspaceId}/datacomponents"
    records_jsonpath = "$._embedded.datacomponents[*]"
    schema = _DataComponentSchema(OPENAPI_SCHEMA, key="DataComponentResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("properties", None)
        return super().post_process(row, context)

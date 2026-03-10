"""Stream type classes for tap-meltano-cloud."""

from __future__ import annotations

import sys
from importlib import resources
from typing import TYPE_CHECKING, Any

from singer_sdk import OpenAPISchema, StreamSchema

from tap_meltano_cloud import openapi
from tap_meltano_cloud.client import MeltanoCloudStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator

    from singer_sdk.helpers.types import Context


OPENAPI_SCHEMA = OpenAPISchema(resources.files(openapi) / "openapi.json")


class WorkspacesStream(MeltanoCloudStream):
    """Workspaces stream."""

    name = "workspaces"
    path = "/workspaces"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.workspaces[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="WorkspaceResource")

    @override
    def generate_child_contexts(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> Generator[Context | None, None, None]:
        """Generate child contexts for workspace-scoped streams."""
        yield {"workspaceId": record["id"]}


class _WorkspaceChildStream(MeltanoCloudStream):
    """Base class for all streams that have `workspaces` as parent."""

    parent_stream_type = WorkspacesStream


class _WorkspaceChildSchema(StreamSchema[str]):
    """Schema for all workspace-scoped streams."""

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"]["workspaceId"] = {
            "format": "uuid",
            "type": ["string", "null"],
        }
        return schema


class PipelinesStream(_WorkspaceChildStream):
    """Pipelines stream."""

    name = "pipelines"
    path = "/workspaces/{workspaceId}/pipelines"
    records_jsonpath = "$._embedded.pipelines[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="PipelineResource")


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
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DataStoreResource")


class DataComponentsStream(_WorkspaceChildStream):
    """Data components stream."""

    name = "datacomponents"
    path = "/workspaces/{workspaceId}/datacomponents"
    records_jsonpath = "$._embedded.datacomponents[*]"
    schema = _WorkspaceChildSchema(OPENAPI_SCHEMA, key="DataComponentResource")

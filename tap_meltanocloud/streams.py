"""Stream type classes for tap-meltanocloud."""

from __future__ import annotations

import sys
from importlib import resources
from typing import TYPE_CHECKING, Any

from singer_sdk import OpenAPISchema, StreamSchema

from tap_meltanocloud import openapi
from tap_meltanocloud.client import MeltanoCloudStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


OPENAPI_SCHEMA = OpenAPISchema(resources.files(openapi) / "openapi.json")


class WorkspacesStream(MeltanoCloudStream):
    """Workspaces stream."""

    name = "workspaces"
    path = "/workspaces/{workspace_id}"
    primary_keys = ("id",)
    records_jsonpath = "$"
    schema = StreamSchema(OPENAPI_SCHEMA, key="WorkspaceResource")

    @property
    @override
    def partitions(self) -> list[dict]:
        """Return a list of partition contexts from configured project IDs."""
        return [{"workspace_id": wid} for wid in self.config["workspace_ids"]]

    @override
    def generate_child_contexts(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> list[Context | None]:
        """Generate child contexts for workspace-scoped streams."""
        yield {"workspace_id": record["id"]}


class PipelinesStream(MeltanoCloudStream):
    """Pipelines stream."""

    name = "pipelines"
    path = "/workspaces/{workspace_id}/pipelines"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.pipelines[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="PipelineResource")
    parent_stream_type = WorkspacesStream


class DatasetsStream(MeltanoCloudStream):
    """Datasets stream."""

    name = "datasets"
    path = "/workspaces/{workspace_id}/datasets"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.datasets[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="DatasetResource")
    parent_stream_type = WorkspacesStream


class JobsStream(MeltanoCloudStream):
    """Jobs stream."""

    name = "jobs"
    path = "/workspaces/{workspace_id}/jobs"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.jobs[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="JobResource")
    parent_stream_type = WorkspacesStream


class ChannelsStream(MeltanoCloudStream):
    """Channels stream."""

    name = "channels"
    path = "/workspaces/{workspace_id}/channels"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.channels[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="ChannelResource")
    parent_stream_type = WorkspacesStream


class DataStoresStream(MeltanoCloudStream):
    """Data stores stream."""

    name = "datastores"
    path = "/workspaces/{workspace_id}/datastores"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.datastores[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="DataStoreResource")
    parent_stream_type = WorkspacesStream


class DataComponentsStream(MeltanoCloudStream):
    """Data components stream."""

    name = "datacomponents"
    path = "/workspaces/{workspace_id}/datacomponents"
    primary_keys = ("id",)
    records_jsonpath = "$._embedded.datacomponents[*]"
    schema = StreamSchema(OPENAPI_SCHEMA, key="DataComponentResource")
    parent_stream_type = WorkspacesStream

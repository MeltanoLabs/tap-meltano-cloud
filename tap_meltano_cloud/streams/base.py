"""Stream type classes for tap-meltano-cloud."""

from __future__ import annotations

import http
import sys
from importlib import resources
from typing import TYPE_CHECKING, Any

import singer_sdk.typing as th
from singer_sdk import OpenAPISchema, Stream, StreamSchema
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator, SinglePagePaginator
from singer_sdk.streams import RESTStream

from tap_meltano_cloud import openapi

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from urllib.parse import ParseResult

    import requests
    from singer_sdk.helpers.types import Context, Record
    from singer_sdk.pagination import BaseAPIPaginator
    from singer_sdk.streams.rest import HTTPRequest, PageContext

OPENAPI_SCHEMA = OpenAPISchema(resources.files(openapi) / "openapi.json")


class MeltanoCloudPaginator(BaseHATEOASPaginator):
    """Paginator for MeltanoCloud Spring HATEOAS paged responses.

    Follows the ``_links.next.href`` URL, but stops on the last page according to
    the current response's ``page`` metadata, or when a page has no records. Some
    endpoints report inconsistent totals across pages, so the ``next`` link alone
    is not a reliable stop condition.
    """

    @override
    def get_next_url(self, response: requests.Response) -> str | None:
        data = response.json()
        if not isinstance(data, dict) or not data.get("_embedded"):
            return None

        page = data.get("page")
        if page and page.get("number", 0) >= page.get("totalPages", 1) - 1:
            return None

        next_url = data.get("_links", {}).get("next", {}).get("href")
        if next_url == response.url:
            return None
        return next_url


class MeltanoCloudStream(RESTStream[Any]):
    """MeltanoCloud stream class."""

    page_size = 50

    records_jsonpath = "$[*]"

    @property
    @override
    def primary_keys(self) -> Sequence[str]:
        return ("id",)

    @primary_keys.setter
    @override
    def primary_keys(self, new_value: Sequence[str]) -> None:
        self._primary_keys = new_value

    @property
    @override
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @property
    @override
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator(token=self.config["auth_token"])

    @override
    def get_new_paginator(self) -> BaseAPIPaginator | None:
        """Return a new paginator instance."""
        return MeltanoCloudPaginator()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Request a larger first page; subsequent pages use the ``next`` URL."""
        return {"size": self.page_size}

    @override
    def get_http_request(self, *, page: PageContext) -> HTTPRequest:
        """Request the HATEOAS ``next`` URL as-is when paginating."""
        request = super().get_http_request(page=page)
        if page.next_page_token:
            request.url = page.next_page_token.geturl()
            request.params = {}
        return request


class WorkspaceChildSchema(StreamSchema[str]):
    """Schema for all workspace-scoped streams."""

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"]["workspaceId"] = {
            "format": "uuid",
            "type": "string",
        }
        return schema


class WorkspaceSchema(StreamSchema[str]):
    """Schema for workspace streams — excludes sensitive fields.

    ``deploymentSecret`` and ``sshPrivateKey`` can contain sensitive credentials,
    so they are omitted until a reliable obfuscation mechanism exists.
    See https://github.com/MeltanoLabs/tap-meltano-cloud/issues/15
    """

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"].pop("deploymentSecret", None)
        schema["properties"].pop("sshPrivateKey", None)
        return schema


class PipelineSchema(WorkspaceChildSchema):
    """Schema for pipeline streams — excludes the ``properties`` field.

    Pipeline properties can contain sensitive data and there is currently no
    reliable way to obfuscate them, so the field is omitted until that
    capability exists.  See https://github.com/MeltanoLabs/tap-meltano-cloud/issues/15
    """

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"].pop("properties", None)
        return schema


class PipelineJobSchema(WorkspaceChildSchema):
    """Schema for pipeline job streams."""

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"]["pipelineId"] = {
            "format": "uuid",
            "type": "string",
        }
        return schema


class DataComponentSchema(WorkspaceChildSchema):
    """Schema for data component streams — excludes the ``properties`` field.

    Data component properties can contain sensitive data and there is currently no
    reliable way to obfuscate them, so the field is omitted until that
    capability exists.  See https://github.com/MeltanoLabs/tap-meltano-cloud/issues/15
    """

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"].pop("properties", None)
        return schema


class DataStoreSchema(WorkspaceChildSchema):
    """Schema for data store streams — excludes sensitive fields.

    ``properties`` and ``jdbcUrl`` can contain sensitive data (credentials,
    connection strings), so they are omitted until a reliable obfuscation
    mechanism exists.  See https://github.com/MeltanoLabs/tap-meltano-cloud/issues/15
    """

    @override
    def get_stream_schema(self, *args: Any, **kwargs: Any) -> dict:
        schema = super().get_stream_schema(*args, **kwargs)
        schema["properties"].pop("jdbcUrl", None)
        schema["properties"].pop("properties", None)
        return schema


class PipelinesMixin(Stream):
    """Shared logic for pipelines streams across both workspace-access modes."""

    name = "pipelines"
    path = "/workspaces/{workspaceId}/pipelines"
    records_jsonpath = "$._embedded.pipelines[*]"
    schema = PipelineSchema(OPENAPI_SCHEMA, key="PipelineResource")

    def get_new_paginator(self) -> BaseAPIPaginator | None:
        """Return a single-page paginator.

        This endpoint ignores paging parameters and returns every pipeline on each
        page, while its ``page`` metadata and ``next`` links keep advancing. Following
        them would emit the same pipelines repeatedly.
        See https://github.com/MeltanoLabs/tap-meltano-cloud/issues/1
        """
        return SinglePagePaginator()

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the pipeline record."""
        row.pop("properties", None)
        row.pop("_embedded", None)
        return super().post_process(row, context)

    @override
    def get_child_context(self, record: dict, context: Context | None = None) -> dict:
        """Get child context for a pipeline record."""
        return {
            "pipelineId": record["id"],
            "workspaceId": context["workspaceId"] if context else None,
        }


class PipelineJobsMixin(Stream):
    """Shared logic for pipeline jobs streams across both workspace-access modes."""

    name = "pipeline_jobs"
    path = "/pipelines/{pipelineId}/jobs"
    records_jsonpath = "$._embedded.jobs[*]"
    schema = PipelineJobSchema(OPENAPI_SCHEMA, key="JobResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the pipeline job record."""
        row.pop("_embedded", None)
        return super().post_process(row, context)


class PipelineMetricsMixin(Stream):
    """Shared logic for pipeline metrics streams across both workspace-access modes."""

    name = "pipeline_metrics"
    path = "/pipelines/{pipelineId}/metrics"

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse pipeline metrics."""
        if response.status_code == http.HTTPStatus.NO_CONTENT:
            return []
        return response.json()

    @property
    def schema(self) -> dict:
        """Get the schema for pipeline metrics."""
        return th.PropertiesList(
            th.Property("workspaceId", th.StringType),
            th.Property("pipelineId", th.StringType),
            th.Property("job_created_at", th.DateTimeType),
            th.Property("value", th.DecimalType),
        ).to_dict()

    @override
    def post_process(self, row: Record, context: Context | None = None) -> Record | None:
        row["job_created_at"] = row.pop("metrics.job-created")
        row["value"] = row.pop("metrics.value")
        return super().post_process(row, context)

    @property
    def primary_keys(self) -> Sequence[str]:
        """Get the primary keys for pipeline metrics."""
        return ("pipelineId", "job_created_at")

    @primary_keys.setter
    def primary_keys(self, new_value: Sequence[str]) -> None:
        self._primary_keys = new_value


class DatasetsMixin(Stream):
    """Shared logic for datasets streams across both workspace-access modes."""

    name = "datasets"
    path = "/workspaces/{workspaceId}/datasets"
    records_jsonpath = "$._embedded.datasets[*]"
    schema = WorkspaceChildSchema(OPENAPI_SCHEMA, key="DatasetResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the dataset record."""
        row.pop("_embedded", None)
        return super().post_process(row, context)


class JobsMixin(Stream):
    """Shared logic for jobs streams across both workspace-access modes."""

    name = "jobs"
    path = "/workspaces/{workspaceId}/jobs"
    records_jsonpath = "$._embedded.jobs[*]"
    schema = WorkspaceChildSchema(OPENAPI_SCHEMA, key="JobResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the job record."""
        row.pop("_embedded", None)
        return super().post_process(row, context)


class ChannelsMixin(Stream):
    """Shared logic for channels streams across both workspace-access modes."""

    name = "channels"
    path = "/workspaces/{workspaceId}/channels"
    records_jsonpath = "$._embedded.channels[*]"
    schema = WorkspaceChildSchema(OPENAPI_SCHEMA, key="ChannelResource")


class DataStoresMixin(Stream):
    """Shared logic for data stores streams across both workspace-access modes."""

    name = "datastores"
    path = "/workspaces/{workspaceId}/datastores"
    records_jsonpath = "$._embedded.datastores[*]"
    schema = DataStoreSchema(OPENAPI_SCHEMA, key="DataStoreResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the data store record."""
        row.pop("jdbcUrl", None)
        row.pop("properties", None)
        return super().post_process(row, context)


class DataComponentsMixin(Stream):
    """Shared logic for data components streams across both workspace-access modes."""

    name = "datacomponents"
    path = "/workspaces/{workspaceId}/datacomponents"
    records_jsonpath = "$._embedded.datacomponents[*]"
    schema = DataComponentSchema(OPENAPI_SCHEMA, key="DataComponentResource")

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Update the data component record."""
        row.pop("properties", None)
        row.pop("_embedded", None)
        return super().post_process(row, context)

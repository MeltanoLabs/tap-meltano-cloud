"""Stream type classes for tap-meltano-cloud."""

from __future__ import annotations

import sys
from importlib import resources
from typing import TYPE_CHECKING, Any

from singer_sdk import OpenAPISchema, StreamSchema
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

from tap_meltano_cloud import openapi

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    import requests
    from singer_sdk.pagination import BaseAPIPaginator

OPENAPI_SCHEMA = OpenAPISchema(resources.files(openapi) / "openapi.json")


# TODO(tap-meltano-cloud): Enable pagination when the API supports it correctly
# https://github.com/MeltanoLabs/tap-meltano-cloud/issues/1
class MeltanoCloudPaginator(BaseHATEOASPaginator):
    """Paginator for MeltanoCloud Spring HATEOAS paged responses."""

    @override
    def get_next_url(self, response: requests.Response) -> str | None:
        return response.json().get("_links", {}).get("next", {}).get("href")


class MeltanoCloudStream(RESTStream[Any]):
    """MeltanoCloud stream class."""

    # TODO(tap-meltano-cloud): Enable pagination when the API supports it correctly
    # https://github.com/MeltanoLabs/tap-meltano-cloud/issues/1
    page_size = 50

    primary_keys = ("id",)
    records_jsonpath = "$[*]"

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
        # TODO(tap-meltano-cloud): Enable pagination when the API supports it correctly
        # https://github.com/MeltanoLabs/tap-meltano-cloud/issues/1
        return None


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

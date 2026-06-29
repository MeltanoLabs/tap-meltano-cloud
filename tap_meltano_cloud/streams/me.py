"""Streams for accessing all data the token owner has access to."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from . import base

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator

    from singer_sdk.helpers.types import Context


class AccountsStream(base.AccountsMixin, base.MeltanoCloudStream):
    """Accounts stream — top-level parent for workspaces."""

    @override
    def get_child_context(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> dict[str, Any]:
        """Pass accountId down to child WorkspacesStream."""
        return {"accountId": record["id"]}


class WorkspacesStream(base.MeltanoCloudStream):
    """Workspaces stream — child of AccountsStream."""

    name = "workspaces"
    path = "/accounts/{accountId}/workspaces"
    records_jsonpath = "$._embedded.workspaces[*]"
    schema = base.WorkspaceSchema(base.OPENAPI_SCHEMA, key="WorkspaceResource")
    parent_stream_type = AccountsStream

    @override
    def generate_child_contexts(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> Generator[Context | None, None, None]:
        """Generate child contexts for workspace-scoped streams."""
        yield {"workspaceId": record["id"], "accountId": context["accountId"] if context else None}

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row.pop("deploymentSecret", None)
        row.pop("sshPrivateKey", None)
        row["accountId"] = context["accountId"] if context else None
        return super().post_process(row, context)


class _WorkspaceChildStream(base.MeltanoCloudStream):
    """Base class for workspace-child streams driven by the me WorkspacesStream."""

    parent_stream_type = WorkspacesStream


class PipelinesStream(base.PipelinesMixin, _WorkspaceChildStream):
    """Pipelines stream."""


class PipelineJobsStream(base.PipelineJobsMixin, _WorkspaceChildStream):
    """Pipeline jobs stream."""

    parent_stream_type = PipelinesStream  # type: ignore[assignment]


class PipelineMetricsStream(base.PipelineMetricsMixin, _WorkspaceChildStream):
    """Pipeline metrics stream."""

    parent_stream_type = PipelinesStream  # type: ignore[assignment]


class DatasetsStream(base.DatasetsMixin, _WorkspaceChildStream):
    """Datasets stream."""


class JobsStream(base.JobsMixin, _WorkspaceChildStream):
    """Jobs stream."""


class ChannelsStream(base.ChannelsMixin, _WorkspaceChildStream):
    """Channels stream."""


class DataStoresStream(base.DataStoresMixin, _WorkspaceChildStream):
    """Data stores stream."""


class DataComponentsStream(base.DataComponentsMixin, _WorkspaceChildStream):
    """Data components stream."""

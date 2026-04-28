"""MeltanoCloud tap class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_meltano_cloud.streams import by_workspace, me

if TYPE_CHECKING:
    from tap_meltano_cloud.streams import base

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapMeltanoCloud(Tap):
    """Singer tap for MeltanoCloud."""

    name = "tap-meltano-cloud"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType(nullable=False),
            required=True,
            secret=True,  # Flag config as protected.
            title="Auth Token",
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            title="API URL",
            default="https://app.matatika.com/api",
            description="The url for the API service",
        ),
        th.Property(
            "workspace_ids",
            th.ArrayType(th.StringType(nullable=False)),
            required=False,
            title="Workspace IDs",
            description=(
                "List of workspace IDs to sync. "
                "When set, only the specified workspaces are fetched individually "
                "without requiring the workspaces list endpoint. "
                "When omitted, all workspaces accessible to the authenticated user "
                "are discovered and synced."
            ),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[base.MeltanoCloudStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        workspace_ids: list[str] | None = self.config.get("workspace_ids")

        if workspace_ids:
            return [
                by_workspace.WorkspacesStream(self, workspace_ids=workspace_ids),
                by_workspace.PipelinesStream(self, workspace_ids=workspace_ids),
                by_workspace.PipelineJobsStream(self, workspace_ids=workspace_ids),
                by_workspace.DatasetsStream(self, workspace_ids=workspace_ids),
                by_workspace.JobsStream(self, workspace_ids=workspace_ids),
                by_workspace.ChannelsStream(self, workspace_ids=workspace_ids),
                by_workspace.DataStoresStream(self, workspace_ids=workspace_ids),
                by_workspace.DataComponentsStream(self, workspace_ids=workspace_ids),
            ]

        return [
            me.WorkspacesStream(self),
            me.PipelinesStream(self),
            me.PipelineJobsStream(self),
            me.DatasetsStream(self),
            me.JobsStream(self),
            me.ChannelsStream(self),
            me.DataStoresStream(self),
            me.DataComponentsStream(self),
        ]


if __name__ == "__main__":
    TapMeltanoCloud.cli()

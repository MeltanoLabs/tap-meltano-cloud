"""MeltanoCloud tap class."""

from __future__ import annotations

import sys

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_meltano_cloud import streams

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
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest record date to sync",
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            title="API URL",
            default="https://app.matatika.com/api",
            description="The url for the API service",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[streams.MeltanoCloudStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.WorkspacesStream(self),
            streams.PipelinesStream(self),
            streams.DatasetsStream(self),
            streams.JobsStream(self),
            streams.ChannelsStream(self),
            streams.DataStoresStream(self),
            streams.DataComponentsStream(self),
        ]


if __name__ == "__main__":
    TapMeltanoCloud.cli()

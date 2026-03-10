"""REST client handling, including MeltanoCloudStream base class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:

    import requests
    from singer_sdk.pagination import BaseAPIPaginator


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

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @override
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator(token=self.config["auth_token"])

    @override
    def get_new_paginator(self) -> BaseAPIPaginator | None:
        """Return a new paginator instance."""
        # TODO(tap-meltano-cloud): Enable pagination when the API supports it correctly
        # https://github.com/MeltanoLabs/tap-meltano-cloud/issues/1
        return None

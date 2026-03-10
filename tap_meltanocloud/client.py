"""REST client handling, including MeltanoCloudStream base class."""

from __future__ import annotations

import decimal
import sys
from typing import TYPE_CHECKING, Any

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, PageNumberPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context


class MeltanoCloudPaginator(PageNumberPaginator):
    """Paginator for MeltanoCloud Spring HATEOAS paged responses."""

    @override
    def has_more(self, response: requests.Response) -> bool:
        """Return True if there are more pages.

        Args:
            response: The HTTP response object.

        Returns:
            True if there are more pages, False otherwise.
        """
        page = response.json().get("page", {})
        return page.get("number", 0) < page.get("totalPages", 0) - 1


class MeltanoCloudStream(RESTStream):
    """MeltanoCloud stream class."""

    records_jsonpath = "$[*]"
    page_size = 20

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @override
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator(token=self.config.get("auth_token", ""))

    @override
    def get_new_paginator(self) -> BaseAPIPaginator:
        """Return a new paginator instance."""
        return MeltanoCloudPaginator(start_value=0)

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {"size": self.page_size}
        if next_page_token is not None:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        yield from extract_jsonpath(
            self.records_jsonpath,
            input=response.json(parse_float=decimal.Decimal),
        )

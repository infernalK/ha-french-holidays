"""Sample API Client."""

from __future__ import annotations

import socket
import urllib.parse
from datetime import datetime
from typing import Any

import aiohttp
import async_timeout

from .const import LOGGER

ZONES_URL = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?group_by=zones&order_by=zones&limit=100"


class FrenchHolidayApiClientError(Exception):
    """Exception to indicate a general API error."""


class FrenchHolidayApiClientCommunicationError(
    FrenchHolidayApiClientError,
):
    """Exception to indicate a communication error."""


class FrenchHolidayApiClientAuthenticationError(
    FrenchHolidayApiClientError,
):
    """Exception to indicate an authentication error."""


class FrenchHolidayApiClient:
    """API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._session = session

    async def async_get_zones(self) -> Any:
        """Get available zones from the API."""
        zones_result = await self._api_wrapper(
            method="get",
            url=ZONES_URL,
        )

        return sorted(
            [x["zones"] for x in zones_result["results"]],
            key=lambda s: "1" if s.startswith("Zone") else "2",
        )

    async def async_get_events(self, zone: str) -> Any:
        """Get data from the API."""
        today = datetime.now().date()  # noqa: DTZ005
        url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?limit=100&refine={
            urllib.parse.quote(f'zones:"{zone}"')
        }&where={
            urllib.parse.quote(f"end_date >= date'{today}' and end_date > start_date")
        }&timezone={urllib.parse.quote('Europe/Paris')}&refine={
            urllib.parse.quote('population:"-"')
        }&refine={urllib.parse.quote('population:"Élèves"')}&order_by={
            urllib.parse.quote('start_date,location')
        }&group_by={
            urllib.parse.quote('start_date,end_date,description,zones,annee_scolaire')
        }"

        events_result = await self._api_wrapper(
            method="get",
            url=url,
        )

        return events_result["results"]

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            return await self._do_request(self._session, method, url, data, headers)
        except (
            TimeoutError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            # Some routers/ISPs (e.g. Freebox) hand out a broken IPv6 route,
            # which makes aiohttp hang or fail on the AAAA record before it
            # ever tries IPv4. Retry once, forcing IPv4 only.
            LOGGER.debug(
                "Request failed (%s), retrying over IPv4 only", exception
            )
            try:
                connector = aiohttp.TCPConnector(family=socket.AF_INET)
                async with aiohttp.ClientSession(connector=connector) as ipv4_session:
                    return await self._do_request(
                        ipv4_session, method, url, data, headers
                    )
            except TimeoutError as ipv4_exception:
                msg = f"Timeout error fetching information - {ipv4_exception}"
                raise FrenchHolidayApiClientCommunicationError(
                    msg,
                ) from ipv4_exception
            except (aiohttp.ClientError, socket.gaierror) as ipv4_exception:
                msg = f"Error fetching information - {ipv4_exception}"
                raise FrenchHolidayApiClientCommunicationError(
                    msg,
                ) from ipv4_exception
        except aiohttp.ClientError as exception:
            msg = f"Error fetching information - {exception}"
            raise FrenchHolidayApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise FrenchHolidayApiClientError(
                msg,
            ) from exception

    @staticmethod
    async def _do_request(
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        data: dict | None,
        headers: dict | None,
    ) -> Any:
        """Perform a single HTTP request and return the parsed JSON body."""
        async with async_timeout.timeout(10):
            response = await session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
            )
            return await response.json()

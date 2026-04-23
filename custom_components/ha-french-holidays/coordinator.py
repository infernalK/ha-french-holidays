"""DataUpdateCoordinator for french_holiday."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import slugify
from homeassistant.util.dt import parse_datetime

from .api import (
    FrenchHolidayApiClientAuthenticationError,
    FrenchHolidayApiClientError,
)
from .const import LOGGER
from .data import FrenchHolidayPeriod

if TYPE_CHECKING:
    from datetime import date

    from .data import FrenchHolidayConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class FrenchHolidayDataUpdateCoordinator(DataUpdateCoordinator[list[FrenchHolidayPeriod]]):
    """Class to manage fetching data from the API."""

    config_entry: FrenchHolidayConfigEntry

    async def _async_update_data(self) -> list[FrenchHolidayPeriod]:
        """Update data via library."""
        try:
            zone = self.config_entry.data["zone"]
            api_events = await self.config_entry.runtime_data.client.async_get_events(
                zone
            )
            LOGGER.debug("Got %s", api_events)
            return sorted(
                [
                    FrenchHolidayPeriod(
                        summary=period["description"],
                        start=parse_datetime(
                            period["start_date"], raise_on_error=True
                        ).date(),
                        end=max(
                            parse_datetime(
                                period["start_date"], raise_on_error=True
                            ).date(),
                            (parse_datetime(
                                period["end_date"], raise_on_error=True
                            ).date() - timedelta(days=1))
                        ),
                        uid=f"{zone}-{slugify(period['description'])}-{
                            period['annee_scolaire']
                        }",
                        year=period["annee_scolaire"],
                        zone=zone,
                    )
                    for period in api_events
                ],
                key=lambda e: e.start,
            )
        except FrenchHolidayApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except FrenchHolidayApiClientError as exception:
            raise UpdateFailed(exception) from exception

    def get_date_next_event(self, start_date: date) -> FrenchHolidayPeriod | None:
        """Get next event for a given date."""
        return next(
            (
                e
                for e in (self.data if self.data is not None else [])
                if e.end >= start_date
            ),
            None,
        )

    def get_date_future_event(self, start_date: date) -> FrenchHolidayPeriod | None:
        """Get next event for a given date."""
        return next(
            (
                e
                for e in (self.data if self.data is not None else [])
                if e.start > start_date
            ),
            None,
        )

    def get_date_event(self, date: date) -> FrenchHolidayPeriod | None:
        """Get next event for a given date."""
        return next(
            (
                event
                for event in (self.data if self.data is not None else [])
                if event.end >= date and event.start <= date
            ),
            None,
        )

    def get_events_between(
        self, start_date: date, end_date: date
    ) -> list[FrenchHolidayPeriod]:
        """Get active events overlapping given dates."""
        if self.data is None:
            return []
        return [
            event
            for event in self.data
            if event.end >= start_date and event.start <= end_date
        ]

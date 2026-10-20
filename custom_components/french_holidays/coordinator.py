"""DataUpdateCoordinator for french_holidays."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import slugify
from homeassistant.util.dt import parse_datetime

from .api import (
    FrenchHolidayApiClientAuthenticationError,
    FrenchHolidayApiClientError,
)
from .const import DOMAIN, LOGGER
from .data import FrenchHolidayPeriod, period_from_dict, period_to_dict

if TYPE_CHECKING:
    from datetime import date

    from homeassistant.core import HomeAssistant

    from .data import FrenchHolidayConfigEntry

STORAGE_VERSION = 1
NORMAL_UPDATE_INTERVAL = timedelta(days=1)
RETRY_UPDATE_INTERVAL = timedelta(hours=1)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class FrenchHolidayDataUpdateCoordinator(DataUpdateCoordinator[list[FrenchHolidayPeriod]]):
    """Class to manage fetching data from the API."""

    config_entry: FrenchHolidayConfigEntry
    using_cached_data: bool = False

    def __init__(self, hass: HomeAssistant, **kwargs) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, **kwargs)
        self._store: Store[list[dict]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{self.config_entry.entry_id}"
        )

    async def _async_update_data(self) -> list[FrenchHolidayPeriod]:
        """Update data via library."""
        try:
            zone = self.config_entry.data["zone"]
            api_events = await self.config_entry.runtime_data.client.async_get_events(
                zone
            )
            LOGGER.debug("Got %s", api_events)
            periods = sorted(
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
            cached = await self._async_load_cached_periods()
            if cached is not None:
                LOGGER.warning(
                    "French holidays API unavailable, using cached data; "
                    "retrying in %s: %s",
                    RETRY_UPDATE_INTERVAL,
                    exception,
                )
                self.using_cached_data = True
                self.update_interval = RETRY_UPDATE_INTERVAL
                return cached
            raise UpdateFailed(exception) from exception
        else:
            self.using_cached_data = False
            self.update_interval = NORMAL_UPDATE_INTERVAL
            await self._store.async_save([period_to_dict(p) for p in periods])
            return periods

    async def _async_load_cached_periods(self) -> list[FrenchHolidayPeriod] | None:
        """Load the last successfully fetched periods from the persistent cache."""
        stored = await self._store.async_load()
        if not stored:
            return None
        try:
            return [period_from_dict(item) for item in stored]
        except (KeyError, ValueError, TypeError):
            LOGGER.warning("Ignoring invalid cached french_holidays data")
            return None

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

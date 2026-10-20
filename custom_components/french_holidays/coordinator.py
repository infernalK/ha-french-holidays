"""DataUpdateCoordinator for french_holidays."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
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
ISSUE_ZONE_NOT_FOUND = "zone_not_found"


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
            if periods:
                self._async_delete_zone_issue()
            else:
                await self._async_check_zone_validity()
            return periods

    def _issue_id(self) -> str:
        return f"{ISSUE_ZONE_NOT_FOUND}_{self.config_entry.entry_id}"

    def _async_delete_zone_issue(self) -> None:
        ir.async_delete_issue(self.hass, DOMAIN, self._issue_id())

    async def _async_check_zone_validity(self) -> None:
        """Flag a repair issue if the configured zone no longer exists upstream.

        An empty result can also mean there is simply no upcoming period yet
        published, so this only raises when the zone itself has disappeared
        from the list the Ministry publishes.
        """
        zone = self.config_entry.data["zone"]
        try:
            zones = await self.config_entry.runtime_data.client.async_get_zones()
        except FrenchHolidayApiClientError:
            return
        if zone in zones:
            self._async_delete_zone_issue()
            return
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            self._issue_id(),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_ZONE_NOT_FOUND,
            translation_placeholders={"zone": zone},
        )

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

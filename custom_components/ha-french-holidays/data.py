"""Custom types for ha-french-holidays."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import date

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import FrenchHolidayApiClient
    from .coordinator import FrenchHolidayDataUpdateCoordinator


type FrenchHolidayConfigEntry = ConfigEntry[FrenchHolidayData]


@dataclass
class FrenchHolidayData:
    """Data for the ha-french-holidays integration."""

    client: FrenchHolidayApiClient
    coordinator: FrenchHolidayDataUpdateCoordinator
    integration: Integration


@dataclass
class FrenchHolidayPeriod:
    """Data for the ha-french-holidays integration."""

    summary: str
    start: date
    end: date
    uid: str
    zone: str
    year: str


def get_period_extra_attributes(event: FrenchHolidayPeriod) -> dict[str, Any]:
    """Get extra attributes for an event."""
    return {
        "start_date": event.start,
        "end_date": event.end,
        "zone": event.zone,
        "année_scolaire": event.year,
    }

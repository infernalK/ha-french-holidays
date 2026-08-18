"""Custom types for french_holidays."""

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
    """Data for the french_holidays integration."""

    client: FrenchHolidayApiClient
    coordinator: FrenchHolidayDataUpdateCoordinator
    integration: Integration


@dataclass
class FrenchHolidayPeriod:
    """Data for the french_holidays integration."""

    summary: str
    start: date
    end: date
    uid: str
    zone: str
    year: str


_MONTHS_SHORT = [
    "janv",
    "févr",
    "mars",
    "avr",
    "mai",
    "juin",
    "juil",
    "août",
    "sept",
    "oct",
    "nov",
    "déc",
]


def _format_date_short(event_date: date) -> str:
    """Format a date to short French format: '04 juil'."""
    return f"{event_date.day:02d} {_MONTHS_SHORT[event_date.month - 1]}"


def get_period_extra_attributes(event: FrenchHolidayPeriod) -> dict[str, Any]:
    """Get extra attributes for an event."""
    return {
        "start_date": event.start,
        "end_date": event.end,
        "start_date_short": _format_date_short(event.start),
        "end_date_short": _format_date_short(event.end),
        "start_weekday": event.start.weekday(),
        "end_weekday": event.end.weekday(),
        "duration_days": (event.end - event.start).days + 1,
        "zone": event.zone,
        "année_scolaire": event.year,
    }

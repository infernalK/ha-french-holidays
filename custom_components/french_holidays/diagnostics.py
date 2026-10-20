"""Diagnostics support for french_holidays."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .data import period_to_dict

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import FrenchHolidayConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: FrenchHolidayConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    periods = coordinator.data or []
    return {
        "entry_data": dict(entry.data),
        "using_cached_data": coordinator.using_cached_data,
        "last_update_success": coordinator.last_update_success,
        "last_exception": repr(coordinator.last_exception)
        if coordinator.last_exception
        else None,
        "update_interval_seconds": (
            coordinator.update_interval.total_seconds()
            if coordinator.update_interval
            else None
        ),
        "periods_count": len(periods),
        "periods": [period_to_dict(p) for p in periods],
    }

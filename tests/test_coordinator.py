"""Tests for the french_holidays DataUpdateCoordinator."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.french_holidays.api import (
    FrenchHolidayApiClientAuthenticationError,
    FrenchHolidayApiClientError,
)
from custom_components.french_holidays.const import DOMAIN
from custom_components.french_holidays.coordinator import (
    NORMAL_UPDATE_INTERVAL,
    RETRY_UPDATE_INTERVAL,
    FrenchHolidayDataUpdateCoordinator,
)
from custom_components.french_holidays.data import FrenchHolidayData

RAW_EVENT = {
    "description": "Vacances de Noël",
    "start_date": "2026-12-20",
    "end_date": "2027-01-05",
    "annee_scolaire": "2026-2027",
}


def _make_coordinator(hass, client) -> FrenchHolidayDataUpdateCoordinator:
    entry = MockConfigEntry(domain=DOMAIN, data={"zone": "Zone C"})
    entry.add_to_hass(hass)
    coordinator = FrenchHolidayDataUpdateCoordinator(
        hass=hass,
        logger=logging.getLogger(__name__),
        name=DOMAIN,
        config_entry=entry,
        update_interval=NORMAL_UPDATE_INTERVAL,
    )
    entry.runtime_data = FrenchHolidayData(
        client=client, coordinator=coordinator, integration=None
    )
    return coordinator


async def test_update_success_parses_periods_and_saves_cache(hass) -> None:
    client = AsyncMock()
    client.async_get_events.return_value = [RAW_EVENT]
    coordinator = _make_coordinator(hass, client)

    periods = await coordinator._async_update_data()

    assert len(periods) == 1
    assert periods[0].summary == "Vacances de Noël"
    assert periods[0].zone == "Zone C"
    assert coordinator.using_cached_data is False
    assert coordinator.update_interval == NORMAL_UPDATE_INTERVAL


async def test_update_failure_without_cache_raises_update_failed(hass) -> None:
    client = AsyncMock()
    client.async_get_events.side_effect = FrenchHolidayApiClientError("boom")
    coordinator = _make_coordinator(hass, client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_update_failure_falls_back_to_cache(hass) -> None:
    client = AsyncMock()
    client.async_get_events.return_value = [RAW_EVENT]
    coordinator = _make_coordinator(hass, client)
    await coordinator._async_update_data()  # populate the persistent cache

    client.async_get_events.side_effect = FrenchHolidayApiClientError("boom")

    periods = await coordinator._async_update_data()

    assert len(periods) == 1
    assert coordinator.using_cached_data is True
    assert coordinator.update_interval == RETRY_UPDATE_INTERVAL


async def test_recovery_after_cache_fallback_resets_interval(hass) -> None:
    client = AsyncMock()
    client.async_get_events.return_value = [RAW_EVENT]
    coordinator = _make_coordinator(hass, client)
    await coordinator._async_update_data()

    client.async_get_events.side_effect = FrenchHolidayApiClientError("boom")
    await coordinator._async_update_data()
    assert coordinator.using_cached_data is True

    client.async_get_events.side_effect = None
    client.async_get_events.return_value = [RAW_EVENT]
    await coordinator._async_update_data()

    assert coordinator.using_cached_data is False
    assert coordinator.update_interval == NORMAL_UPDATE_INTERVAL


async def test_auth_failure_raises_config_entry_auth_failed(hass) -> None:
    client = AsyncMock()
    client.async_get_events.side_effect = FrenchHolidayApiClientAuthenticationError(
        "nope"
    )
    coordinator = _make_coordinator(hass, client)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()

"""Sensor platform for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt, slugify

from .const import DOMAIN, FRIENDLY_PREFIX
from .data import get_period_extra_attributes
from .entity import FrenchHolidayEntity


def _format_date_french(date_obj) -> str:
    """Format a date object to French format: 'Lundi 18 avril'."""
    weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    weekday = weekdays[date_obj.weekday()]
    month = months[date_obj.month - 1]
    return f"{weekday} {date_obj.day} {month}"


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FrenchHolidayDataUpdateCoordinator
    from .data import FrenchHolidayConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: FrenchHolidayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [
            CurrentVacancesFrSensor(
                coordinator=entry.runtime_data.coordinator,
            ),
            NextVacancesFrSensor(
                coordinator=entry.runtime_data.coordinator,
            ),
            DaysUntilNextVacancesFrSensor(
                coordinator=entry.runtime_data.coordinator,
            ),
            NextVacancesFrDatesSensor(
                coordinator=entry.runtime_data.coordinator,
            ),
        ]
    )


class CurrentVacancesFrSensor(FrenchHolidayEntity, SensorEntity):
    """ha-french-holidays current Sensor class."""

    def __init__(
        self,
        coordinator: FrenchHolidayDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_current_{
            slugify(self.coordinator.config_entry.data['zone'])
        }"
        self.entity_description = SensorEntityDescription(
            key="current",
            name=f"{FRIENDLY_PREFIX} en cours",
            icon="mdi:format-quote-close",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to event each day at 00:00 to update value."""
        await super().async_added_to_hass()
        self.unsubscribe = async_track_time_change(
            self.hass, lambda _: self._handle_coordinator_update(), 0, 0, 0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the events."""
        if self.unsubscribe:
            self.unsubscribe()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity."""
        today_event = self.coordinator.get_date_event(dt.now().date())
        if today_event is not None:
            self._attr_native_value = today_event.summary
            self._attr_extra_state_attributes = get_period_extra_attributes(today_event)
        else:
            self._attr_native_value = None

        self.schedule_update_ha_state()


class NextVacancesFrSensor(FrenchHolidayEntity, SensorEntity):
    """ha-french-holidays next Sensor class."""

    def __init__(
        self,
        coordinator: FrenchHolidayDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_next_{
            slugify(self.coordinator.config_entry.data['zone'])
        }"
        self.entity_description = SensorEntityDescription(
            key="next",
            name=f"{FRIENDLY_PREFIX} à venir",
            icon="mdi:format-quote-close",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to event each day at 00:00 to update value."""
        await super().async_added_to_hass()
        self.unsubscribe = async_track_time_change(
            self.hass, lambda _: self._handle_coordinator_update(), 0, 0, 0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the events."""
        if self.unsubscribe:
            self.unsubscribe()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity."""
        today = dt.now().date()
        next_event = self.coordinator.get_date_future_event(today)
        if next_event is not None:
            self._attr_native_value = next_event.summary
            self._attr_extra_state_attributes = get_period_extra_attributes(next_event)
        else:
            self._attr_native_value = None

        self.schedule_update_ha_state()


class DaysUntilNextVacancesFrSensor(FrenchHolidayEntity, SensorEntity):
    """ha-french-holidays days until next Sensor class."""

    def __init__(
        self,
        coordinator: FrenchHolidayDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_days_until_next_{
            slugify(self.coordinator.config_entry.data['zone'])
        }"
        self.entity_description = SensorEntityDescription(
            key="days_until_next",
            name=f"{FRIENDLY_PREFIX} - jours avant prochaines",
            icon="mdi:calendar-clock",
            native_unit_of_measurement="days",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to event each day at 00:00 to update value."""
        await super().async_added_to_hass()
        self.unsubscribe = async_track_time_change(
            self.hass, lambda _: self._handle_coordinator_update(), 0, 0, 0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the events."""
        if self.unsubscribe:
            self.unsubscribe()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity."""
        today = dt.now().date()
        next_event = self.coordinator.get_date_future_event(today)
        if next_event is not None:
            days_until = (next_event.start - today).days
            self._attr_native_value = days_until
            self._attr_extra_state_attributes = get_period_extra_attributes(next_event)
        else:
            self._attr_native_value = None

        self.schedule_update_ha_state()


class NextVacancesFrDatesSensor(FrenchHolidayEntity, SensorEntity):
    """ha-french-holidays next dates Sensor class."""

    def __init__(
        self,
        coordinator: FrenchHolidayDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_next_dates_{
            slugify(self.coordinator.config_entry.data['zone'])
        }"
        self.entity_description = SensorEntityDescription(
            key="next_dates",
            name=f"{FRIENDLY_PREFIX} - dates prochaines",
            icon="mdi:calendar-range",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to event each day at 00:00 to update value."""
        await super().async_added_to_hass()
        self.unsubscribe = async_track_time_change(
            self.hass, lambda _: self._handle_coordinator_update(), 0, 0, 0
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from the events."""
        if self.unsubscribe:
            self.unsubscribe()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity."""
        today = dt.now().date()
        next_event = self.coordinator.get_date_future_event(today)
        if next_event is not None:
            start_formatted = _format_date_french(next_event.start)
            end_formatted = _format_date_french(next_event.end)
            self._attr_native_value = f"{start_formatted} - {end_formatted}"
            self._attr_extra_state_attributes = get_period_extra_attributes(next_event)
        else:
            self._attr_native_value = None

        self.schedule_update_ha_state()

"""Calendar platform for vacances_fr."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.util import dt, slugify

from .const import DOMAIN, FRIENDLY_NAME
from .entity import VacancesFrEntity

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import VacancesFrDataUpdateCoordinator
    from .data import VacancesFrConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: VacancesFrConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    async_add_entities(
        [
            VacancesFrCalendar(
                coordinator=entry.runtime_data.coordinator,
                entity_description=CalendarEntityDescription(
                    key="vacances_fr", name=FRIENDLY_NAME
                ),
            )
        ]
    )


class VacancesFrCalendar(VacancesFrEntity, CalendarEntity):
    """Vacances_fr calendar class."""

    _event: CalendarEvent | None = None

    def __init__(
        self,
        coordinator: VacancesFrDataUpdateCoordinator,
        entity_description: CalendarEntityDescription,
    ) -> None:
        """Initialize the calendar class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_id = (
            f"{Platform.CALENDAR}.{DOMAIN}_"
            f"{slugify(self.coordinator.config_entry.data.get('zone', 'unknown'))}"
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity."""
        next_event = self.coordinator.get_date_next_event(dt.now().date())

        if next_event is None:
            self._event = None
        else:
            # Pour CalendarEvent, end doit être exclusif (jour après la fin)
            calendar_end = next_event.end + timedelta(days=1)
            self._event = CalendarEvent(
                start=next_event.start,
                end=calendar_end,
                summary=f"{next_event.summary} - {next_event.zone}",
                uid=next_event.uid,
            )

        self.async_write_ha_state()

    async def async_get_events(
        self,
        hass: HomeAssistant,  # noqa: ARG002
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Get events in a specific date range."""
        if self.coordinator.data is None:
            return []
            
        events = self.coordinator.get_events_between(
            start_date.date(),
            end_date.date(),
        )

        return [
            CalendarEvent(
                summary=f"{event.summary} - {event.zone}",
                start=event.start,
                end=event.end + timedelta(days=1),  # end exclusif pour CalendarEvent
                uid=event.uid,
            )
            for event in events
        ]

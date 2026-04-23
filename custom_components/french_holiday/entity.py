"""FrenchHolidayEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTRIBUTION, FRIENDLY_NAME
from .coordinator import FrenchHolidayDataUpdateCoordinator


class FrenchHolidayEntity(CoordinatorEntity[FrenchHolidayDataUpdateCoordinator]):
    """FrenchHolidayEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: FrenchHolidayDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-{slugify(self.__class__.__name__)}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=f"{FRIENDLY_NAME} ({coordinator.config_entry.data['zone']})",
        )

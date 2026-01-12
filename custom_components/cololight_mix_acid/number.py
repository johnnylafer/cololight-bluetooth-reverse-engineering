"""Number platform for Cololight Mix ACID."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import CololightDataUpdateCoordinator
from . import protocol

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cololight number entities."""
    coordinator: CololightDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[NumberEntity] = [
        CololightSpeedNumber(coordinator),
    ]

    async_add_entities(entities)


class CololightSpeedNumber(NumberEntity):
    """Number entity for effect speed control (0-255 slider)."""

    _attr_has_entity_name = True
    _attr_name = "Effect Speed"
    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: CololightDataUpdateCoordinator) -> None:
        """Initialize the speed number entity."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_speed_slider"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }
        self._current_speed = 10  # Default speed (0x0a)

    @property
    def native_value(self) -> float:
        """Return the current speed value."""
        # Try to get speed from current scene
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)
                if decoded.get('speed') is not None:
                    self._current_speed = decoded['speed']
            except Exception:
                pass
        return float(self._current_speed)

    async def async_set_native_value(self, value: float) -> None:
        """Set new speed value."""
        speed = int(value)

        # Try to maintain current effect if possible
        current_effect_idx = None
        current_variation = 0
        current_mode = 0x01  # Default to mode 0x01

        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)
                current_effect_idx = decoded.get('effect_index')
                current_mode = decoded.get('mode', 0x01)
                if decoded.get('variation') is not None:
                    current_variation = decoded['variation']
            except Exception:
                pass

        if current_effect_idx is not None:
            # Re-apply current effect with new speed, maintaining the current mode
            if current_mode == 0x01:
                cmd = protocol.encode_dynamic_effect(
                    current_effect_idx, speed=speed, variation=current_variation
                )
            elif current_mode in (0x03, 0x05):
                # Special overall or smooth overall
                cmd = protocol.encode_smooth_overall(
                    current_effect_idx, speed=speed, variation=current_variation
                )
            elif current_mode in (0x04, 0x06):
                # Special individual or smooth individual
                cmd = protocol.encode_smooth_individual(
                    current_effect_idx, speed=speed, variation=current_variation
                )
            else:
                # Fallback to dynamic effect
                cmd = protocol.encode_dynamic_effect(
                    current_effect_idx, speed=speed, variation=current_variation
                )

            await self.coordinator.async_set_scene(cmd.hex())
        else:
            # Default to white breathing if no current effect
            cmd = protocol.encode_dynamic_effect(0x89, speed=speed)
            await self.coordinator.async_set_scene(cmd.hex())

        self._current_speed = speed
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

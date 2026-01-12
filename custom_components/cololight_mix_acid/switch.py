"""Switch platform for Cololight Mix ACID."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up Cololight switch entities."""
    coordinator: CololightDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[SwitchEntity] = [
        CololightSmoothTransitionSwitch(coordinator),
    ]

    async_add_entities(entities)


class CololightSmoothTransitionSwitch(SwitchEntity):
    """Switch entity for enabling smooth transitions (mode 0x05/0x06)."""

    _attr_has_entity_name = True
    _attr_name = "Smooth Transitions"

    def __init__(self, coordinator: CololightDataUpdateCoordinator) -> None:
        """Initialize the smooth transition switch."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_smooth_transitions"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }
        self._is_smooth = False

    @property
    def is_on(self) -> bool:
        """Return true if smooth transitions are enabled."""
        # Check current mode - modes 0x05 and 0x06 are smooth
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)
                mode = decoded.get('mode')
                self._is_smooth = mode in (0x05, 0x06)
            except Exception:
                pass
        return self._is_smooth

    async def async_turn_on(self, **kwargs) -> None:
        """Enable smooth transitions."""
        # Convert current effect to smooth mode
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)

                current_mode = decoded.get('mode')
                effect_idx = decoded.get('effect_index')
                speed = decoded.get('speed', 0x0A)
                variation = decoded.get('variation', 0)
                color_jump = decoded.get('color_jump', 0)

                if effect_idx is not None:
                    # Convert to smooth mode
                    if current_mode == 0x01:
                        # Mode 0x01 doesn't have a direct smooth equivalent, use mode 0x05
                        cmd = protocol.encode_smooth_overall(
                            effect_idx, speed=speed, variation=variation, color_jump=color_jump
                        )
                    elif current_mode == 0x03:
                        # Mode 0x03 -> Mode 0x05 (smooth overall)
                        cmd = protocol.encode_smooth_overall(
                            effect_idx, speed=speed, variation=variation, color_jump=color_jump
                        )
                    elif current_mode == 0x04:
                        # Mode 0x04 -> Mode 0x06 (smooth individual)
                        cmd = protocol.encode_smooth_individual(
                            effect_idx, speed=speed, variation=variation, color_jump=color_jump
                        )
                    elif current_mode in (0x05, 0x06):
                        # Already smooth, do nothing
                        return
                    else:
                        # Unknown mode, default to smooth individual
                        cmd = protocol.encode_smooth_individual(
                            effect_idx, speed=speed, variation=variation
                        )

                    await self.coordinator.async_set_scene(cmd.hex())
                    self._is_smooth = True
                    self.async_write_ha_state()
            except Exception as ex:
                _LOGGER.error("Failed to enable smooth transitions: %s", ex)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable smooth transitions."""
        # Convert current effect to non-smooth mode
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)

                current_mode = decoded.get('mode')
                effect_idx = decoded.get('effect_index')
                speed = decoded.get('speed', 0x0A)
                variation = decoded.get('variation', 0)
                color_jump = decoded.get('color_jump', 0)

                if effect_idx is not None:
                    # Convert to non-smooth mode
                    if current_mode == 0x05:
                        # Mode 0x05 -> Mode 0x03 (special overall)
                        cmd = protocol.encode_special_overall(
                            effect_idx, speed=speed, variation=variation, color_jump=color_jump
                        )
                    elif current_mode == 0x06:
                        # Mode 0x06 -> Mode 0x04 (special individual)
                        cmd = protocol.encode_special_individual(
                            effect_idx, speed=speed, variation=variation, color_jump=color_jump
                        )
                    elif current_mode in (0x03, 0x04):
                        # Already non-smooth, do nothing
                        return
                    elif current_mode == 0x01:
                        # Mode 0x01 is already non-smooth
                        return
                    else:
                        # Unknown mode, default to dynamic effect
                        cmd = protocol.encode_dynamic_effect(
                            effect_idx, speed=speed, variation=variation
                        )

                    await self.coordinator.async_set_scene(cmd.hex())
                    self._is_smooth = False
                    self.async_write_ha_state()
            except Exception as ex:
                _LOGGER.error("Failed to disable smooth transitions: %s", ex)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

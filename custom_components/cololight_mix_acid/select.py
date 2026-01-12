"""Select platform for Cololight Mix ACID."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DYNAMIC_EFFECTS, BUILT_IN_SCENES
from .coordinator import CololightDataUpdateCoordinator
from . import protocol

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cololight select entities."""
    coordinator: CololightDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[SelectEntity] = [
        CololightEffectSelect(coordinator),
        CololightVariationSelect(coordinator),
    ]

    async_add_entities(entities)


class CololightEffectSelect(SelectEntity):
    """Select entity for choosing dynamic effects."""

    _attr_has_entity_name = True
    _attr_name = "Effect"

    def __init__(self, coordinator: CololightDataUpdateCoordinator) -> None:
        """Initialize the effect select."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_effect"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }
        self._attr_options = list(DYNAMIC_EFFECTS.keys())
        self._current_effect = None

    @property
    def current_option(self) -> str | None:
        """Return the currently selected effect."""
        # Try to determine current effect from coordinator state
        if self.coordinator.current_scene:
            # Parse the scene hex to extract effect index
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                if len(scene_bytes) >= 5:
                    decoded = protocol.decode_state(scene_bytes)
                    if decoded.get('effect_index') is not None:
                        effect_idx = decoded['effect_index']
                        # Find effect name by index
                        for name, idx in DYNAMIC_EFFECTS.items():
                            if idx == effect_idx:
                                return name
            except Exception:
                pass
        return self._current_effect

    async def async_select_option(self, option: str) -> None:
        """Select a new effect."""
        if option not in DYNAMIC_EFFECTS:
            _LOGGER.error("Invalid effect: %s", option)
            return

        effect_idx = DYNAMIC_EFFECTS[option]
        # Use mode 0x06 (smooth individual) like the original working scenes
        # Default speed 0x18 (24), variation 0x00
        cmd = protocol.encode_smooth_individual(effect_idx, speed=0x18, variation=0)
        await self.coordinator.async_set_scene(cmd.hex())
        self._current_effect = option
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


class CololightSpeedSelect(SelectEntity):
    """Select entity for effect speed control."""

    _attr_has_entity_name = True
    _attr_name = "Effect Speed"

    def __init__(self, coordinator: CololightDataUpdateCoordinator) -> None:
        """Initialize the speed select."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }
        # Provide common speed presets
        self._attr_options = [
            "Very Fast (0x00)",
            "Fast (0x05)",
            "Normal (0x0a)",
            "Slow (0x14)",
            "Very Slow (0x1e)",
        ]
        self._speed_map = {
            "Very Fast (0x00)": 0x00,
            "Fast (0x05)": 0x05,
            "Normal (0x0a)": 0x0A,
            "Slow (0x14)": 0x14,
            "Very Slow (0x1e)": 0x1E,
        }
        self._current_speed = "Normal (0x0a)"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected speed."""
        return self._current_speed

    async def async_select_option(self, option: str) -> None:
        """Select a new speed."""
        if option not in self._speed_map:
            _LOGGER.error("Invalid speed: %s", option)
            return

        speed = self._speed_map[option]

        # Try to maintain current effect if possible
        current_effect_idx = None
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)
                current_effect_idx = decoded.get('effect_index')
            except Exception:
                pass

        if current_effect_idx is not None:
            # Re-apply current effect with new speed
            cmd = protocol.encode_dynamic_effect(current_effect_idx, speed=speed)
            await self.coordinator.async_set_scene(cmd.hex())
        else:
            # Default to white breathing if no current effect
            cmd = protocol.encode_dynamic_effect(0x89, speed=speed)  # White breathing
            await self.coordinator.async_set_scene(cmd.hex())

        self._current_speed = option
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


class CololightVariationSelect(SelectEntity):
    """Select entity for variation mode control."""

    _attr_has_entity_name = True
    _attr_name = "Variation Mode"

    def __init__(self, coordinator: CololightDataUpdateCoordinator) -> None:
        """Initialize the variation select."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.address}_variation"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }
        # For mode 0x01, variation is just 0x00-0x0F
        self._attr_options = [f"Variation {i:X}" for i in range(16)]
        self._current_variation = "Variation 0"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected variation."""
        return self._current_variation

    async def async_select_option(self, option: str) -> None:
        """Select a new variation."""
        # Extract hex value from option string
        try:
            variation = int(option.split()[1], 16)
        except (IndexError, ValueError):
            _LOGGER.error("Invalid variation: %s", option)
            return

        # Try to maintain current effect if possible
        current_effect_idx = None
        current_speed = 0x0A
        if self.coordinator.current_scene:
            try:
                scene_bytes = bytes.fromhex(self.coordinator.current_scene)
                decoded = protocol.decode_state(scene_bytes)
                current_effect_idx = decoded.get('effect_index')
                if decoded.get('speed') is not None:
                    current_speed = decoded['speed']
            except Exception:
                pass

        if current_effect_idx is not None:
            # Re-apply current effect with new variation using smooth mode
            cmd = protocol.encode_smooth_individual(
                current_effect_idx, speed=current_speed, variation=variation
            )
            await self.coordinator.async_set_scene(cmd.hex())
        else:
            # Default to white breathing with smooth mode if no current effect
            cmd = protocol.encode_smooth_individual(0x89, speed=0x18, variation=variation)
            await self.coordinator.async_set_scene(cmd.hex())

        self._current_variation = option
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

"""Light platform for Cololight Mix ACID."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BUILT_IN_SCENES, CONF_CUSTOM_SCENES, DOMAIN
from .coordinator import CololightDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cololight light from a config entry."""
    coordinator: CololightDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Get custom scenes from options
    custom_scenes = {}
    if CONF_CUSTOM_SCENES in config_entry.options:
        scenes_text = config_entry.options[CONF_CUSTOM_SCENES]
        if scenes_text:
            for line in scenes_text.strip().split("\n"):
                if ":" in line:
                    name, hex_val = line.strip().split(":", 1)
                    if len(hex_val) == 10:
                        custom_scenes[name.strip()] = hex_val.strip()

    async_add_entities([CololightLight(coordinator, custom_scenes)])


class CololightLight(CoordinatorEntity[CololightDataUpdateCoordinator], LightEntity):
    """Representation of a Cololight Mix ACID light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(
        self,
        coordinator: CololightDataUpdateCoordinator,
        custom_scenes: dict[str, str],
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._custom_scenes = custom_scenes

        # Build complete effect list (built-in + custom)
        self._attr_effect_list = list(BUILT_IN_SCENES.keys()) + list(
            custom_scenes.keys()
        )

        # Set unique ID based on MAC address
        self._attr_unique_id = coordinator.address.lower().replace(":", "")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": "Cololight Mix ACID",
            "manufacturer": "Cololight",
            "model": "Mix ACID",
            "connections": {("bluetooth", coordinator.address)},
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.coordinator.is_on

    @property
    def brightness(self) -> int:
        """Return the brightness (0-255)."""
        # Convert from 0-100 to 0-255
        return int((self.coordinator.brightness / 100.0) * 255)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color."""
        return self.coordinator.rgb_color

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        if self.coordinator.current_scene:
            # Check if it matches a known scene
            for name, hex_val in BUILT_IN_SCENES.items():
                if self.coordinator.current_scene.lower() == hex_val.lower():
                    return name

            # Check custom scenes
            for name, hex_val in self._custom_scenes.items():
                if self.coordinator.current_scene.lower() == hex_val.lower():
                    return name

        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        # Handle effect selection
        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]

            # Check built-in scenes
            if effect in BUILT_IN_SCENES:
                await self.coordinator.async_set_scene(BUILT_IN_SCENES[effect])
            # Check custom scenes
            elif effect in self._custom_scenes:
                await self.coordinator.async_set_scene(self._custom_scenes[effect])
            else:
                _LOGGER.warning("Unknown effect: %s", effect)

        # Handle RGB color
        elif ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            brightness = None

            # If brightness is also provided, use it
            if ATTR_BRIGHTNESS in kwargs:
                # Convert from 0-255 to 0-100
                brightness = int((kwargs[ATTR_BRIGHTNESS] / 255.0) * 100)

            await self.coordinator.async_set_rgb_color(rgb, brightness)

        # Handle brightness only
        elif ATTR_BRIGHTNESS in kwargs:
            # Convert from 0-255 to 0-100
            brightness = int((kwargs[ATTR_BRIGHTNESS] / 255.0) * 100)
            await self.coordinator.async_set_brightness(brightness)

        # Just turn on with last RGB state
        else:
            # Restore last known RGB color
            await self.coordinator.async_set_rgb_color(
                self.coordinator.rgb_color, self.coordinator.brightness
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.coordinator.async_turn_off()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

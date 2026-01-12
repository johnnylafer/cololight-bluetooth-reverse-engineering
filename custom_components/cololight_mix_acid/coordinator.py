"""Coordinator for Cololight Mix ACID."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakClient
from bleak.exc import BleakError
from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import CoreState, HomeAssistant, callback

from .const import CHAR_BRIGHTNESS, CHAR_STATE

_LOGGER = logging.getLogger(__name__)


class CololightDataUpdateCoordinator(ActiveBluetoothDataUpdateCoordinator[None]):
    """Class to manage fetching Cololight data."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            address=address,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_poll,
            mode=bluetooth.BluetoothScanningMode.ACTIVE,
            connectable=True,
        )

        # Cached state
        self._is_on = False
        self._brightness = 100
        self._rgb_color = (255, 255, 255)
        self._current_scene: str | None = None

    @callback
    def _needs_poll(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        seconds_since_last_poll: float | None,
    ) -> bool:
        """Determine if we need to poll the device."""
        # Only poll if Home Assistant is running and we have a connectable device
        return (
            self.hass.state == CoreState.running
            and bool(
                bluetooth.async_ble_device_from_address(
                    self.hass, service_info.device.address, connectable=True
                )
            )
        )

    async def _async_poll(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Poll the device for state."""
        # Get a connectable BLE device
        if service_info.connectable:
            ble_device = service_info.device
        elif device := bluetooth.async_ble_device_from_address(
            self.hass, service_info.device.address, True
        ):
            ble_device = device
        else:
            raise RuntimeError(
                f"No connectable device found for {service_info.device.address}"
            )

        # Establish connection using bleak-retry-connector
        try:
            async with establish_connection(
                client_class=BleakClient,
                device=ble_device,
                name=service_info.name,
                disconnected_callback=lambda client: None,
                max_attempts=3,
                use_services_cache=True,
            ) as client:
                await self._async_read_state(client)
        except (BleakError, TimeoutError) as ex:
            _LOGGER.debug("Error polling %s: %s", self.address, ex)

    async def _async_read_state(self, client: BleakClient) -> None:
        """Read current state from device."""
        try:
            # Read STATE characteristic
            state_data = await client.read_gatt_char(CHAR_STATE)
            if len(state_data) >= 5:
                # Check if device is on (not all zeros except header)
                self._is_on = not all(b == 0 for b in state_data[1:])

                if self._is_on:
                    # Mode byte is at position 4
                    mode = state_data[4]

                    if mode == 0x00:
                        # RGB mode - Read format: [0xFF] [B] [G] [R] [0x00]
                        self._rgb_color = (state_data[3], state_data[2], state_data[1])
                        self._current_scene = None
                    else:
                        # Scene mode
                        self._current_scene = state_data.hex()

            # Read brightness
            brightness_data = await client.read_gatt_char(CHAR_BRIGHTNESS)
            if len(brightness_data) >= 2 and brightness_data[0] == 0xCF:
                self._brightness = brightness_data[1]

        except BleakError as ex:
            _LOGGER.debug("Failed to read state: %s", ex)

    @callback
    def _async_handle_unavailable(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Handle device going unavailable."""
        _LOGGER.debug("Device %s is unavailable", self.address)

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle Bluetooth advertisement."""
        # For this device, we primarily use polling since state changes
        # are initiated by user actions, not advertisements
        pass

    async def async_set_brightness(self, brightness: int) -> None:
        """Set brightness."""
        await self._async_execute_command(
            lambda client: self._async_write_brightness(client, brightness)
        )

    async def async_set_rgb_color(
        self, rgb: tuple[int, int, int], brightness: int | None = None
    ) -> None:
        """Set RGB color."""
        await self._async_execute_command(
            lambda client: self._async_write_rgb(client, rgb, brightness)
        )

    async def async_set_scene(self, scene_hex: str) -> None:
        """Set scene."""
        await self._async_execute_command(
            lambda client: self._async_write_scene(client, scene_hex)
        )

    async def async_turn_off(self) -> None:
        """Turn off the light."""
        await self._async_execute_command(self._async_write_off)

    async def _async_execute_command(self, command_func) -> None:
        """Execute a command on the device."""
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if not ble_device:
            _LOGGER.warning("Device %s not available", self.address)
            return

        try:
            async with establish_connection(
                client_class=BleakClient,
                device=ble_device,
                name=ble_device.name,
                disconnected_callback=lambda client: None,
                max_attempts=3,
                use_services_cache=True,
            ) as client:
                await command_func(client)
                # Read back state after command
                await self._async_read_state(client)
        except (BleakError, TimeoutError) as ex:
            _LOGGER.error("Failed to execute command: %s", ex)

    async def _async_write_brightness(
        self, client: BleakClient, brightness: int
    ) -> None:
        """Write brightness value."""
        brightness = max(0, min(100, brightness))
        cmd = bytes([0xCF, brightness])
        await client.write_gatt_char(CHAR_BRIGHTNESS, cmd, response=True)

    async def _async_write_rgb(
        self,
        client: BleakClient,
        rgb: tuple[int, int, int],
        brightness: int | None,
    ) -> None:
        """Write RGB color."""
        r, g, b = rgb

        # If brightness provided, scale RGB values
        if brightness is not None:
            scale = brightness / 100.0
            r = int(r * scale)
            g = int(g * scale)
            b = int(b * scale)

        # Write format: [0xFF] [0x00] [R] [G] [B]
        cmd = bytes([0xFF, 0x00, r, g, b])
        await client.write_gatt_char(CHAR_STATE, cmd, response=True)

    async def _async_write_scene(
        self, client: BleakClient, scene_hex: str
    ) -> None:
        """Write scene command."""
        if len(scene_hex) != 10:
            _LOGGER.error("Invalid scene hex length: %s", scene_hex)
            return

        cmd = bytes.fromhex(scene_hex)
        await client.write_gatt_char(CHAR_STATE, cmd, response=True)

    async def _async_write_off(self, client: BleakClient) -> None:
        """Write off command."""
        # Set to black (RGB 0,0,0)
        cmd = bytes([0xFF, 0x00, 0x00, 0x00, 0x00])
        await client.write_gatt_char(CHAR_STATE, cmd, response=True)

    @property
    def is_on(self) -> bool:
        """Return if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int:
        """Return brightness (0-100)."""
        return self._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return RGB color."""
        return self._rgb_color

    @property
    def current_scene(self) -> str | None:
        """Return current scene hex if in scene mode."""
        return self._current_scene

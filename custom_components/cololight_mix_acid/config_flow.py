"""Config flow for Cololight Mix ACID integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_CUSTOM_SCENES, CONF_MAC_ADDRESS, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class CololightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cololight Mix ACID."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS]

            # Set unique ID to prevent duplicate entries
            await self.async_set_unique_id(mac_address.lower())
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_NAME, DEFAULT_NAME),
                data={
                    CONF_MAC_ADDRESS: mac_address,
                    CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                },
            )

        # Get discovered Bluetooth devices
        discovered_devices = {}
        for service_info in bluetooth.async_discovered_service_info(self.hass):
            if service_info.name and "MIX Acid" in service_info.name:
                discovered_devices[service_info.address] = service_info.name

        # Build device list for dropdown
        if discovered_devices:
            device_list = {
                addr: f"{name} ({addr})" for addr, name in discovered_devices.items()
            }
        else:
            device_list = {}

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_list)
                if device_list
                else str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        _LOGGER.debug("Discovered Cololight device: %s", discovery_info)

        address = discovery_info.address
        name = discovery_info.name or DEFAULT_NAME

        await self.async_set_unique_id(address.lower())
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": name}

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user confirmation of discovered device."""
        if user_input is not None:
            address = self.unique_id
            assert self._discovery_info is not None
            name = user_input.get(CONF_NAME, self._discovery_info.name or DEFAULT_NAME)

            return self.async_create_entry(
                title=name,
                data={
                    CONF_MAC_ADDRESS: address,
                    CONF_NAME: name,
                },
            )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME,
                        default=self._discovery_info.name
                        if self._discovery_info
                        else DEFAULT_NAME,
                    ): str,
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return CololightOptionsFlow(config_entry)


class CololightOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Cololight Mix ACID."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get existing custom scenes
        existing_scenes = self.config_entry.options.get(CONF_CUSTOM_SCENES, {})

        # Build text field with current scenes (one per line)
        scenes_text = "\n".join(
            [f"{name}:{hex_val}" for name, hex_val in existing_scenes.items()]
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CUSTOM_SCENES,
                        description={
                            "suggested_value": scenes_text,
                        },
                    ): str,
                }
            ),
            description_placeholders={
                "info": (
                    "Add custom scenes in the format:\n"
                    "SceneName:ff06891800\n"
                    "MyScene:ff01800900\n\n"
                    "One scene per line. Hex values must be 10 characters."
                )
            },
        )

from typing import Any
from homeassistant import config_entries, data_entry_flow
from homeassistant.data_entry_flow import FlowResult

import voluptuous as vol
from .const import (
    CONF_CITY,
    CONF_STREET,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
    DEFAULT_UPDATE_INTEVAL,
)

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STREET): str,
        vol.Required(CONF_CITY): str,
    }
)


class vmeabConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """vmeabConfigFlow"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

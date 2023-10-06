""" VMEAB Sophämtning """
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_CITY, CONF_STREET
from .coordinator import MyCoordinator

PLATFORMS = ["sensor", "text"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Called from Config Flow"""

    hass.data.setdefault(DOMAIN, {})

    StreetName = config_entry.data.get(CONF_STREET)
    City = config_entry.data.get(CONF_CITY)

    coordinator = MyCoordinator(hass, config_entry.data, StreetName, City)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    )

    # hass.async_create_task(
    #    hass.config_entries.async_forward_entry_setup(config_entry, "text")
    # )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        del hass.data[DOMAIN]

    return unload_ok

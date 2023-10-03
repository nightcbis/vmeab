import logging
import aiohttp
import json
import time
import asyncio

from datetime import timedelta
from pathlib import Path
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from bs4 import BeautifulSoup
from .const import DOMAIN, CONF_COORDINATOR_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_get_page(vmeab, URL):
    async with vmeab.get(URL) as page:
        text = await page.read()

    return BeautifulSoup(text, "html.parser")


async def async_post_page(vmeab, URL, data):
    async with vmeab.post(URL, data=data) as page:
        text = await page.read()

    return BeautifulSoup(text, "html.parser")


class MyCoordinator(DataUpdateCoordinator):
    """Coordinator som uppdaterar datan vi har"""

    def __init__(self, hass: HomeAssistant, my_api, StreetName, City) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="VMEAB Coordinator",
            update_interval=timedelta(seconds=int(CONF_COORDINATOR_UPDATE_INTERVAL)),
        )
        self.my_api = my_api
        self._street = StreetName
        self._city = City
        self._hass = hass
        self.tunnor = {}  # Unprotected

    async def _async_update_data(self):
        """Fetcha infon här."""
        # tunnor = vmeab_scrape("Flundregatan 29", "Västervik")

        URL = "https://www.vmeab.se/tjanster/avfall--atervinning/min-sophamtning/"
        HOSTURL = "https://www.vmeab.se"

        vmeab = aiohttp.ClientSession()
        get_page = asyncio.create_task(async_get_page(vmeab, URL))
        # soup = await async_get_page(vmeab, URL)
        soup = await get_page

        # Hittar formen för sökningen. Vi måste plocka ur en dold nyckel där med mera.
        form = soup.find(id="wasteDisposalNextPickupForm")

        # VMEAB har skapat en dold input som innehåller en nyckel som vi måste skicka i våran post.
        # Detta är för att hämta den.
        __RequestVerificationToken = form.find(type="hidden")["value"]

        # Ifall att de ändrar var API't ligger så hämtar vi den här varje gång.
        formAction = form["action"]
        formURL = HOSTURL + formAction

        # Detta är våran data för våran post
        data = {
            "__RequestVerificationToken": __RequestVerificationToken,
            "StreetAddress": self._street,
            "City": self._city,
        }

        # soup = await async_post_page(vmeab, formURL, data)
        post_page = asyncio.create_task(async_post_page(vmeab, formURL, data))
        soup = await post_page
        await vmeab.close()

        # Varje tunna ligger som en egen div med class waste-disposal-search-result-item
        allaTunnor = soup.find_all("div", class_="waste-disposal-search-result-item")

        tunnor = {}  # Använder json för att spara sakerna i.

        for tunna in allaTunnor:
            soup = BeautifulSoup(tunna.prettify(), "html.parser")

            # Lägger in varje träff som ett nytt inlägg i form av json
            tunnor[soup.find("h4").get_text().strip().split(",")[0]] = (
                soup.find("p").get_text().strip().split(": ")[1]
            )

        tunnor["last_update"] = time.time()
        self.tunnor = tunnor

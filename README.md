![maintained](https://img.shields.io/maintenance/yes/2023.svg)
[![hacs_badge](https://img.shields.io/badge/hacs-default-green.svg)](https://github.com/custom-components/hacs)
[![ha_version](https://img.shields.io/badge/home%20assistant-2023.10%2B-green.svg)](https://www.home-assistant.io)
![version](https://img.shields.io/badge/version-1.0.1-green.svg)
![stability-alpha](https://img.shields.io/badge/stability-stable-green.svg)
[![maintainer](https://img.shields.io/badge/maintainer-nightcbis-blue.svg)](https://github.com/DSorlov)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

VMEAB Sophantering / Västervik Miljö & Energi Sophantering
============================================

A small Integration to get the pickups of VMEAB Trash pickups
En liten Intregration som hämtar hämtningar av sopor ifrån VMEAB

## Install using HACS

* If you haven't already you must have [HACS installed](https://hacs.xyz/docs/setup/download).
* Go into HACS and search for Svensk Postutdelning under the Integrations headline. Install it. You will need to restart Home Assistant to finish the process.
* Once that is done, try to reload your GUI (caching issues could prevent the integration to be shown).
* Goto Integrations and add Svensk Postutdelning or Swedish Mail Delivery (depending on language)
* Enter postal code and select your providers
* Sensors are created and updated. Enjoy!
  - One sensor for each selected provider
  - An additional combined sensor regardless of provider

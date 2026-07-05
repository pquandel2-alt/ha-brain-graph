"""Brain Graph Integration: Live 3D entity relationship graph visualization."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    FRONTEND_URL,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL_PATH,
)

_LOGGER = logging.getLogger(__name__)
_FRONTEND_VERSION = "1.0.0"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_frontend(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    store = hass.data.get(DOMAIN, {})
    if store.get("panel_registered"):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
        store["panel_registered"] = False
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Register the Brain Graph panel and static assets."""
    store = hass.data[DOMAIN]

    # Register static files only once
    if not store.get("frontend_registered"):
        www = Path(__file__).parent / "www"
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(FRONTEND_URL, str(www / "brain-graph-panel.js"), False),
            ]
        )
        frontend.add_extra_js_url(hass, f"{FRONTEND_URL}?v={_FRONTEND_VERSION}")
        store["frontend_registered"] = True

    # Register or re-register the panel
    if store.get("panel_registered"):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)

    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name="brain-graph-panel",
        module_url=f"{FRONTEND_URL}?v={_FRONTEND_VERSION}",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=False,
        config={},
        embed_iframe=False,
    )
    store["panel_registered"] = True

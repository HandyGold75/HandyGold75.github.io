from WebKit import CSS, HTML, JS, WS, Module, Widget

__author__ = "HandyGold75"

__all__ = (
    "HTML",
    "CSS",
    "JS",
    "WS",
    "Widget",
    "Buttons",
    "PortalPage",
)

Buttons = Module.buttons()
WS = WS.WebSocket()

from WebKit.Pages import PortalPage

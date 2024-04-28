from os import path as osPath
from threading import Thread

from ..mod import fileManager, logger
from .Admin import admin
from .Sonos import sonos
from .Tapo import tapo
from .YTDL import ytdl

__all__ = "get"


def get(userData):
    coms = {
        "admin": {"class": admin, "kwargs": {"userData": userData}},
        "sonos": {"class": sonos, "kwargs": {}},
        "tapo": {"class": tapo, "kwargs": {"userData": userData}},
        "ytdl": {"class": ytdl, "kwargs": {"userData": userData}},
        "asset": {
            "class": fileManager,
            "kwargs": {
                "workFolder": f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{userData["Token"]}/AssetManager',
                "sheets": {
                    "Assignments": (("Name", str), ("Devices", list), ("Assets", list), ("Parts", list), ("Servers", list), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Devices": (("Name", str), ("Brand", str), ("Device", str), ("Series", str), ("S/N", str), ("MAC-WiFi", str), ("MAC-Eth", str), ("DOP", int), ("EOL", int), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Assets": (("Name", str), ("Brand", str), ("Asset", str), ("Series", str), ("S/N", str), ("DOP", int), ("EOL", int), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Parts": (("Name", str), ("Brand", str), ("Part", str), ("Series", str), ("S/N", str), ("DOP", int), ("EOL", int), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Servers": (("Name", str), ("Brand", str), ("Server", str), ("Series", str), ("S/N", str), ("MAC", str), ("DOP", int), ("EOL", int), ("Modified", float), ("Active", bool), ("Notes", str)),
                },
                "modifiedKey": "Modified",
            },
        },
        "license": {
            "class": fileManager,
            "kwargs": {
                "workFolder": f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{userData["Token"]}/LicenseManager',
                "sheets": {
                    "Assignments": (("Name", str), ("Licenses", list), ("Devices", list), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Licenses": (("Name", str), ("Product", str), ("Key", str), ("URL", str), ("DOP", int), ("EOL", int), ("Cost", float), ("Auto Renew", bool), ("Modified", float), ("Active", bool), ("Notes", str)),
                    "Devices": (("Name", str), ("Device", str), ("Modified", float), ("Active", bool), ("Notes", str)),
                },
                "modifiedKey": "Modified",
            },
        },
        "query": {
            "class": fileManager,
            "kwargs": {
                "workFolder": f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{userData["Token"]}/Query',
                "sheets": {
                    "Links": (("Img", list), ("url", str), ("text", str), ("cat", str), ("Index", int), ("Active", bool), ("Modified", float)),
                    "Contact": (("Img", list), ("url", str), ("text", str), ("Index", int), ("Active", bool), ("Modified", float)),
                },
                "modifiedKey": "Modified",
            },
        },
    }

    threads = []
    threadsReturns = {}
    for com in coms:
        threadsReturns[com] = [None]
        trd = Thread(target=coms[com]["class"], kwargs={**coms[com]["kwargs"], "return_var": threadsReturns[com]})
        trd.start()
        threads.append(trd)
    for trd in threads:
        trd.join()
    for name in threadsReturns:
        threadsReturns[name] = threadsReturns[name][0]

    return threadsReturns

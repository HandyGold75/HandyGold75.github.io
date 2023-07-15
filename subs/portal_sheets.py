from WebKit import HTML, CSS, JS, Widget
from WebKit.WebSocket import WS
from rsa import encrypt
from datetime import datetime, timedelta


class invoke:
    def AP(args=None):
        glb.lastUpdate = 0

        glb.knownFiles = {
            "/Config.json": {
                "IP": str,
                "PORT": int,
                "LogLevel": int,
                "SonosSubnet": list,
                "Debug": bool,
                "Modified": int
            },
            "/Tokens.json": {
                "Token": {
                    "User": str,
                    "Auth": int,
                    "Roles": list,
                    "Expires": int,
                    "Modified": int,
                    "Active": bool,
                    "TapoUser": str,
                    "Notes": str
                }
            },
            "/Server.log": {
                "Index": {
                    "Date/ Time": str,
                    "IP/ Port": str,
                    "Command": str,
                    "Status": str
                }
            }
        }

        glb.dates = ["Modified", "Expires"]
        glb.halfView = ["User", "Auth", "Expires", "Modified", "Active", "TapoUser", "Action", "Date/ Time", "IP/ Port", "Status"]
        glb.excludeView = ["Expires", "Modified", "TapoUser", "Notes"]
        glb.invokePswChange = {"User": "Password", "TapoUser": "TapoPassword"}
        glb.optionsDict = {"/Config.json": {"SonosSubnet": ["10.69.1.0/24", "10.69.2.0/24", "10.69.3.0/24", "10.69.4.0/24", "10.69.5.0/24"]}, "/Tokens.json": {"Roles": ["Admin", "Home"]}}
        glb.tagIsList = False
        glb.hideInput = True
        glb.svcoms = {"main": "admin", "read": "read", "add": "uadd", "modify": "modify", "rmodify": "tkmodify", "rpwmodify": "tkpwmodify", "kmodify": "kmodify", "kpwmodify": "kpwmodify", "delete": "delete", "clean": "clean"}
        glb.mainCom = "admin"
        glb.extraButtons = (("Add", "add", userAdd, True),("Clean", "clean", clean, True), ("Inactive", "active", pageSub, False), ("Expand", "compact", pageSub, False))

        getData()

    def AM(args=None):
        glb.lastUpdate = 0

        glb.knownFiles = {
            "/Assignments.json": {
                "User": {
                    "Devices": list,
                    "Assets": list,
                    "Servers": list,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            },
            "/Devices.json": {
                "Tag": {
                    "Brand": str,
                    "Device": str,
                    "Series": str,
                    "S/N": str,
                    "MAC-WiFi": str,
                    "MAC-Eth": str,
                    "DOP": int,
                    "EOL": int,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            },
            "/Assets.json": {
                "Tag": {
                    "Brand": str,
                    "Asset": str,
                    "Series": str,
                    "S/N": str,
                    "DOP": int,
                    "EOL": int,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            },
            "/Servers.json": {
                "Tag": {
                    "Brand": str,
                    "Server": str,
                    "Series": str,
                    "S/N": str,
                    "MAC": str,
                    "DOP": int,
                    "EOL": int,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            }
        }

        glb.dates = ["DOP", "EOL", "Modified"]
        glb.halfView = ["User", "Tag", "Brand", "Series", "Active", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Action"]
        glb.excludeView = ["S/N", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Notes"]
        glb.invokePswChange = {}
        glb.optionsDict = {}
        glb.tagIsList = False
        glb.hideInput = False
        glb.svcoms = {"main": "am", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "rpwmodify": "rpwmodify", "kmodify": "kmodify", "kpwmodify": "kpwmodify", "delete": "delete", "clean": "clean"}
        glb.mainCom = "am"
        glb.extraButtons = (("Bulk Add", "bulkadd", bulkAdd, False), ("Inactive", "active", pageSub, False), ("Expand", "compact", pageSub, False))

        getData()

    def LM(args=None):
        glb.lastUpdate = 0

        glb.knownFiles = {
            "/Assignments.json": {
                "Tag": {
                    "Licenses": list,
                    "Devices": list,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            },
            "/Devices.json": {
                "Tag": {
                    "Device": str,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            },
            "/Licenses.json": {
                "Tag": {
                    "Product": str,
                    "Key": str,
                    "URL": str,
                    "DOP": int,
                    "EOL": int,
                    "Cost": float,
                    "Auto Renew": bool,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            }
        }

        glb.dates = ["DOP", "EOL", "Modified"]
        glb.halfView = ["Tag", "DOP", "EOL", "Cost", "Auto Renew", "Modified", "Active", "Action"]
        glb.excludeView = ["DOP", "EOL", "Cost", "Auto Renew", "Modified", "Notes"]
        glb.invokePswChange = {}
        glb.optionsDict = {}
        glb.tagIsList = False
        glb.hideInput = False
        glb.svcoms = {"main": "lm", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "rpwmodify": "rpwmodify", "kmodify": "kmodify", "kpwmodify": "kpwmodify", "delete": "delete", "clean": "clean"}
        glb.mainCom = "lm"
        glb.extraButtons = (("Bulk Add", "bulkadd", bulkAdd, False), ("Inactive", "active", pageSub, False), ("Expand", "compact", pageSub, False))

        getData()

    def QR(args=None):
        glb.lastUpdate = 0

        glb.knownFiles = {"/Links.json": {"Tag": {"url": str, "text": str, "cat": str, "Index": int, "Active": bool, "Modified": int}}, "/Contact.json": {"Tag": {"url": str, "text": str, "Index": int, "Active": bool, "Modified": int}}}
        glb.dates = ["Modified"]
        glb.halfView = ["Index", "Modified", "Active", "Action"]
        glb.excludeView = ["Index", "Modified"]
        glb.invokePswChange = {}
        glb.optionsDict = {
            "/Links.json": {
                "Tag": [
                    "Bol.png", "CloudConvert.png", "Cloudflare.png", "Dell.png", "DownDetector.png", "G-Calendar.png", "G-Drive.png", "GitHub.png", "G-Mail.png", "G-Photos.png", "Linode.png", "LinusTechTips.png", "Megekko.png", "M365.png", "Nord.png",
                    "NS.png", "OneDrive.png", "OneTimeSecret.png", "Outlook.png", "OutlookCalendar.png", "RockStar.png", "SokPop.png", "Sophos.png", "SpeedTest.png", "Spotify.png", "UniFi.png", "Vodafone.png", "YouTube.png", "YouTubeMusic.png",
                    "Zwoofs.png"
                ]
            },
            "/Contact.json": {
                "Tag": ["discord.png", "exchange.png", "snapchat.png", "spotify.png", "steam.png", "twitch.png", "youtube.png"]
            }
        }
        glb.tagIsList = True
        glb.hideInput = False
        glb.maincoms = {"Admin": "admin", "Asset Manager": "am", "License Manager": "lm", "Query": "qr"}
        glb.svcoms = {"main": "qr", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "rpwmodify": "rpwmodify", "kmodify": "kmodify", "kpwmodify": "kpwmodify", "delete": "delete", "clean": "clean"}
        glb.mainCom = "qr"
        glb.extraButtons = (("Inactive", "active", pageSub, False), ("Expand", "compact", pageSub, False))

        getData()


class glb:
    lastUpdate = 0
    compactView = None
    hideInactive = None

    knownFiles = {}
    dates = []
    halfView = []
    excludeView = []
    invokePswChange = []
    optionsDict = []
    tagIsList = None
    hideInput = None
    maincoms = {}
    svcoms = {}
    mainCom = ""
    extraButtons = ()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        for file in glb.knownFiles:
            WS.send(f'{glb.mainCom} read {file}')

        glb.lastUpdate = datetime.now().timestamp()


def userAdd(args):
    if JS.cache("page_portalSub") == "":
        return None

    WS.onMsg("{\"" + glb.mainCom + "\":", pageSub, oneTime=True)
    WS.send(f'{glb.mainCom} uadd {JS.cache("page_portalSub").replace(" ", "%20")}')


def bulkAdd(args):
    if JS.cache("page_portalSub") == "":
        return None

    prefix = JS.popup(f'prompt', "Prefix")
    amount = JS.popup(f'prompt', "Amount")

    if prefix is None or amount is None:
        return None

    try:
        amount = int(amount)
    except ValueError:
        JS.popup(f'alert', "Please enter a rounded number!")
        return None

    if JS.popup(f'confirm', f'Records with token "{prefix}{"0" * 2}" to "{prefix}{"0" * (2 - len(str(amount - 1)))}{amount - 1}" will be created!\nDo you want to continue?'):
        for i in range(0, amount):
            WS.onMsg("{\"" + glb.mainCom + "\":", pageSub, oneTime=True)
            WS.send(f'{glb.mainCom} add {JS.cache("page_portalSub").replace(" ", "%20")} {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')


def clean(args):
    def cleanResults():
        JS.popup("alert", f'Cleaning results:\n{chr(10).join(WS.dict()["admin"]["Cleaned"])}')

    if JS.popup("confirm", "Are you sure you want to clean?\nThis will delete all data of no longer existing users and making it imposable to recover this data!"):
        WS.onMsg("{\"" + glb.mainCom + "\":", cleanResults, oneTime=True)
        WS.send(f'{glb.mainCom} clean')


def pageSub(args=None):
    def setup(args):
        data = WS.dict()[glb.mainCom]
        file = JS.cache("page_portalSub")

        if not args is None:
            if args.target.id.split("_")[-1] == "compact":
                glb.compactView = not glb.compactView
                if glb.compactView:
                    CSS.setAttribute(args.target.id, "innerHTML", "Expand")
                else:
                    CSS.setAttribute(args.target.id, "innerHTML", "Compact")

            elif args.target.id.split("_")[-1] == "active":
                glb.hideInactive = not glb.hideInactive
                if glb.hideInactive:
                    CSS.setAttribute(args.target.id, "innerHTML", "Inactive")
                else:
                    CSS.setAttribute(args.target.id, "innerHTML", "Active")

            elif f'{args.target.id.split("_")[-1]}' in glb.knownFiles:
                file = f'{args.target.id.split("_")[-1]}'
                JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

            elif f'{args.target.id.split("_")[-1]}' in glb.knownFiles:
                file = f'{args.target.id.split("_")[-1]}'
                JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

        if not file in data:
            return None

        data = data[file]

        if data == {}:
            data[" "] = {}
            mainValue = list(glb.knownFiles[file])[-1]
            data[" "] = {}

            for value in glb.knownFiles[file][mainValue]:
                data[" "][value] = glb.knownFiles[file][mainValue][value]()

        for butTxt, butId, butFunc, butAct in glb.extraButtons:
            if not butAct:
                HTML.disableElement(f'SubPage_nav_options_{butId}')

        if glb.knownFiles[file] is str:
            return data

        if type(glb.knownFiles[file][list(glb.knownFiles[file])[-1]]) is dict:
            for butTxt, butId, butFunc, butAct in glb.extraButtons:
                HTML.enableElement(f'SubPage_nav_options_{butId}')

        return data

    HTML.clrElement(f'SubPage_page')

    data = setup(args)
    if data is None:
        return None

    elif type(data) is str:
        dataTemp, data = (data, {})

        for i1, line in enumerate(reversed(dataTemp.split("\n"))):
            if line == "":
                continue

            data[i1], lineSplit = ({}, line.split("%S%"))
            for i2, key in enumerate(dict(glb.knownFiles[JS.cache("page_portalSub")][list(glb.knownFiles[JS.cache("page_portalSub")])[-1]])):
                try:
                    data[i1][key] = lineSplit[i2]
                except IndexError:
                    data[i1][key] = ""

        def doAction():
            Widget.sheet(
                maincom=glb.maincoms[JS.cache("page_portal")],
                name=JS.cache("page_portalSub"),
                data=dict(data),
                elId="SubPage_page",
                dates=tuple(glb.dates),
                halfView=list(glb.halfView),
                excludeView=(lambda: list(glb.excludeView) if glb.compactView else [])() + (lambda: ["Active"] if glb.hideInactive else [])(),
                typeDict=dict(glb.knownFiles[JS.cache("page_portalSub")][list(glb.knownFiles[JS.cache("page_portalSub")])[-1]]),
                showInput=False,
                showAction=False,
                showTag=False,
            )

        JS.aSync(doAction)

    elif type(data[list(data)[-1]]) is not dict:
        dataTemp, data = (data, {})

        for i, key in enumerate(dict(glb.knownFiles[JS.cache("page_portalSub")])):
            data[key] = {}
            try:
                data[key]["Value"] = dataTemp[key]
            except IndexError:
                data[key]["Value"] = ""

        options = (lambda: {**dict(WS.dict()[glb.mainCom]), **dict(glb.optionsDict[JS.cache("page_portalSub")])} if JS.cache("page_portalSub") in glb.optionsDict else dict(WS.dict()[glb.mainCom]))()

        htmlStr, eventConfig = Widget.sheet(
            maincom=glb.maincoms[JS.cache("page_portal")],
            name=JS.cache("page_portalSub"),
            data=dict(data),
            dates=tuple(glb.dates),
            halfView=list(glb.halfView),
            excludeView=(lambda: list(glb.excludeView) if glb.compactView else [])() + (lambda: ["Active"] if glb.hideInactive else [])(),
            typeDict=dict(glb.knownFiles[JS.cache("page_portalSub")]),
            optionsDict=options,
            showInput=False,
            showAction=False,
        )
        HTML.setElementRaw("SubPage_page", htmlStr)
        JS.afterDelay(lambda: Widget.sheetMakeEvents(eventConfig, optionsDict=options, pswChangeDict=glb.invokePswChange, sendKey=False), 50)

    else:
        if glb.hideInactive:
            for key in dict(data):
                if not "Active" in data[key] or key == " " or len(data) < 2:
                    continue
                elif not data[key]["Active"]:
                    data.pop(key)

        options = (lambda: {**dict(WS.dict()[glb.mainCom]), **dict(glb.optionsDict[JS.cache("page_portalSub")])} if JS.cache("page_portalSub") in glb.optionsDict else dict(WS.dict()[glb.mainCom]))()

        htmlStr, eventConfig = Widget.sheet(
            maincom=glb.maincoms[JS.cache("page_portal")],
            name=JS.cache("page_portalSub"),
            data=dict(data),
            dates=tuple(glb.dates),
            halfView=list(glb.halfView),
            excludeView=(lambda: list(glb.excludeView) if glb.compactView else [])() + (lambda: ["Active"] if glb.hideInactive else [])(),
            typeDict=dict(glb.knownFiles[JS.cache("page_portalSub")][list(glb.knownFiles[JS.cache("page_portalSub")])[-1]]),
            optionsDict=options,
            showInput=(not glb.hideInput),
            tagIsList=glb.tagIsList,
        )
        HTML.setElementRaw("SubPage_page", htmlStr)
        JS.afterDelay(lambda: Widget.sheetMakeEvents(eventConfig, optionsDict=options, pswChangeDict=glb.invokePswChange), 50)


def main(args=None, sub=None):
    data = WS.dict()[glb.mainCom]
    glb.hideInactive = True
    glb.compactView = True

    btn = ""
    for file in data:
        if not file in glb.knownFiles:
            continue
        btn += HTML.genElement(f'button', nest=f'{file.replace("/", "").replace(".json", "").replace(".log", "")}', id=f'SubPage_nav_main_{file}', type=f'button', style=f'buttonSmall')

    if btn == "":
        txt = HTML.genElement(f'h2', nest=f'Unauthorized!', style=f'margin: 10px auto; text-align: center;')
        HTML.setElement(f'div', f'SubPage', id=f'SubPage_nav_main', nest=txt, align=f'center', style=f'width: 100%;')
        HTML.disableElement(f'page_portal_{JS.cache(f"page_portal")}')
        return None

    div = HTML.genElement(f'div', id=f'SubPage_nav_main', nest=btn, align=f'left', style=f'width: 60%;"')

    btn = ""
    for butTxt, butId, butFunc, butAct in glb.extraButtons:
        btn += HTML.genElement(f'button', nest=f'{butTxt}', id=f'SubPage_nav_options_{butId}', type=f'button', align=f'right', style=f'buttonSmall')

    div += HTML.genElement(f'div', id=f'SubPage_nav_options', nest=btn, align=f'right', style=f'width: 40%;')

    mainDiv = HTML.genElement(f'div', id=f'SubPage_nav', nest=div, align=f'center', style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    mainDiv += HTML.genElement(f'div', id=f'SubPage_page', align=f'center', style=f'margin: 10px 10px 10px 0px;')
    HTML.setElementRaw(f'SubPage', mainDiv)

    for file in data:
        if not file in glb.knownFiles:
            continue

        JS.addEvent(f'SubPage_nav_main_{file}', pageSub)
        JS.addEvent(f'SubPage_nav_main_{file}', getData, f'mousedown')
        CSS.onHoverClick(f'SubPage_nav_main_{file}', f'buttonHover', f'buttonClick')

    for butTxt, butId, butFunc, butAct in glb.extraButtons:
        JS.addEvent(f'SubPage_nav_options_{butId}', butFunc)
        CSS.onHoverClick(f'SubPage_nav_options_{butId}', f'buttonHover', f'buttonClick')

        if not butAct:
            HTML.disableElement(f'SubPage_nav_options_{butId}')

    if sub is not None:
        JS.cache("page_portalSub", f'{sub}')
        pageSub(args)

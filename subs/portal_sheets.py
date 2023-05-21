from WebKit import HTML, CSS, JS, WS, widgets
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
        glb.invokePasswordOnChange = ["User", "TapoUser"]
        glb.optionsDict = {"/Tokens.json": {"Roles": ["Admin", "Home"]}}
        glb.tagIsList = False
        glb.svcoms = {"main": "admin", "read": "read", "add": "uadd", "modify": "modify", "rmodify": "tkmodify", "rpwmodify": "tkpwmodify", "kmodify": "kmodify", "kpwmodify": "kpwmodify", "delete": "delete", "clean": "clean"}
        glb.mainCom = "admin"
        glb.extraButtons = (("Clean", "clean", clean, True), ("Inactive", "active", pageSub, False), ("Expand", "compact", pageSub, False))

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
        glb.invokePasswordOnChange = []
        glb.optionsDict = {}
        glb.tagIsList = False
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
        glb.invokePasswordOnChange = []
        glb.optionsDict = {}
        glb.tagIsList = False
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
        glb.invokePasswordOnChange = []
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
    invokePasswordOnChange = []
    optionsDict = []
    tagIsList = None
    maincoms = {}
    svcoms = {}
    mainCom = ""
    extraButtons = ()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        for file in glb.knownFiles:
            WS.send(f'{glb.mainCom} {glb.svcoms["read"]} {file}')

        glb.lastUpdate = datetime.now().timestamp()


def editRecord(args):
    def submit(args):
        if not args.key in ["Enter", "Escape"]:
            return None

        el = HTML.get(f'{args.target.id}')

        if "_" in el.id:
            mainValue = list(glb.knownFiles[JS.cache("page_portalSub")])[-1]
            knownValues = glb.knownFiles[JS.cache("page_portalSub")][mainValue]
            value = el.id.split("_")[1]

        else:
            mainValue = None
            knownValues = glb.knownFiles[JS.cache("page_portalSub")]
            value = el.id

        data = el.value.replace(" ", "%20")
        width = el.style.width

        if el.localName == "select":
            width = f'{float(width.replace("%", "")) - 0.5}%'

        if data == "":
            data = "%20"

        styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'
        html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{data.replace("%20", " ")}</p>'

        if value in knownValues:
            if knownValues[value] is int:
                if value in glb.dates:
                    data = int(datetime.strptime(data, "%Y-%m-%d").timestamp())
                    html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{datetime.fromtimestamp(data).strftime("%d %b %y")}</p>'
                else:
                    try:
                        data = int(data)
                    except ValueError:
                        JS.popup(f'alert', f'{data} is not a number!\nPlease enter a valid number.')
                        return None

            elif knownValues[value] is float:
                try:
                    data = float(data)
                except ValueError:
                    JS.popup(f'alert', f'{data} is not a number!\nPlease enter a valid number.')
                    return None

            elif knownValues[value] is list:
                data = []

                for i in range(0, int(args.target.name.split("_")[1])):
                    if args.target.item(i).selected is True:
                        data.append(args.target.item(i).value)

                data = ", ".join(data).replace(" ", "%20")
                html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{data.replace("%20", " ")}</p>'

        if value in glb.invokePasswordOnChange:
            password = JS.popup(f'prompt', "Please enter the new password for the user.")

            if password is None:
                return None

            if value != "User":
                password = str(encrypt(password.encode(), WS.PK)).replace(" ", "%20")
            else:
                password = str(encrypt(data.encode() + "<SPLIT>".encode() + password.encode(), WS.PK)).replace(" ", "%20")

            if not mainValue is None:
                WS.send(f'{glb.mainCom} {glb.svcoms["rpwmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {el.id.split("_")[0].replace(" ", "%20")} {value.replace("User", "")}Password {password}')
            else:
                WS.send(f'{glb.mainCom} {glb.svcoms["kpwmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {value.replace("User", "")}Password {password}')

        if not mainValue is None:
            WS.send(f'{glb.mainCom} {glb.svcoms["rmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} {data}')
        else:
            WS.send(f'{glb.mainCom} {glb.svcoms["kmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {value.replace(" ", "%20")} {data}')

        el.outerHTML = html

        CSS.setStyle(f'{el.id}', f'width', f'{width}')

        JS.addEvent(el.id, editRecord, "dblclick")

    el = HTML.get(f'{args.target.id}')
    width = el.style.width
    parantHeight = HTML.get(el.parentElement.id).offsetHeight

    if "_" in el.id:
        value = el.id.split("_")[1]
        mainValue = list(glb.knownFiles[JS.cache("page_portalSub")])[-1]
        knownValues = glb.knownFiles[JS.cache("page_portalSub")][mainValue]

    else:
        value = el.id
        mainValue = None
        knownValues = glb.knownFiles[JS.cache("page_portalSub")]

    if el.innerHTML == " ":
        el.innerHTML = ""

    styleInp = f'margin: -1px -1px; padding: 1px 1px 4px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
    styleSlc = f'height: {parantHeight + 4}px; margin: -1px -1px; padding: 1px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
    html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{el.innerHTML}"')

    if value in knownValues:
        if knownValues[value] is int:
            if value in glb.dates:
                html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'date', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{datetime.strptime(el.innerHTML, "%d %b %y").strftime("%Y-%m-%d")}"')
            else:
                html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{el.innerHTML}"')

        elif knownValues[value] is bool:
            if el.innerHTML == "No":
                if not mainValue is None:
                    WS.send(f'{glb.mainCom} {glb.svcoms["rmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} True')
                else:
                    WS.send(f'{glb.mainCom} {glb.svcoms["kmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {value.replace(" ", "%20")} True')

                el.innerHTML = "Yes"
                return None

            if not mainValue is None:
                WS.send(f'{glb.mainCom} {glb.svcoms["rmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} False')
            else:
                WS.send(f'{glb.mainCom} {glb.svcoms["kmodify"]} {JS.cache("page_portalSub").replace(" ", "%20")} {value.replace(" ", "%20")} False')

            el.innerHTML = "No"
            return None

        elif knownValues[value] is list:
            if glb.optionsDict[JS.cache("page_portalSub")] == []:
                data = WS.dict()[glb.mainCom][f'{el.id.split("_")[1]}']
            else:
                data = glb.optionsDict[JS.cache("page_portalSub")]

            optionsHtml = f''

            for option in data:
                optionsHtml += HTML.add(f'option', _nest=f'{option}', _custom=f'value="{option}"')

            html = HTML.add(f'select', _nest=f'{optionsHtml}', _id=f'{el.id}', _class=f'{el.className}', _style=f'selectSmall %% {styleSlc}', _custom=f'name="{value}_{len(data)}" size="1" multiple')

    el.outerHTML = html

    el = HTML.get(f'{el.id}')
    el.style.width = width

    if el.localName == "select":
        el.style.width = f'{float(width.replace("%", "")) + 0.5}%'
        CSS.onHoverFocus(el.id, f'selectHover %% margin-bottom: { - 105 + parantHeight}px;', f'selectFocus %% margin-bottom: { - 105 + parantHeight}px;')
    else:
        CSS.onHoverFocus(el.id, f'inputHover', f'inputFocus')

    JS.addEvent(el.id, submit, "keyup")


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
            if glb.svcoms["add"] == "uadd":
                WS.send(f'{glb.mainCom} {glb.svcoms["add"]} {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')
                continue

            WS.onMsg("{\"" + glb.mainCom + "\":", pageSub, oneTime=True)
            WS.send(f'{glb.mainCom} {glb.svcoms["add"]} {JS.cache("page_portalSub").replace(" ", "%20")} {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')


def clean(args):
    def cleanResults():
        JS.popup("alert", f'Cleaning results:\n{chr(10).join(WS.dict()["admin"]["Cleaned"])}')

    if JS.popup("confirm", "Are you sure you want to clean?\nThis will delete all data of no longer existing users and making it imposable to recover this data!"):
        WS.onMsg("{\"admin\":", cleanResults, oneTime=True)
        WS.send(f'{glb.mainCom} {glb.svcoms["clean"]}')


def pageSub(args=None):
    def setup(args):
        data = WS.dict()[glb.mainCom]
        file = JS.cache("page_portalSub")

        if not args is None:
            if args.target.id.split("_")[-1] == "compact":
                glb.compactView = not glb.compactView

                el = HTML.get(f'{args.target.id}')

                if glb.compactView:
                    el.innerHTML = "Expand"
                else:
                    el.innerHTML = "Compact"

            elif args.target.id.split("_")[-1] == "active":
                glb.hideInactive = not glb.hideInactive

                el = HTML.get(f'{args.target.id}')

                if glb.hideInactive:
                    el.innerHTML = "Inactive"
                else:
                    el.innerHTML = "Active"

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
                HTML.enable(f'SubPage_nav_options_{butId}', False)

        if glb.knownFiles[file] is str:
            return data

        if type(glb.knownFiles[file][list(glb.knownFiles[file])[-1]]) is dict:
            for butTxt, butId, butFunc, butAct in glb.extraButtons:
                HTML.enable(f'SubPage_nav_options_{butId}', True)

        return data

    def addMinimal(data):
        def addHeader():
            rowC = 0
            HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

            styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

            for header in ["Key", "Value"]:
                HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{header}', _class=f'SubPage_page_keys', _style=f'{styleP}')

            return rowC

        def addRows(data, rowC):
            knownValues = glb.knownFiles[JS.cache("page_portalSub")]
            styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

            HTMLrows = f''
            for key in data:
                rowC += 1
                HTMLcols = HTML.add(f'p', _nest=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')
                value = data[key]

                if knownValues[key] is int:
                    if key in glb.dates:
                        HTMLcols += HTML.add(f'p', _nest=f'{datetime.fromtimestamp(value).strftime("%d %b %y")}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    else:
                        HTMLcols += HTML.add(f'p', _nest=f'{value}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                elif knownValues[key] is bool:
                    if value:
                        HTMLcols += HTML.add(f'p', _nest=f'Yes', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    else:
                        HTMLcols += HTML.add(f'p', _nest=f'No', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                elif knownValues[key] is list:
                    HTMLcols += HTML.add(f'p', _nest=f'{", ".join(value)}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                else:
                    HTMLcols += HTML.add(f'p', _nest=f'{value}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                HTMLrows += HTML.add(f'div', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

            HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

            return rowC

        rowC = addHeader()
        rowC = addRows(data, rowC)

        for item in HTML.get(f'SubPage_page_keys', isClass=True):
            item.style.width = "50%"

        for item in HTML.get(f'SubPage_page_keys', isClass=True):
            if item.id != "":
                JS.addEvent(item, editRecord, "dblclick", isClass=True)

    HTML.clear(f'SubPage_page')

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
            widgets.sheet(maincom=glb.maincoms[JS.cache("page_portal")],
                          name=JS.cache("page_portalSub"),
                          data=dict(data),
                          elId="SubPage_page",
                          dates=tuple(glb.dates),
                          halfView=list(glb.halfView),
                          excludeView=(lambda: list(glb.excludeView) if glb.compactView else [])() + (lambda: ["Active"] if glb.hideInactive else [])(),
                          typeDict=dict(glb.knownFiles[JS.cache("page_portalSub")][list(glb.knownFiles[JS.cache("page_portalSub")])[-1]]),
                          showAddRem=False,
                          showTag=False)

        JS.aSync(doAction)

    elif type(data[list(data)[-1]]) is not dict:
        addMinimal(data)
        return None

    else:
        if glb.hideInactive:
            for key in dict(data):
                if not "Active" in data[key] or key == " " or len(data) < 2:
                    continue
                elif not data[key]["Active"]:
                    data.pop(key)

        htmlStr, eventConfig = widgets.sheet(
            maincom=glb.maincoms[JS.cache("page_portal")],
            name=JS.cache("page_portalSub"),
            data=dict(data),
            dates=tuple(glb.dates),
            halfView=list(glb.halfView),
            excludeView=(lambda: list(glb.excludeView) if glb.compactView else [])() + (lambda: ["Active"] if glb.hideInactive else [])(),
            typeDict=dict(glb.knownFiles[JS.cache("page_portalSub")][list(glb.knownFiles[JS.cache("page_portalSub")])[-1]]),
            optionsDict=(lambda: {
                **dict(WS.dict()[glb.mainCom]),
                **dict(glb.optionsDict[JS.cache("page_portalSub")])
            } if JS.cache("page_portalSub") in glb.optionsDict else dict(WS.dict()[glb.mainCom]))(),
            tagIsList=glb.tagIsList,
        )
        HTML.setRaw("SubPage_page", htmlStr)
        JS.afterDelay(lambda: widgets.sheetMakeEvents(eventConfig), 50)


def main(args=None, sub=None):
    data = WS.dict()[glb.mainCom]
    glb.hideInactive = True
    glb.compactView = True

    btn = ""
    for file in data:
        if not file in glb.knownFiles:
            continue
        btn += HTML.add(f'button', _nest=f'{file.replace("/", "").replace(".json", "").replace(".log", "")}', _id=f'SubPage_nav_main_{file}', _type=f'button', _style=f'buttonSmall')

    if btn == "":
        txt = HTML.add(f'h2', _nest=f'Unauthorized!', _style=f'margin: 10px auto; text-align: center;')
        HTML.set(f'div', f'SubPage', _id=f'SubPage_nav_main', _nest=txt, _align=f'center', _style=f'width: 100%;')
        HTML.enable(f'page_portal_{JS.cache(f"page_portal")}', False)
        return None

    div = HTML.add(f'div', _id=f'SubPage_nav_main', _nest=btn, _align=f'left', _style=f'width: 60%;"')

    btn = ""
    for butTxt, butId, butFunc, butAct in glb.extraButtons:
        btn += HTML.add(f'button', _nest=f'{butTxt}', _id=f'SubPage_nav_options_{butId}', _type=f'button', _align=f'right', _style=f'buttonSmall')

    div += HTML.add(f'div', _id=f'SubPage_nav_options', _nest=btn, _align=f'right', _style=f'width: 40%;')

    mainDiv = HTML.add(f'div', _id=f'SubPage_nav', _nest=div, _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    mainDiv += HTML.add(f'div', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')
    HTML.setRaw(f'SubPage', mainDiv)

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
            HTML.enable(f'SubPage_nav_options_{butId}', False)

    if sub is not None:
        JS.cache("page_portalSub", f'{sub}')
        pageSub(args)

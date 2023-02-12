import mod.ws as ws
import mod.functions as f
import mod.HTML as HTML
import mod.CSS as CSS
from rsa import encrypt
from datetime import datetime, timedelta


class invoke:
    def AP(args=None):
        glb.mainPage = "Admin"
        glb.currentSub = ""

        glb.lastUpdate = 0
        glb.knownFiles = {
            "/Config.json": {
                "IP": str,
                "PORT": int,
                "LogLevel": int,
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
                    "Notes": str
                }
            },
            "/Logs.dmp": str,
        }

        glb.dates = ["Modified", "Expires"]

        glb.halfView = ["User", "Auth", "Expires", "Modified", "Active", "Action"]
        glb.compactView = False

        glb.excludeView = ["Expires", "Modified", "Notes"]
        glb.hideInactive = False

        glb.disabledInputs = ["Token", "User", "Auth", "Roles", "Expires", "Modified", "Active", "Notes"]
        glb.invokePasswordOnChange = ["User"]

        glb.optionsList = ["Admin", "Home", "Asset Manager", "License Manager"]

        glb.svcoms = {"main": "admin", "read": "read", "add": "uadd", "modify": "modify", "rmodify": "tkmodify", "kmodify": "kmodify", "delete": "delete"}

        getData()

    def AM(args=None):
        glb.mainPage = "Asset Manager"
        glb.currentSub = ""

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
        glb.compactView = False

        glb.excludeView = ["S/N", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Notes"]
        glb.hideInactive = False

        glb.disabledInputs = ["Modified"]
        glb.invokePasswordOnChange = []

        glb.optionsList = []

        glb.svcoms = {"main": "am", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "kmodify": "kmodify", "delete": "delete"}

        getData()

    def LM(args=None):
        glb.mainPage = "License Manager"
        glb.currentSub = ""

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
                    "Cost": int,
                    "Auto Renew": bool,
                    "Modified": int,
                    "Active": bool,
                    "Notes": str
                }
            }
        }

        glb.dates = ["DOP", "EOL", "Modified"]

        glb.halfView = ["Tag", "DOP", "EOL", "Cost", "Auto Renew", "Modified", "Active", "Action"]
        glb.compactView = False

        glb.excludeView = ["DOP", "EOL", "Cost", "Auto Renew", "Modified", "Notes"]
        glb.hideInactive = False

        glb.disabledInputs = ["Modified"]
        glb.invokePasswordOnChange = []

        glb.optionsList = []

        glb.svcoms = {"main": "lm", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "kmodify": "kmodify", "delete": "delete"}

        getData()


class glb:
    mainPage = ""
    currentSub = ""

    lastUpdate = 0
    knownFiles = {}

    dates = []

    halfView = []
    compactView = None

    excludeView = []
    hideInactive = None

    disabledInputs = []
    invokePasswordOnChange = []

    optionsList = []

    svcoms = {}
    logsLoaded = 0


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        try:
            for file in glb.knownFiles:
                ws.send(f'{glb.svcoms["main"]} {glb.svcoms["read"]} {file}')
        except ConnectionError:
            f.connectionError()

        glb.lastUpdate = datetime.now().timestamp()


def addRecord(args):
    if glb.svcoms["add"] == "uadd":
        try:
            ws.send(f'{glb.svcoms["main"]} {glb.svcoms["add"]} /{glb.currentSub.replace(" ", "%20")}.json')
        except ConnectionError:
            f.connectionError()

        f.popup(f'alert', f'New user created.\nReload the subpage for changes to appear.')

        return None

    token = ""
    data = {}

    mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
    knownValues = glb.knownFiles[f'/{glb.currentSub}.json'][mainValue]

    for item in HTML.get(f'SubPage_page_new', isClass=True):
        name = str(item.name.split("_")[0])
        value = str(item.value)

        if name == mainValue and ("_" in value):
            f.popup(f'alert', f'Invalid format for "{name}"!\n"{name}" may not include underscores ("_").')
            return None

        if name in knownValues:
            if knownValues[name] is int:
                if value == "":
                    value = 0

                if name in glb.dates:
                    value = int(datetime.now().timestamp())

                    if item.value != "":
                        value = int(datetime.strptime(item.value, "%Y-%m-%d").timestamp())
                else:
                    value = int(value)

            elif knownValues[name] is bool:
                value = bool(item.checked)

            elif knownValues[name] is list:
                value = []

                for i1 in range(0, int(item.name.split("_")[1])):
                    if item.item(i1).selected is True:
                        value.append(item.item(i1).value)

            elif item.value == "":
                value = knownValues[name]()
            else:
                value = knownValues[name](item.value)

        if name == mainValue:
            token = value
            data[token] = {}

            for knownValue in knownValues:
                if knownValue != mainValue:
                    if knownValues[knownValue] is bool:
                        data[token][knownValue] = not knownValues[knownValue]()
                        continue

                    data[token][knownValue] = knownValues[knownValue]()
            continue

        data[token][name] = value

    try:
        ws.send(f'{glb.svcoms["main"]} {glb.svcoms["add"]} /{glb.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")}')
        ws.send(f'{glb.svcoms["main"]} {glb.svcoms["modify"]} /{glb.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")} {str(data).replace(" ", "%20").replace("False", "false").replace("True", "true")}')
    except ConnectionError:
        f.connectionError()

    pageSub(args, {f'/{glb.currentSub}.json': data})


def editRecord(args):
    def submit(args):
        if not args.key in ["Enter", "Escape"]:
            return None

        el = HTML.get(f'{args.target.id}')

        if "_" in el.id:
            mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
            knownValues = glb.knownFiles[f'/{glb.currentSub}.json'][mainValue]
            value = el.id.split("_")[1]

        else:
            mainValue = None
            knownValues = glb.knownFiles[f'/{glb.currentSub}.json']
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
                        f.popup(f'alert', f'{data} is not a number!\nPlease enter a valid number.')
                        return None

            elif knownValues[value] is list:
                data = []

                for i in range(0, int(args.target.name.split("_")[1])):
                    if args.target.item(i).selected is True:
                        data.append(args.target.item(i).value)

                data = ", ".join(data).replace(" ", "%20")
                html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{data.replace("%20", " ")}</p>'

        if value in glb.invokePasswordOnChange:
            password = f.popup(f'prompt', "Please enter the new password for the user.")

            if password is None:
                return None

            password = str(encrypt(data.encode() + "<SPLIT>".encode() + password.encode(), f.glb.pk)).replace(" ", "%20")
            try:
                if not mainValue is None:
                    ws.send(f'{glb.svcoms["main"]} {glb.svcoms["rmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {el.id.split("_")[0].replace(" ", "%20")} Password {password}')
                else:
                    ws.send(f'{glb.svcoms["main"]} {glb.svcoms["kmodify"]} /{glb.currentSub.replace(" ", "%20")}.json Password {password}')
            except ConnectionError:
                f.connectionError()

        try:
            if not mainValue is None:
                ws.send(f'{glb.svcoms["main"]} {glb.svcoms["rmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} {data}')
            else:
                ws.send(f'{glb.svcoms["main"]} {glb.svcoms["kmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {value.replace(" ", "%20")} {data}')
        except ConnectionError:
            f.connectionError()

        el.outerHTML = html

        CSS.setStyle(f'{el.id}', f'width', f'{width}')

        f.addEvent(el.id, editRecord, "dblclick")

    el = HTML.get(f'{args.target.id}')
    width = el.style.width
    parantHeight = HTML.get(el.parentElement.id).offsetHeight

    if "_" in el.id:
        value = el.id.split("_")[1]
        mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
        knownValues = glb.knownFiles[f'/{glb.currentSub}.json'][mainValue]

    else:
        value = el.id
        mainValue = None
        knownValues = glb.knownFiles[f'/{glb.currentSub}.json']

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
                try:
                    if not mainValue is None:
                        ws.send(f'{glb.svcoms["main"]} {glb.svcoms["rmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} True')
                    else:
                        ws.send(f'{glb.svcoms["main"]} {glb.svcoms["kmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {value.replace(" ", "%20")} True')
                except ConnectionError:
                    f.connectionError()

                el.innerHTML = "Yes"
                return None

            try:
                if not mainValue is None:
                    ws.send(f'{glb.svcoms["main"]} {glb.svcoms["rmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {el.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} False')
                else:
                    ws.send(f'{glb.svcoms["main"]} {glb.svcoms["kmodify"]} /{glb.currentSub.replace(" ", "%20")}.json {value.replace(" ", "%20")} False')
            except ConnectionError:
                f.connectionError()

            el.innerHTML = "No"
            return None

        elif knownValues[value] is list:
            if glb.optionsList == []:
                try:
                    data = ws.msgDict()[glb.svcoms["main"]][f'/{el.id.split("_")[1]}.json']
                except ConnectionError:
                    f.connectionError()
                    return None
            else:
                data = glb.optionsList

            optionsHtml = f''

            for option in data:
                optionsHtml += HTML.add(f'option', _nest=f'{option}', _custom=f'value="{option}"')

            html = HTML.add(f'select', _nest=f'{optionsHtml}', _id=f'{el.id}', _class=f'{el.className}', _style=f'selectSmall %% {styleSlc}', _custom=f'name="{value}_{len(data)}" size="1" multiple')

    el.outerHTML = html

    el = HTML.get(f'{el.id}')
    el.style.width = width

    if el.localName == "select":
        el.style.width = f'{float(width.replace("%", "")) + 0.5}%'

        CSS.onHover(el.id, f'selectHover %% margin-bottom: { - 105 + parantHeight}px;')
        CSS.onFocus(el.id, f'selectFocus %% margin-bottom: { - 105 + parantHeight}px;')

    else:
        CSS.onHover(el.id, f'inputHover')
        CSS.onFocus(el.id, f'inputFocus')

    f.addEvent(el.id, submit, "keyup")


def delRecord(args):
    if not f.popup(f'confirm', f'Are you sure you want to delete "{args.target.id.split("_")[-1]}"?\nThis can not be reverted!'):
        return None

    try:
        ws.send(f'{glb.svcoms["main"]} {glb.svcoms["delete"]} /{glb.currentSub.replace(" ", "%20")}.json {args.target.id.split("_")[-1].replace(" ", "%20")}')
    except ConnectionError:
        f.connectionError()

    HTML.get(HTML.get(f'{args.target.id}').parentNode.id).remove()


def bulkAdd(args):
    if glb.currentSub == "":
        return None

    prefix = f.popup(f'prompt', "Prefix")
    amount = f.popup(f'prompt', "Amount")

    if prefix is None or amount is None:
        return None

    try:
        amount = int(amount)
    except ValueError:
        f.popup(f'alert', "Please enter a rounded number!")
        return None

    if f.popup(f'confirm', f'Records with token "{prefix}{"0" * 2}" to "{prefix}{"0" * (2 - len(str(amount - 1)))}{amount - 1}" will be created!\nDo you want to continue?'):
        for i in range(0, amount):
            try:
                if glb.svcoms["add"] == "uadd":
                    ws.send(f'{glb.svcoms["main"]} {glb.svcoms["add"]} {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')
                    continue

                ws.send(f'{glb.svcoms["main"]} {glb.svcoms["add"]} /{glb.currentSub.replace(" ", "%20")}.json {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')
            except ConnectionError:
                f.connectionError()


def pageSub(args, extraData: dict = {}):
    def setup(args, extraData={}):
        try:
            data = ws.msgDict()[glb.svcoms["main"]]
        except ConnectionError:
            f.connectionError()
            return None

        file = f'/{glb.currentSub}.json'

        if extraData != {}:
            for dic in extraData:
                data[dic] = {**extraData[dic], **data[dic]}

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

        elif f'/{args.target.id.split("_")[-1]}.json' in glb.knownFiles:
            file = f'/{args.target.id.split("_")[-1]}.json'
            glb.currentSub = args.target.id.split("_")[-1]

        elif f'/{args.target.id.split("_")[-1]}' in glb.knownFiles:
            file = f'/{args.target.id.split("_")[-1]}'
            glb.currentSub = args.target.id.split("_")[-1]

        if not file in data:
            return None

        data = data[file]

        if data == {}:
            data[" "] = {}
            mainValue = list(glb.knownFiles[file])[-1]
            data[" "] = {}

            for value in glb.knownFiles[file][mainValue]:
                data[" "][value] = glb.knownFiles[file][mainValue][value]()

        HTML.enable(f'SubPage_nav_options_bulkadd', False)
        HTML.enable(f'SubPage_nav_options_active', False)
        HTML.enable(f'SubPage_nav_options_compact', False)

        if glb.knownFiles[file] is str:
            return data

        if type(glb.knownFiles[file][list(glb.knownFiles[file])[-1]]) is dict:
            HTML.enable(f'SubPage_nav_options_bulkadd', True)
            HTML.enable(f'SubPage_nav_options_active', True)
            HTML.enable(f'SubPage_nav_options_compact', True)

        return data

    def addFull(data):
        def addHeader(data):
            mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
            styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; background: #1F1F1F;'

            rowC = -1
            colC = 0

            HTMLrows = f''
            for record in data:
                rowC += 1
                colC += 0.5

                HTMLcols = HTML.add(f'h1', _nest=f'{mainValue}', _id=f'header_{mainValue}', _class=f'SubPage_page_header', _style=f'headerSmall %% {styleP}')

                if mainValue in glb.halfView:
                    colC += 0.5
                else:
                    colC += 1

                for value in data[record]:
                    if (glb.compactView and value in glb.excludeView) or (glb.hideInactive and value == "Active"):
                        continue

                    HTMLcols += HTML.add(f'h1', _nest=f'{value}', _id=f'header_{value}', _class=f'SubPage_page_header', _style=f'headerSmall %% {styleP}')

                    if value in glb.halfView:
                        colC += 0.5
                        continue
                    colC += 1

                HTMLcols += HTML.add(f'h1', _nest=f'Action', _id=f'header_Action', _class=f'SubPage_page_header', _style=f'headerSmall %% {styleP}')
                colC += 0.5

                HTMLrows += HTML.add(f'div', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                break

            HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

            for item in HTML.get(f'SubPage_page_header', isClass=True):
                if item.id.split("_")[1] in glb.halfView:
                    item.style.width = f'{110 / (colC * 2)}%'
                    continue

                item.style.width = f'{110 / colC}%'

            return rowC, colC

        def addInputRow(data, rowC, colC):
            mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
            knownValues = glb.knownFiles[f'/{glb.currentSub}.json'][mainValue]

            styleInp = f'padding: 0px 1px 3px 1px; margin: 1px -1px; border: 2px solid #55F; border-radius: 0px;'
            styleSlc = f'margin: 1px -1px; height: 28px; border: 2px solid #55F; border-radius: 0px;'
            styleCbx = f'margin: 5px 2px; padding: 0px 0px;'

            HTMLrows = f''
            for record in data:
                rowC += 1
                HTMLcols = HTML.add(f'input', _id=f'SubPage_page_new_input_{mainValue}', _class=f'SubPage_page_new', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{mainValue}"')

                for value in data[record]:
                    if (glb.compactView and value in glb.excludeView) or (glb.hideInactive and value == "Active"):
                        continue

                    elif value in knownValues:
                        if knownValues[value] is int:
                            if value in glb.dates:
                                HTMLcols += HTML.add(f'input', _id=f'SubPage_page_new_input_{value}', _class=f'SubPage_page_new', _type=f'date', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}"')
                            else:
                                HTMLcols += HTML.add(f'input', _id=f'SubPage_page_new_input_{value}', _class=f'SubPage_page_new', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}"')

                        elif knownValues[value] is bool:
                            HTMLcols += HTML.add(f'input', _id=f'SubPage_page_new_checkbox_{value}', _class=f'SubPage_page_new', _type=f'checkbox', _style=f'inputMedium %% {styleCbx}', _custom=f'name="{value}" checked')

                        elif knownValues[value] is list:
                            if glb.optionsList == []:
                                try:
                                    allData = ws.msgDict()[glb.svcoms["main"]][f'/{value}.json']
                                except ConnectionError:
                                    f.connectionError()
                                    return None

                            else:
                                allData = glb.optionsList

                            optionsHtml = f''

                            for option in allData:
                                optionsHtml += HTML.add(f'option', _nest=f'{option}', _custom=f'value="{option}"')
                            name = f'{value}_{len(allData)}'
                            HTMLcols += HTML.add(f'select', _nest=f'{optionsHtml}', _id=f'SubPage_page_new_select_{name}', _class=f'SubPage_page_new', _style=f'selectSmall %% {styleSlc}', _custom=f'name="{name}" size="1" multiple')

                        else:
                            HTMLcols += HTML.add(f'input', _id=f'SubPage_page_new_input_{value}', _class=f'SubPage_page_new', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}"')
                            continue

                    else:
                        HTMLcols += HTML.add(f'input', _id=f'SubPage_page_new_input_{value}', _class=f'SubPage_page_new', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}"')

                HTMLcols += HTML.add(f'button', _nest=f'Add', _id=f'SubPage_page_add', _type=f'submit', _style=f'buttonSmall %% color: #BFF; width: {110 / (colC * 2)}%;')
                HTMLrows += HTML.add(f'form', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;', _custom=f'onsubmit="return false"')

                break

            HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

            for item in HTML.get(f'SubPage_page_new', isClass=True):
                name = item.name.split("_")[0]

                if item.localName == "select" and name in glb.halfView:
                    item.style.width = f'{(110 / (colC * 2)) + 0.5}%'
                    continue

                elif item.localName == "select":
                    item.style.width = f'{(110 / colC) + 0.5}%'
                    continue

                if name in glb.halfView:
                    item.style.width = f'{110 / (colC * 2)}%'
                    continue

                item.style.width = f'{110 / colC}%'

            return rowC

        def addRows(data, rowC, colC):
            mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]
            knownValues = glb.knownFiles[f'/{glb.currentSub}.json'][mainValue]
            buttons = []
            styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

            HTMLrows = f''
            for record in data:
                if glb.hideInactive and not data[record]["Active"]:
                    continue

                rowC += 1
                HTMLcols = HTML.add(f'p', _nest=f'{record}', _id=f'{record}_{mainValue}', _class=f'SubPage_page_records', _style=f'{styleP}')

                for value in data[record]:
                    if (glb.compactView and value in glb.excludeView) or (glb.hideInactive and value == "Active"):
                        continue

                    elif value in knownValues:
                        if knownValues[value] is int:
                            if value in glb.dates:
                                HTMLcols += HTML.add(f'p', _nest=f'{datetime.fromtimestamp(data[record][value]).strftime("%d %b %y")}', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')

                            else:
                                HTMLcols += HTML.add(f'p', _nest=f'{data[record][value]}', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')

                        elif knownValues[value] is bool:
                            if data[record][value]:
                                HTMLcols += HTML.add(f'p', _nest=f'Yes', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')
                            else:
                                HTMLcols += HTML.add(f'p', _nest=f'No', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')

                        elif knownValues[value] is list:
                            HTMLcols += HTML.add(f'p', _nest=f'{", ".join(data[record][value])}', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')

                        else:
                            HTMLcols += HTML.add(f'p', _nest=f'{data[record][value]}', _id=f'{record}_{value}', _class=f'SubPage_page_records', _style=f'{styleP}')

                HTMLcols += HTML.add(f'button', _nest=f'Del', _id=f'SubPage_page_del_{record}', _type=f'button', _style=f'buttonSmall %% padding: 1px 3px;')
                buttons.append(f'SubPage_page_del_{record}')

                HTMLrows += HTML.add(f'div', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

            HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

            for item in HTML.get(f'SubPage_page_records', isClass=True):
                if item.id.split("_")[1] in glb.halfView:
                    item.style.width = f'{110 / (colC * 2)}%'
                    continue

                item.style.width = f'{110 / colC}%'

            return rowC, buttons

        rowC, colC = addHeader(data)
        rowC = addInputRow(data, rowC, colC)
        rowC, buttons = addRows(data, rowC, colC)

        for item in HTML.get(f'SubPage_page_new', isClass=True):
            if not item.localName in ["input", "select"]:
                continue

            elif item.type == "text":
                CSS.onHover(item.id, f'inputHover')
                CSS.onFocus(item.id, f'inputFocus')

            elif item.type == "select-multiple":
                CSS.onHover(item.id, f'selectHover')
                CSS.onFocus(item.id, f'selectFocus')

            if item.name.split("_")[0] in glb.disabledInputs:
                HTML.enable(item.id, False)

        f.addEvent(f'SubPage_page_add', addRecord)
        CSS.onHover(f'SubPage_page_add', f'buttonHover')
        CSS.onClick(f'SubPage_page_add', f'buttonClick')

        for button in buttons:
            CSS.setStyle(f'{button}', f'width', f'{110 / (colC * 2)}%')

            f.addEvent(button, delRecord)
            CSS.onHover(button, f'buttonHover')
            CSS.onClick(button, f'buttonClick')

        mainValue = list(glb.knownFiles[f'/{glb.currentSub}.json'])[-1]

        for item in HTML.get(f'SubPage_page_records', isClass=True):
            if not item.id.split("_")[1] == mainValue:
                f.addEvent(item, editRecord, "dblclick", isClass=True)

    def addMinimal(data):
        def addHeader():
            rowC = 0
            HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

            styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

            for header in ["Key", "Value"]:
                HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{header}', _class=f'SubPage_page_keys', _style=f'{styleP}')

            return rowC

        def addRows(data, rowC):
            knownValues = glb.knownFiles[f'/{glb.currentSub}.json']
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
                f.addEvent(item, editRecord, "dblclick", isClass=True)

    def addLogs(data):
        def loadLogs(args=None):
            rowC = glb.logsLoaded
            styleP = f'margin: -1px ; padding: 3px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

            cutInt = None
            if rowC > 0:
                cutInt = -rowC

            HTMLrows = f''
            for line in reversed(data.split("\n")[:cutInt]):
                if line == "":
                    continue

                rowC += 1
                HTMLcols = f''
                for i, item in enumerate(line.split("%S%")):
                    HTMLcols += HTML.add(f'p', _nest=f'{item}', _id=f'SubPage_page_row{rowC}_col{i}', _class=f'SubPage_page_lines', _style=f'{styleP};')
                    pass

                HTMLrows += HTML.add(f'div', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

            HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

            glb.logsLoaded = rowC

            for item in HTML.get(f'SubPage_page_lines', isClass=True):
                item.classList.remove(f'SubPage_page_lines')
                item.style.width = sizeDict[item.id.split("_")[-1]]

                if item.id.split("_")[-1] == "col2":
                    if item.id == "SubPage_page_row0_col2":
                        continue

                    item.style.textAlign = "left"

            if not HTML.get(f'SubPage_page_buttons') is None:
                HTML.remove(f'SubPage_page_buttons')

            btn = HTML.add(f'button', _nest=f'Load More', _id=f'SubPage_page_buttons_loadMoreLogs', _type=f'button', _style=f'buttonMedium %% width: 75%; height: 40px;')
            HTML.add(f'div', f'SubPage_page', _nest=f'{btn}', _id=f'SubPage_page_buttons', _align=f'center', _style=f'padding-top: 15px; display: flex; justify-content: center;')

            f.addEvent(f'SubPage_page_buttons_loadMoreLogs', loadLogs)
            CSS.onHover(f'SubPage_page_buttons_loadMoreLogs', f'buttonHover')
            CSS.onClick(f'SubPage_page_buttons_loadMoreLogs', f'buttonClick')

        rowC = 0
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

        sizeDict = {"col0": "10%", "col1": "12.5%", "col2": "70%", "col3": "7.5%"}
        styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

        for i, header in enumerate(["Date/ Time", "IP/ Port", "Command", "Status"]):
            HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{header}', _id=f'SubPage_page_row{rowC}_col{i}', _class=f'SubPage_page_lines', _style=f'{styleP}')

        loadLogs()

    HTML.clear(f'SubPage_page')

    data = setup(args, extraData)

    if data is None:
        return None

    elif type(data) is str:
        glb.logsLoaded = 0
        addLogs(data)
        return None

    elif type(data[list(data)[-1]]) is not dict:
        addMinimal(data)
        return None

    else:
        addFull(data)


def main(args=None, sub=None):
    HTML.set(f'div', f'SubPage', _id=f'SubPage_nav', _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.add(f'div', f'SubPage', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')

    HTML.set(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'left', _style=f'width: 60%;"')
    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_options', _align=f'right', _style=f'width: 40%;')

    try:
        data = ws.msgDict()[glb.svcoms["main"]]
    except ConnectionError:
        f.connectionError()
        return None

    foundFile = False

    for file in data:
        if file in glb.knownFiles:
            fileName = f'{file.replace("/", "").replace(".json", "")}'
            HTML.add(f'button', f'SubPage_nav_main', _nest=f'{fileName.replace(".dmp", "")}', _id=f'SubPage_nav_main_{fileName}', _type=f'button', _style=f'buttonSmall')

            foundFile = True

    if not foundFile:
        HTML.set(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'center', _style=f'width: 100%;')
        HTML.add(f'h2', f'SubPage_nav_main', _nest=f'Unauthorized!', _style=f'margin: 10px auto; text-align: center;')
        HTML.enable(f'page_portal_{glb.mainPage}', False)

        return None

    glb.hideInactive = True
    glb.compactView = True

    HTML.add(f'button', f'SubPage_nav_options', _nest=f'Bulk Add', _id=f'SubPage_nav_options_bulkadd', _type=f'button', _align=f'right', _style=f'buttonSmall')
    HTML.add(f'button', f'SubPage_nav_options', _nest=f'Inactive', _id=f'SubPage_nav_options_active', _type=f'button', _align=f'right', _style=f'buttonSmall')
    HTML.add(f'button', f'SubPage_nav_options', _nest=f'Expand', _id=f'SubPage_nav_options_compact', _type=f'button', _align=f'right', _style=f'buttonSmall')

    for file in data:
        if file in glb.knownFiles:
            fileName = f'{file.replace("/", "").replace(".json", "")}'
            f.addEvent(f'SubPage_nav_main_{fileName}', pageSub)
            f.addEvent(f'SubPage_nav_main_{fileName}', getData, f'mousedown')

            CSS.onHover(f'SubPage_nav_main_{fileName}', f'buttonHover')
            CSS.onClick(f'SubPage_nav_main_{fileName}', f'buttonClick')

    f.addEvent(f'SubPage_nav_options_bulkadd', bulkAdd)
    f.addEvent(f'SubPage_nav_options_active', pageSub)
    f.addEvent(f'SubPage_nav_options_compact', pageSub)

    CSS.onHover(f'SubPage_nav_options_bulkadd', f'buttonHover')
    CSS.onHover(f'SubPage_nav_options_active', f'buttonHover')
    CSS.onHover(f'SubPage_nav_options_compact', f'buttonHover')

    CSS.onClick(f'SubPage_nav_options_bulkadd', f'buttonClick')
    CSS.onClick(f'SubPage_nav_options_active', f'buttonClick')
    CSS.onClick(f'SubPage_nav_options_compact', f'buttonClick')

    HTML.enable(f'SubPage_nav_options_bulkadd', False)
    HTML.enable(f'SubPage_nav_options_active', False)
    HTML.enable(f'SubPage_nav_options_compact', False)

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

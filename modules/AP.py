from WS import ws
from datetime import datetime, timedelta
from js import document, window, console
from pyodide.ffi import create_proxy


class func:
    def addEvent(id: str, func, action="click", isClass=False):
        proxy = create_proxy(func)

        if isClass:
            id.addEventListener(action, proxy)
            return None

        document.getElementById(id).addEventListener(action, proxy)

    def connectionError():
        element = document.getElementById(f'page_scripts_body')
        element.innerHTML = f'<div id="page_scripts_body_error" align="center"></div>'

        element = document.getElementById(f'page_scripts_body_error')
        element.innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! The server is probably not running!<br>Please refresh the page to try again.</p><br>'


class AP:
    currentPage = "Admin"
    currentSub = ""

    lastUpdate = 0
    knownFiles = {
        "/Config.json": {
            "IP": str,
            "PORT": int,
            "Debug": bool,
            "Modified": int
        },
        "/Tokens.json": {
            "Token": {
                "Username": str,
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

    dates = ["Modified", "Expires"]

    halfView = ["User", "Auth", "Expires", "Modified", "Active", "Action"]
    compactView = False

    excludeView = ["Expires", "Modified"]
    hideInactive = False

    optionsList = ["Admin", "Asset Manager"]
    fetshOptions = False

    svcoms = {"main": "admin", "read": "read", "add": "add", "modify": "modify", "rmodify": "tkmodify", "kmodify": "kmodify", "delete": "delete"}

    def getData(args=None):
        if (datetime.now() - timedelta(seconds=5)).timestamp() > AP.lastUpdate:
            try:
                for file in AP.knownFiles:
                    ws.send(f'{AP.svcoms["main"]} {AP.svcoms["read"]} {file}')
            except ConnectionError:
                func.connectionError()

            AP.lastUpdate = datetime.now().timestamp()

    def addRecord(args):
        element = document.getElementsByClassName(f'{AP.currentPage}_page_new')

        token = ""
        data = {}

        mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
        knownValues = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]

        for i in range(0, element.length):
            name = str(element.item(i).name.split("_")[0])
            value = str(element.item(i).value)

            if name == mainValue and ("_" in value):
                window.alert(f'Invalid format for "{name}"!\n"{name}" may not include underscores ("_").')
                return None

            if name in knownValues:
                if knownValues[name] is bool:
                    value = bool(element.item(i).checked)

                elif knownValues[name] is int:
                    value = int(value)

                    if name in AP.dates:
                        value = int(datetime.now().timestamp())

                        if element.item(i).value != "":
                            value = int(datetime.strptime(element.item(i).value, "%Y-%m-%d").timestamp())

                elif knownValues[name] is list:

                    value = []

                    for i1 in range(0, int(element.item(i).name.split("_")[1])):
                        if element.item(i).item(i1).selected is True:
                            value.append(element.item(i).item(i1).value)

                elif element.item(i).value == "":
                    value = knownValues[name]()

                else:
                    value = knownValues[name](element.item(i).value)

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

        ws.send(f'{AP.svcoms["main"]} {AP.svcoms["add"]} /{AP.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")}')
        ws.send(f'{AP.svcoms["main"]} {AP.svcoms["modify"]} /{AP.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")} {str(data).replace(" ", "%20").replace("False", "false").replace("True", "true")}')

        AP.pageSub(args, {f'/{AP.currentSub}.json': data})

    def editRecord(args):
        def submit(args):
            if not args.key in ["Enter", "Escape"]:
                return None

            mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
            knownValues = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]

            element = document.getElementById(args.target.id)
            value = element.id.split("_")[1]

            if args.key == "s" and value.replace(" ", "%20") in knownValues:
                if not knownValues[value.replace(" ", "%20")] is list:
                    return None

            data = element.value.replace(" ", "%20")
            width = element.style.width

            if element.localName == "select":
                width = f'{float(width.replace("%", "")) - 0.645}%'

            if data == "":
                data = "%20"

            html = f'<p class="{element.className}" id="{element.id}">{data.replace("%20", " ")}</p>'

            if value in knownValues:
                if knownValues[value] is int:
                    data = int(data)

                    if value in AP.dates:
                        data = int(datetime.strptime(data, "%Y-%m-%d").timestamp())
                        html = f'<p class="{element.className}" id="{element.id}">{datetime.fromtimestamp(data).strftime("%d %b %y")}</p>'

                elif knownValues[value] is list:
                    data = []

                    for i in range(0, int(args.target.name.split("_")[1])):
                        if args.target.item(i).selected is True:
                            data.append(args.target.item(i).value)

                    data = ", ".join(data).replace(" ", "%20")

                    html = f'<p class="{element.className}" id="{element.id}">{data.replace("%20", " ")}</p>'

            ws.send(f'{AP.svcoms["main"]} {AP.svcoms["rmodify"]} /{AP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} {data}')

            element.outerHTML = html

            element = document.getElementById(element.id)
            element.style.width = width

            func.addEvent(element.id, AP.editRecord, "dblclick")

        element = document.getElementById(args.target.id)
        width = element.style.width
        value = element.id.split("_")[1]

        mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
        knownValues = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]

        if element.innerHTML == " ":
            element.innerHTML = ""

        html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="text" value="{element.innerHTML}">'

        if value in knownValues:
            if knownValues[value] is bool:
                if element.innerHTML == "No":
                    ws.send(f'{AP.svcoms["main"]} {AP.svcoms["rmodify"]} /{AP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} True')
                    element.innerHTML = "Yes"
                    return None

                ws.send(f'{AP.svcoms["main"]} {AP.svcoms["rmodify"]} /{AP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} False')
                element.innerHTML = "No"
                return None

            elif knownValues[value] is list:
                if AP.fetshOptions:
                    try:
                        data = ws.msgDict()[f'/{element.id.split("_")[1]}.json']
                    except ConnectionError:
                        func.connectionError()
                        return None
                else:
                    data = AP.optionsList

                optionsHtml = f''

                for option in data:
                    optionsHtml += f'<option value="{option}">{option}</option>'

                html = f'<select class="{element.className}" id="{element.id}" name="{value}_{len(data)}" size="1" multiple>{optionsHtml}</select>'

            elif knownValues[value] is int:
                if value in AP.dates:
                    html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="date" value="{datetime.strptime(element.innerHTML, "%d %b %y").strftime("%Y-%m-%d")}">'
                else:
                    html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="date" value="{element.innerHTML}">'

        element.outerHTML = html

        element = document.getElementById(element.id)
        element.style.width = width

        if element.localName == "select":
            element.style.width = f'{float(width.replace("%", "")) + 0.645}%'

        func.addEvent(element.id, submit, "keyup")

    def delRecord(args):
        if not window.confirm(f'Are you sure you want to delete "{args.target.id.split("_")[-1]}"?\nThis can not be reverted!'):
            return None

        ws.send(f'{AP.svcoms["main"]} {AP.svcoms["delete"]} /{AP.currentSub.replace(" ", "%20")}.json {args.target.id.split("_")[-1].replace(" ", "%20")}')

        element = document.getElementById(args.target.id)
        element = document.getElementById(element.parentNode.id)
        element.remove()

    def bulkAdd(args):
        if AP.currentSub == "":
            return None

        prefix = window.prompt("Prefix")
        amount = window.prompt("Amount")

        if prefix is None or amount is None:
            return None

        try:
            amount = int(amount)
        except ValueError:
            window.alert("Please enter a rounded number!")
            return None

        if window.confirm(f'Records with token "{prefix}{"0" * 2}" to "{prefix}{"0" * (2 - len(str(amount - 1)))}{amount - 1}" will be created!\nDo you want to continue?'):
            for i in range(0, amount):
                ws.send(f'{AP.svcoms["main"]} {AP.svcoms["add"]} /{AP.currentSub.replace(" ", "%20")}.json {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')

    def pageSub(args, extraData: dict = {}):
        def setup(args, extraData={}):
            try:
                data = ws.msgDict()
            except ConnectionError:
                func.connectionError()
                return None

            file = f'/{AP.currentSub}.json'

            if extraData != {}:
                for dic in extraData:
                    data[dic] = {**extraData[dic], **data[dic]}

            if args.target.id.split("_")[-1] == "compact":
                AP.compactView = not AP.compactView

                element = document.getElementById(args.target.id)

                if AP.compactView:
                    element.innerHTML = "Expand"
                else:
                    element.innerHTML = "Compact"

            if args.target.id.split("_")[-1] == "active":
                AP.hideInactive = not AP.hideInactive

                element = document.getElementById(args.target.id)

                if AP.hideInactive:
                    element.innerHTML = "Inactive"
                else:
                    element.innerHTML = "Active"

            elif f'/{args.target.id.split("_")[-1]}.json' in AP.knownFiles:
                file = f'/{args.target.id.split("_")[-1]}.json'
                AP.currentSub = args.target.id.split("_")[-1]

            if not file in data:
                return None

            data = data[file]

            if data == {}:
                data[" "] = {}
                mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
                data[" "] = {}

                for value in AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]:
                    data[" "][value] = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue][value]()

            element = document.getElementById(f'{AP.currentPage}_nav_options_bulkadd')
            element.disabled = True
            element = document.getElementById(f'{AP.currentPage}_nav_options_active')
            element.disabled = True
            element = document.getElementById(f'{AP.currentPage}_nav_options_compact')
            element.disabled = True

            if type(AP.knownFiles[f'/{AP.currentSub}.json'][list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]]) is dict:
                element = document.getElementById(f'{AP.currentPage}_nav_options_bulkadd')
                element.disabled = False
                element = document.getElementById(f'{AP.currentPage}_nav_options_active')
                element.disabled = False
                element = document.getElementById(f'{AP.currentPage}_nav_options_compact')
                element.disabled = False

            return data

        def newRow(rowC, form: bool = False):
            element = document.getElementById(f'{AP.currentPage}_page')

            if form:
                element.innerHTML += f'<form id="{AP.currentPage}_page_row{rowC}" align="left" onsubmit="return false"></form>'

            else:
                element.innerHTML += f'<div id="{AP.currentPage}_page_row{rowC}" align="left"></div>'

            element = document.getElementById(f'{AP.currentPage}_page_row{rowC}')
            element.style.display = "flex"

            return element, rowC + 1

        def addHeader(data, rowC, colC):
            mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]

            for record in data:
                element, rowC = newRow(rowC)
                colC += 0.5

                element.innerHTML += f'<p class="{AP.currentPage}_page_header" id="header_{mainValue}"><b>{mainValue}</b></p>'

                if mainValue in AP.halfView:
                    colC += 0.5
                else:
                    colC += 1

                for value in data[record]:
                    if (AP.compactView and value in AP.excludeView) or (AP.hideInactive and value == "Active"):
                        continue

                    element.innerHTML += f'<p class="{AP.currentPage}_page_header" id="header_{value}"><b>{value}</b></p>'

                    if value in AP.halfView:
                        colC += 0.5
                        continue

                    colC += 1

                element.innerHTML += f'<p class="{AP.currentPage}_page_header" id="header_Action"><b>Action</b></p>'
                colC += 0.5

                element = document.getElementsByClassName(f'{AP.currentPage}_page_header')

                for i in range(0, element.length):
                    if element.item(i).id.split("_")[1] in AP.halfView:
                        element.item(i).style.width = f'{110 / (colC * 2)}%'
                        continue

                    element.item(i).style.width = f'{110 / colC}%'

                return rowC, colC

        def addInputRow(data, rowC, colC):
            mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
            knownValues = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]

            for record in data:
                element, rowC = newRow(rowC, form=True)
                element.innerHTML += f'<input class="{AP.currentPage}_page_new" name={mainValue} type="text" disabled>'

                for value in data[record]:
                    if (AP.compactView and value in AP.excludeView) or (AP.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is int:
                            if value in AP.dates:
                                element.innerHTML += f'<input class="{AP.currentPage}_page_new" name="{value}" type="date">'
                                continue

                        elif knownValues[value] is bool:
                            element.innerHTML += f'<input class="{AP.currentPage}_page_new" name="{value}" type="checkbox" checked>'
                            continue

                        elif knownValues[value] is list:
                            if AP.fetshOptions:
                                try:
                                    allData = ws.msgDict()
                                except ConnectionError:
                                    func.connectionError()
                                    return None

                                if f'/{value}.json' in allData:
                                    allDataValue = list(allData[f'/{value}.json'])[-1]
                                    allData = allData[f'/{value}.json'][allDataValue]
                                else:
                                    allData == {}

                                if allData == {}:
                                    allData[" "] = {}

                                    for value1 in AP.knownFiles[f'/{AP.currentSub}.json']:
                                        if not value1 == mainValue:
                                            allData[" "][value1] = AP.knownFiles[f'/{AP.currentSub}.json'][value1]()
                            else:
                                allData = AP.optionsList

                            optionsHtml = f''

                            for option in allData:
                                optionsHtml += f'<option value="{option}">{option}</option>'

                            element.innerHTML += f'<select class="{AP.currentPage}_page_new" name="{value}_{len(allData)}" size="1" multiple>{optionsHtml}</select>'
                            continue

                    element.innerHTML += f'<input class="{AP.currentPage}_page_new" name="{value}" type="text">'

                element.innerHTML += f'<button id="{AP.currentPage}_page_add" type="submit">Add</button>'

                element = document.getElementById(f'{AP.currentPage}_page_add')
                element.style.width = f'{110 / (colC * 2)}%'

                break

            element = document.getElementsByClassName(f'{AP.currentPage}_page_new')

            for i in range(0, element.length):

                if element.item(i).localName == "select" and element.item(i).name in AP.halfView:
                    element.item(i).style.width = f'{(110 / (colC * 2)) + 0.645}%'
                    continue

                elif element.item(i).localName == "select":
                    element.item(i).style.width = f'{(110 / colC) + 0.645}%'
                    continue

                elif element.item(i).name in AP.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC

        def addRows(data, rowC, colC):
            mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
            knownValues = AP.knownFiles[f'/{AP.currentSub}.json'][mainValue]
            buttons = []

            for record in data:
                if AP.hideInactive and not data[record]["Active"]:
                    continue

                element, rowC = newRow(rowC)
                element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{mainValue}">{record}</p>'

                for value in data[record]:
                    if (AP.compactView and value in AP.excludeView) or (AP.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is int:
                            if value in AP.dates:
                                element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">{datetime.fromtimestamp(data[record][value]).strftime("%d %b %y")}</p>'
                                continue

                            element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">{data[record][value]}</p>'
                            continue

                        if knownValues[value] is bool:
                            if data[record][value]:
                                element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">Yes</p>'
                                continue

                            element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">No</p>'
                            continue

                        if knownValues[value] is list:
                            element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">{", ".join(data[record][value])}</p>'
                            continue

                    element.innerHTML += f'<p class="{AP.currentPage}_page_records" id="{record}_{value}">{data[record][value]}</p>'

                element.innerHTML += f'<button id="{AP.currentPage}_page_del_{record}" type="button">Del</button>'
                buttons.append(f'{AP.currentPage}_page_del_{record}')

            element = document.getElementsByClassName(f'{AP.currentPage}_page_records')

            for i in range(0, element.length):
                if element.item(i).id.split("_")[1] in AP.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC, buttons

        def addEvents(buttons, colC):
            func.addEvent(f'{AP.currentPage}_page_add', AP.addRecord)

            for button in buttons:
                element = document.getElementById(button)
                element.style.width = f'{110 / (colC * 2)}%'

                func.addEvent(button, AP.delRecord)

            mainValue = list(AP.knownFiles[f'/{AP.currentSub}.json'])[-1]
            element = document.getElementsByClassName(f'{AP.currentPage}_page_records')

            for i in range(0, element.length):
                if not element.item(i).id.split("_")[1] == mainValue:
                    func.addEvent(element.item(i), AP.editRecord, "dblclick", True)

        element = document.getElementById(f'{AP.currentPage}_page')
        element.innerHTML = f''

        data = setup(args, extraData)

        if data is None:
            return None

        rowC = 0
        colC = 0

        rowC, colC = addHeader(data, rowC, colC)
        rowC = addInputRow(data, rowC, colC)
        rowC, buttons = addRows(data, rowC, colC)

        addEvents(buttons, colC)

    def page(args=None, sub=None):
        element = document.getElementById(f'{AP.currentPage}')
        element.innerHTML = f'<div id="{AP.currentPage}_nav" align="center"></div>'
        element.innerHTML += f'<div id="{AP.currentPage}_page" align="center"></div>'

        element = document.getElementById(f'{AP.currentPage}_nav')
        element.innerHTML += f'<div id="{AP.currentPage}_nav_main" align="left"></div>'
        element.innerHTML += f'<div id="{AP.currentPage}_nav_options" align="right"></div>'

        element = document.getElementById(f'{AP.currentPage}_nav_main')

        try:
            data = ws.msgDict()
        except ConnectionError:
            func.connectionError()
            return None

        if data == {}:
            element.innerHTML += f'<h2>Unauthorized!</h2>'

        for file in data:
            if file in AP.knownFiles:
                element.innerHTML += f'<button id="{AP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}" type="button">{file.replace("/", "").replace(".json", "").replace(".dmp", "")}</button>'

        AP.hideInactive = True
        AP.compactView = True

        element = document.getElementById(f'{AP.currentPage}_nav_options')
        element.innerHTML += f'<button id="{AP.currentPage}_nav_options_bulkadd" type="button" align=right disabled>Bulk Add</button>'
        element.innerHTML += f'<button id="{AP.currentPage}_nav_options_active" type="button" align=right disabled>Inactive</button>'
        element.innerHTML += f'<button id="{AP.currentPage}_nav_options_compact" type="button" align=right disabled>Expand</button>'

        for file in data:
            if file in AP.knownFiles:
                func.addEvent(f'{AP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', AP.pageSub)
                func.addEvent(f'{AP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', AP.getData, f'mousedown')

        func.addEvent(f'{AP.currentPage}_nav_options_bulkadd', AP.bulkAdd)
        func.addEvent(f'{AP.currentPage}_nav_options_active', AP.pageSub)
        func.addEvent(f'{AP.currentPage}_nav_options_compact', AP.pageSub)

        if sub is not None:
            AP.currentSub = sub
            AP.pageSub(args)
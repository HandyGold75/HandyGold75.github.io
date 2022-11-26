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


class AM:
    currentPage = "Asset Manager"
    currentSub = ""

    lastUpdate = 0
    knownValues = {
        "Assignments": {
            "Devices": list,
            "Assets": list,
            "Servers": list,
            "Modified": int,
            "Active": bool,
            "Notes": str
        },
        "Devices": {
            "Tag": str,
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
        },
        "Assets": {
            "Tag": str,
            "Brand": str,
            "Asset": str,
            "Series": str,
            "S/N": str,
            "DOP": int,
            "EOL": int,
            "Modified": int,
            "Active": bool,
            "Notes": str
        },
        "Servers": {
            "Tag": str,
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
    knownFiles = []

    halfView = ["Tag", "Brand", "Series", "Active", "Action", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified"]
    compactView = False
    excludeView = ["S/N", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified"]
    hideInactive = False

    def getData(args=None):
        if (datetime.now() - timedelta(seconds=5)).timestamp() > AM.lastUpdate:
            try:
                ws.send(f'am read /Assignments.json')
                ws.send(f'am read /Devices.json')
                ws.send(f'am read /Assets.json')
                ws.send(f'am read /Servers.json')
            except ConnectionError:
                func.connectionError()

            AM.lastUpdate = datetime.now().timestamp()

    def addRecord(args):
        element = document.getElementsByClassName(f'{AM.currentPage}_page_new')

        tag = ""
        data = {}

        knownValues = AM.knownValues[AM.currentSub]

        for i in range(0, element.length):
            name = str(element.item(i).name.split("_")[0])
            value = str(element.item(i).value)

            if name == "Tag" and ("_" in value):
                window.alert(f'Invalid format for "{name}"!\n"{name}" may not include underscores ("_").')
                return None

            if name in knownValues:
                if knownValues[name.split("_")[0]] is bool:
                    value = bool(element.item(i).checked)

                elif knownValues[name] is int:
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

            if name == "Tag":
                tag = value
                data[tag] = {}

                for knownValue in knownValues:
                    if knownValue != "Tag":
                        if knownValues[knownValue] is bool:
                            data[tag][knownValue] = not knownValues[knownValue]()
                            continue

                        data[tag][knownValue] = knownValues[knownValue]()

                continue

            data[tag][name] = value

        ws.send(f'am add /{AM.currentSub.replace(" ", "%20")}.json {tag.replace(" ", "%20")}')
        ws.send(f'am modify /{AM.currentSub.replace(" ", "%20")}.json {tag.replace(" ", "%20")} {str(data).replace(" ", "%20").replace("False", "false").replace("True", "true")}')

        AM.pageSub(args, {f'/{AM.currentSub}.json': data})

    def editRecord(args):
        def submit(args):
            if not args.key in ["Enter", "Escape"]:
                return None

            knownValues = AM.knownValues[AM.currentSub]
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

            if value.replace(" ", "%20") in knownValues:
                if knownValues[value.replace(" ", "%20")] is int:
                    data = int(datetime.strptime(data, "%Y-%m-%d").timestamp())
                    html = f'<p class="{element.className}" id="{element.id}">{datetime.fromtimestamp(data).strftime("%d %b %y")}</p>'

                elif knownValues[value.replace(" ", "%20")] is list:
                    data = []

                    for i in range(0, int(args.target.name.split("_")[1])):
                        if args.target.item(i).selected is True:
                            data.append(args.target.item(i).value)

                    data = ", ".join(data).replace(" ", "%20")

                    html = f'<p class="{element.className}" id="{element.id}">{data.replace("%20", " ")}</p>'

            ws.send(f'am rmodify /{AM.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} {data}')

            element.outerHTML = html

            element = document.getElementById(element.id)
            element.style.width = width

            func.addEvent(element.id, AM.editRecord, "dblclick")

        element = document.getElementById(args.target.id)
        width = element.style.width
        value = element.id.split("_")[1]

        knownValues = AM.knownValues[AM.currentSub]

        if element.innerHTML == " ":
            element.innerHTML = ""

        html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="text" value="{element.innerHTML}">'

        if value in knownValues:
            if knownValues[value] is bool:
                if element.innerHTML == "No":
                    ws.send(f'am rmodify /{AM.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} True')
                    element.innerHTML = "Yes"
                    return None

                ws.send(f'am rmodify /{AM.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} False')
                element.innerHTML = "No"
                return None

            elif knownValues[value] is list:
                try:
                    data = ws.msgDict()[f'/{element.id.split("_")[1]}.json']
                except ConnectionError:
                    func.connectionError()
                    return None

                optionsHtml = f''

                for option in data:
                    optionsHtml += f'<option value="{option}">{option}</option>'

                html = f'<select class="{element.className}" id="{element.id}" name="{value}_{len(data)}" size="1" multiple>{optionsHtml}</select>'

            elif knownValues[value] is int:
                html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="date" value="{datetime.strptime(element.innerHTML, "%d %b %y").strftime("%Y-%m-%d")}">'

        element.outerHTML = html

        element = document.getElementById(element.id)
        element.style.width = width

        if element.localName == "select":
            element.style.width = f'{float(width.replace("%", "")) + 0.645}%'

        func.addEvent(element.id, submit, "keyup")

    def delRecord(args):
        if not window.confirm(f'Are you sure you want to delete "{args.target.id.split("_")[-1]}"?\nThis can not be reverted!'):
            return None

        ws.send(f'am delete /{AM.currentSub.replace(" ", "%20")}.json {args.target.id.split("_")[-1].replace(" ", "%20")}')

        element = document.getElementById(args.target.id)
        element = document.getElementById(element.parentNode.id)
        element.remove()

    def bulkAdd(args):
        if AM.currentSub == "":
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

        if window.confirm(f'Records with tag "{prefix}{"0" * 2}" to "{prefix}{"0" * (2 - len(str(amount - 1)))}{amount - 1}" will be created!\nDo you want to continue?'):
            for i in range(0, amount):
                ws.send(f'am add /{AM.currentSub.replace(" ", "%20")}.json {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')

    def pageSub(args, extraData: dict = {}):
        def setup(args, data={}):
            try:
                data = ws.msgDict()
            except ConnectionError:
                func.connectionError()
                return None

            file = f'/{AM.currentSub}.json'

            if extraData != {}:
                for dic in extraData:
                    data[dic] = {**extraData[dic], **data[dic]}

            if args.target.id.split("_")[-1] == "compact":
                AM.compactView = not AM.compactView

                element = document.getElementById(args.target.id)

                if AM.compactView:
                    element.innerHTML = "Expand"
                else:
                    element.innerHTML = "Compact"

            if args.target.id.split("_")[-1] == "active":
                AM.hideInactive = not AM.hideInactive

                element = document.getElementById(args.target.id)

                if AM.hideInactive:
                    element.innerHTML = "Inactive"
                else:
                    element.innerHTML = "Active"

            elif args.target.id.split("_")[-1] in AM.knownValues:
                file = f'/{args.target.id.split("_")[-1]}.json'
                AM.currentSub = args.target.id.split("_")[-1]

            if not file in data:
                return None

            data = data[file]

            if data == {}:
                data[" "] = {}

                for value in AM.knownValues[AM.currentSub]:
                    if not value == "Tag":
                        data[" "][value] = AM.knownValues[AM.currentSub][value]()

            return data

        def newRow(rowC, form: bool = False):
            element = document.getElementById(f'{AM.currentPage}_page')

            if form:
                element.innerHTML += f'<form id="{AM.currentPage}_page_row{rowC}" align="left" onsubmit="return false"></form>'

            else:
                element.innerHTML += f'<div id="{AM.currentPage}_page_row{rowC}" align="left"></div>'

            element = document.getElementById(f'{AM.currentPage}_page_row{rowC}')
            element.style.display = "flex"

            return element, rowC + 1

        def addHeader(data, rowC, colC):
            for record in data:
                element, rowC = newRow(rowC)
                element.innerHTML += f'<p class="{AM.currentPage}_page_header" id="header_Tag"><b>Tag</b></p>'
                colC += 1

                for value in data[record]:
                    if (AM.compactView and value in AM.excludeView) or (AM.hideInactive and value == "Active"):
                        continue

                    element.innerHTML += f'<p class="{AM.currentPage}_page_header" id="header_{value}"><b>{value}</b></p>'

                    if value in AM.halfView:
                        colC += 0.5
                        continue

                    colC += 1

                element.innerHTML += f'<p class="{AM.currentPage}_page_header" id="header_Action"><b>Action</b></p>'
                colC += 0.5

                element = document.getElementsByClassName(f'{AM.currentPage}_page_header')

                for i in range(0, element.length):
                    if element.item(i).id.split("_")[1] in AM.halfView:
                        element.item(i).style.width = f'{110 / (colC * 2)}%'
                        continue

                    element.item(i).style.width = f'{110 / colC}%'

                return rowC, colC

        def addInputRow(data, rowC, colC):
            knownValues = AM.knownValues[AM.currentSub]

            for record in data:
                element, rowC = newRow(rowC, form=True)
                element.innerHTML += f'<input class="{AM.currentPage}_page_new" name="Tag" type="text">'

                for value in data[record]:
                    if (AM.compactView and value in AM.excludeView) or (AM.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is bool:
                            element.innerHTML += f'<input class="{AM.currentPage}_page_new" name="{value}" type="checkbox" checked>'
                            continue

                        elif knownValues[value] is list:
                            try:
                                data = ws.msgDict()
                            except ConnectionError:
                                func.connectionError()
                                return None

                            if not f'/{value}.json' in data:
                                return None

                            data = data[f'/{value}.json']

                            if data == {}:
                                data[" "] = {}

                                for value in AM.knownValues[AM.currentSub]:
                                    if not value == "Tag":
                                        data[" "][value] = AM.knownValues[AM.currentSub][value]()

                            optionsHtml = f''

                            for option in data:
                                optionsHtml += f'<option value="{option}">{option}</option>'

                            element.innerHTML += f'<select class="{AM.currentPage}_page_new" name="{value}_{len(data)}" size="1" multiple>{optionsHtml}</select>'
                            continue

                        elif knownValues[value] is int:
                            element.innerHTML += f'<input class="{AM.currentPage}_page_new" name="{value}" type="date">'
                            continue

                    element.innerHTML += f'<input class="{AM.currentPage}_page_new" name="{value}" type="text">'

                element.innerHTML += f'<button id="{AM.currentPage}_page_add" type="submit">Add</button>'

                element = document.getElementById(f'{AM.currentPage}_page_add')
                element.style.width = f'{110 / (colC * 2)}%'

                break

            element = document.getElementsByClassName(f'{AM.currentPage}_page_new')

            for i in range(0, element.length):

                if element.item(i).localName == "select" and element.item(i).name in AM.halfView:
                    element.item(i).style.width = f'{(110 / (colC * 2)) + 0.645}%'
                    continue

                elif element.item(i).localName == "select":
                    element.item(i).style.width = f'{(110 / colC) + 0.645}%'
                    continue

                elif element.item(i).name in AM.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC, colC

        def addRows(data, rowC, colC):
            knownValues = AM.knownValues[AM.currentSub]
            buttons = []

            for record in data:
                if AM.hideInactive and not data[record]["Active"]:
                    continue

                element, rowC = newRow(rowC)
                element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_Tag">{record}</p>'

                for value in data[record]:
                    if (AM.compactView and value in AM.excludeView) or (AM.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is int:
                            element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_{value}">{datetime.fromtimestamp(data[record][value]).strftime("%d %b %y")}</p>'
                            continue

                        if knownValues[value] is bool:
                            if data[record][value]:
                                element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_{value}">Yes</p>'
                                continue

                            element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_{value}">No</p>'
                            continue

                        if knownValues[value] is list:
                            element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_{value}">{", ".join(data[record][value])}</p>'
                            continue

                    element.innerHTML += f'<p class="{AM.currentPage}_page_records" id="{record}_{value}">{data[record][value]}</p>'

                element.innerHTML += f'<button id="{AM.currentPage}_page_del_{record}" type="button">Del</button>'
                buttons.append(f'{AM.currentPage}_page_del_{record}')

            element = document.getElementsByClassName(f'{AM.currentPage}_page_records')

            for i in range(0, element.length):
                if element.item(i).id.split("_")[1] in AM.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC, colC, buttons

        def addEvents(buttons, colC):
            func.addEvent(f'{AM.currentPage}_page_add', AM.addRecord)

            for button in buttons:
                element = document.getElementById(button)
                element.style.width = f'{110 / (colC * 2)}%'

                func.addEvent(button, AM.delRecord)

            element = document.getElementsByClassName(f'{AM.currentPage}_page_records')

            for i in range(0, element.length):
                if not element.item(i).id.split("_")[1] == "Tag":
                    func.addEvent(element.item(i), AM.editRecord, "dblclick", True)

        element = document.getElementById(f'{AM.currentPage}_page')
        element.innerHTML = f''

        data = setup(args, extraData)

        if data is None:
            return None

        rowC = 0
        colC = 0

        rowC, colC = addHeader(data, rowC, colC)
        rowC, colC = addInputRow(data, rowC, colC)
        rowC, colC, buttons = addRows(data, rowC, colC)

        addEvents(buttons, colC)

    def page(args=None, sub=None):
        element = document.getElementById(f'{AM.currentPage}')
        element.innerHTML = f'<div id="{AM.currentPage}_nav" align="center"></div>'
        element.innerHTML += f'<div id="{AM.currentPage}_page" align="center"></div>'

        element = document.getElementById(f'{AM.currentPage}_nav')
        element.innerHTML += f'<div id="{AM.currentPage}_nav_main" align="left"></div>'
        element.innerHTML += f'<div id="{AM.currentPage}_nav_options" align="right"></div>'

        element = document.getElementById(f'{AM.currentPage}_nav_main')

        try:
            data = ws.msgDict()
        except ConnectionError:
            func.connectionError()
            return None

        if data == {}:
            element.innerHTML += f'<h2>Unauthorized!</h2>'

        for file in data:
            AM.knownFiles.append(file)
            element.innerHTML += f'<button id="{AM.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}" type="button">{file.replace("/", "").replace(".json", "")}</button>'

        AM.hideInactive = True
        AM.compactView = True

        element = document.getElementById(f'{AM.currentPage}_nav_options')
        element.innerHTML += f'<button id="{AM.currentPage}_nav_options_bulkadd" type="button" align=right>Bulk Add</button>'
        element.innerHTML += f'<button id="{AM.currentPage}_nav_options_active" type="button" align=right>Inactive</button>'
        element.innerHTML += f'<button id="{AM.currentPage}_nav_options_compact" type="button" align=right>Expand</button>'

        for file in data:
            func.addEvent(f'{AM.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', AM.pageSub)
            func.addEvent(f'{AM.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', AM.getData, f'mousedown')

        func.addEvent(f'{AM.currentPage}_nav_options_bulkadd', AM.bulkAdd)
        func.addEvent(f'{AM.currentPage}_nav_options_active', AM.pageSub)
        func.addEvent(f'{AM.currentPage}_nav_options_compact', AM.pageSub)

        if sub is not None:
            AM.currentSub = sub
            AM.pageSub(args)

from WS import ws
from rsa import encrypt, PublicKey
from datetime import datetime, timedelta
from js import document, window, console
from pyodide.ffi import create_proxy


class func:
    pk = PublicKey(
        17975725580318426255082147295765624015303015361719602497231012933790462235693879580362187130307063578819348335338567705110647296830122706922462277858985753916807418663775359155059872610188320580932610131649669750813854841233828756158531041784174256821099975573954534872920341091204735563674609735155365230886328225569764099100220190749309854601263231477479542538657656228075477248164911150242612255058022595583271630531937574957740889057640197605063861387428744601476627747146952083278992989884033643188605058493867723623443206205193049387986735721023723231370158070058492831123317729469188277654546977114897225138444403440484404763488252900359062156606277556273881462454700682132900566293665122593793415917496306396245694769766289157377434428292617546842809345418069309429637482719212135032501150835116958632132203299437985348946833084644910715245987521602696627857328192665936755312620767597809000086619959376727150300660078176663731141210223403780234209251726760747452546317356315404004871864255840070441131656153163327938733747321658554956837916867148392977768261809450501332458691119391299657873525192653810706009363153494395380856616333139608534198022835408820709017274233496194895658713718965362482943679407034749283305672669328250828229765188719765598395616090554409644372199205005788822144569725849378518257318799359385281740742304089043012203207090757315833795382410385714872414605971371066034681422629572254445672849310499485979905134814561918728629098272915355126315453439738702075534702666290929177330864697626107597200532737216328442694999218938113176867865482874172297137142445161550097040446308420534920219666339316839673749833944188357418385020268794629695550903965269473702504547059078067498031149096658925058636652798068077433395661533192684961900825996213912591011509835703499018540858216533684827588691036564984023994359992388733781114505117772831573454751130891256075050103442171938154332660431264950585164243096093925476801938794141572630854512014984334825819438750599965004024341493159922341794445006274654995566118300460214077412075511161181698540977050816711684965694813515198715185678618288095811937806305637976252287014606730927818130439428520119356203573068177397436647258848659927556173455871707333064805630504242580519613705444817600006146353152014424758858473533029673605478152571643653561181152156398594145488582743474039155367716449975165309811984584398398690891924952884510454449930797215394455097922506895883409901302916494995512076986478728196359060058428252757519467838794722732611686045347810271767912080044182207678353913483129629823113438113820791587878184283905176268454906351041779158933382590216398059177568853055270942077059156649685981827207451739862232562515028977633596944364071556509266121310722218226028783650241233584332498505271414144626505460338325024130616840681895382408708213628489128094251273023012874086250181912500877109239104433256351412004835767020264459805538504082187665406998198032223427723556839093765764713436949937704964091432419465151166261180178053480295497695748125437451332250448661556736139515685003382928341989,
        65537)

    def addEvent(id: str, func, action="click", isClass=False):
        proxy = create_proxy(func)

        if isClass:
            id.addEventListener(action, proxy)
            return None

        document.getElementById(id).addEventListener(action, proxy)

    def connectionError():
        element = document.getElementById(f'page_portal_body')
        element.innerHTML = f'<div id="page_portal_body_error" align="center"></div>'

        element = document.getElementById(f'page_portal_body_error')
        element.innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! The server is probably not running!<br>Please refresh the page to try again.</p><br>'

    def invoke_AP(args=None):
        SP.currentPage = "Admin"
        SP.currentSub = ""

        SP.knownFiles = {
            "/Config.json": {
                "IP": str,
                "PORT": int,
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

        SP.dates = ["Modified", "Expires"]

        SP.halfView = ["User", "Auth", "Expires", "Modified", "Active", "Action"]
        SP.compactView = False

        SP.excludeView = ["Expires", "Modified"]
        SP.hideInactive = False

        SP.disabledInputs = ["Token", "User", "Auth", "Roles", "Expires", "Modified", "Active", "Notes"]
        SP.invokePasswordOnChange = ["User"]

        SP.optionsList = ["Admin", "Asset Manager", "License Manager"]

        SP.svcoms = {"main": "admin", "read": "read", "add": "uadd", "modify": "modify", "rmodify": "tkmodify", "kmodify": "kmodify", "delete": "delete"}

        SP.getData()

    def invoke_AM(args=None):
        SP.currentPage = "Asset Manager"
        SP.currentSub = ""

        SP.knownFiles = {
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

        SP.dates = ["DOP", "EOL", "Modified"]

        SP.halfView = ["User", "Tag", "Brand", "Series", "Active", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified", "Action"]
        SP.compactView = False

        SP.excludeView = ["S/N", "MAC", "MAC-WiFi", "MAC-Eth", "DOP", "EOL", "Modified"]
        SP.hideInactive = False

        SP.disabledInputs = ["Modified"]
        SP.invokePasswordOnChange = []

        SP.optionsList = []

        SP.svcoms = {"main": "am", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "kmodify": "kmodify", "delete": "delete"}

        SP.getData()

    def invoke_LM(args=None):
        SP.currentPage = "License Manager"
        SP.currentSub = ""

        SP.knownFiles = {
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

        SP.dates = ["DOP", "EOL", "Modified"]

        SP.halfView = ["Tag", "DOP", "EOL", "Cost", "Auto Renew", "Modified", "Active", "Action"]
        SP.compactView = False

        SP.excludeView = ["DOP", "EOL", "Cost", "Auto Renew", "Modified"]
        SP.hideInactive = False

        SP.disabledInputs = ["Modified"]
        SP.invokePasswordOnChange = []

        SP.optionsList = []

        SP.svcoms = {"main": "lm", "read": "read", "add": "add", "modify": "modify", "rmodify": "rmodify", "kmodify": "kmodify", "delete": "delete"}

        SP.getData()


class SP:
    currentPage = ""
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

    def getData(args=None):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > SP.lastUpdate:
            try:
                for file in SP.knownFiles:
                    ws.send(f'{SP.svcoms["main"]} {SP.svcoms["read"]} {file}')
            except ConnectionError:
                func.connectionError()

            SP.lastUpdate = datetime.now().timestamp()

    def addRecord(args):
        if SP.svcoms["add"] == "uadd":
            try:
                ws.send(f'{SP.svcoms["main"]} {SP.svcoms["add"]} /{SP.currentSub.replace(" ", "%20")}.json')
            except ConnectionError:
                func.connectionError()

            window.alert(f'New user created.\nReload the subpage for changes to appear.')

            return None

        element = document.getElementsByClassName(f'{SP.currentPage}_page_new')

        token = ""
        data = {}

        mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
        knownValues = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]

        for i in range(0, element.length):
            name = str(element.item(i).name.split("_")[0])
            value = str(element.item(i).value)

            if name == mainValue and ("_" in value):
                window.alert(f'Invalid format for "{name}"!\n"{name}" may not include underscores ("_").')
                return None

            if name in knownValues:
                if knownValues[name] is int:
                    if value == "":
                        value = 0

                    value = int(value)

                    if name in SP.dates:
                        value = int(datetime.now().timestamp())

                        if element.item(i).value != "":
                            value = int(datetime.strptime(element.item(i).value, "%Y-%m-%d").timestamp())

                elif knownValues[name] is bool:
                    value = bool(element.item(i).checked)

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

        try:
            ws.send(f'{SP.svcoms["main"]} {SP.svcoms["add"]} /{SP.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")}')
            ws.send(f'{SP.svcoms["main"]} {SP.svcoms["modify"]} /{SP.currentSub.replace(" ", "%20")}.json {token.replace(" ", "%20")} {str(data).replace(" ", "%20").replace("False", "false").replace("True", "true")}')
        except ConnectionError:
            func.connectionError()

        SP.pageSub(args, {f'/{SP.currentSub}.json': data})

    def editRecord(args):
        def submit(args):
            if not args.key in ["Enter", "Escape"]:
                return None

            mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
            knownValues = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]

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

                    if value in SP.dates:
                        data = int(datetime.strptime(data, "%Y-%m-%d").timestamp())
                        html = f'<p class="{element.className}" id="{element.id}">{datetime.fromtimestamp(data).strftime("%d %b %y")}</p>'

                elif knownValues[value] is list:
                    data = []

                    for i in range(0, int(args.target.name.split("_")[1])):
                        if args.target.item(i).selected is True:
                            data.append(args.target.item(i).value)

                    data = ", ".join(data).replace(" ", "%20")
                    html = f'<p class="{element.className}" id="{element.id}">{data.replace("%20", " ")}</p>'

            if value in SP.invokePasswordOnChange:
                password = window.prompt("Please enter the new password for the user.")

                if password is None:
                    return None

                password = str(encrypt(data.encode() + password.encode(), func.pk)).replace(" ", "%20")
                try:
                    ws.send(f'{SP.svcoms["main"]} {SP.svcoms["rmodify"]} /{SP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} Password {password}')
                except ConnectionError:
                    func.connectionError()

            try:
                ws.send(f'{SP.svcoms["main"]} {SP.svcoms["rmodify"]} /{SP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} {data}')
            except ConnectionError:
                func.connectionError()

            element.outerHTML = html

            element = document.getElementById(element.id)
            element.style.width = width

            func.addEvent(element.id, SP.editRecord, "dblclick")

        element = document.getElementById(args.target.id)
        width = element.style.width
        value = element.id.split("_")[1]

        mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
        knownValues = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]

        if element.innerHTML == " ":
            element.innerHTML = ""

        html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="text" value="{element.innerHTML}">'

        if value in knownValues:
            if knownValues[value] is int:
                if value in SP.dates:
                    html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="date" value="{datetime.strptime(element.innerHTML, "%d %b %y").strftime("%Y-%m-%d")}">'
                else:
                    html = f'<input class="{element.className}" id="{element.id}" name="{value}" type="text" value="{element.innerHTML}">'

            elif knownValues[value] is bool:
                if element.innerHTML == "No":
                    try:
                        ws.send(f'{SP.svcoms["main"]} {SP.svcoms["rmodify"]} /{SP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} True')
                    except ConnectionError:
                        func.connectionError()

                    element.innerHTML = "Yes"
                    return None

                try:
                    ws.send(f'{SP.svcoms["main"]} {SP.svcoms["rmodify"]} /{SP.currentSub.replace(" ", "%20")}.json {element.id.split("_")[0].replace(" ", "%20")} {value.replace(" ", "%20")} False')
                except ConnectionError:
                    func.connectionError()

                element.innerHTML = "No"
                return None

            elif knownValues[value] is list:
                if SP.optionsList == []:
                    try:
                        data = ws.msgDict()[f'/{element.id.split("_")[1]}.json']
                    except ConnectionError:
                        func.connectionError()
                        return None
                else:
                    data = SP.optionsList

                optionsHtml = f''

                for option in data:
                    optionsHtml += f'<option value="{option}">{option}</option>'

                html = f'<select class="{element.className}" id="{element.id}" name="{value}_{len(data)}" size="1" multiple>{optionsHtml}</select>'

        element.outerHTML = html

        element = document.getElementById(element.id)
        element.style.width = width

        if element.localName == "select":
            element.style.width = f'{float(width.replace("%", "")) + 0.645}%'

        func.addEvent(element.id, submit, "keyup")

    def delRecord(args):
        if not window.confirm(f'Are you sure you want to delete "{args.target.id.split("_")[-1]}"?\nThis can not be reverted!'):
            return None

        try:
            ws.send(f'{SP.svcoms["main"]} {SP.svcoms["delete"]} /{SP.currentSub.replace(" ", "%20")}.json {args.target.id.split("_")[-1].replace(" ", "%20")}')
        except ConnectionError:
            func.connectionError()

        element = document.getElementById(args.target.id)
        element = document.getElementById(element.parentNode.id)
        element.remove()

    def bulkAdd(args):
        if SP.currentSub == "":
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
                try:
                    ws.send(f'{SP.svcoms["main"]} {SP.svcoms["add"]} /{SP.currentSub.replace(" ", "%20")}.json {prefix.replace(" ", "%20")}{"0" * (2 - len(str(i)))}{i}')
                except ConnectionError:
                    func.connectionError()

    def pageSub(args, extraData: dict = {}):
        def setup(args, extraData={}):
            try:
                data = ws.msgDict()
            except ConnectionError:
                func.connectionError()
                return None

            file = f'/{SP.currentSub}.json'

            if extraData != {}:
                for dic in extraData:
                    data[dic] = {**extraData[dic], **data[dic]}

            if args.target.id.split("_")[-1] == "compact":
                SP.compactView = not SP.compactView

                element = document.getElementById(args.target.id)

                if SP.compactView:
                    element.innerHTML = "Expand"
                else:
                    element.innerHTML = "Compact"

            if args.target.id.split("_")[-1] == "active":
                SP.hideInactive = not SP.hideInactive

                element = document.getElementById(args.target.id)

                if SP.hideInactive:
                    element.innerHTML = "Inactive"
                else:
                    element.innerHTML = "Active"

            elif f'/{args.target.id.split("_")[-1]}.json' in SP.knownFiles:
                file = f'/{args.target.id.split("_")[-1]}.json'
                SP.currentSub = args.target.id.split("_")[-1]

            if not file in data:
                return None

            data = data[file]

            if data == {}:
                data[" "] = {}
                mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
                data[" "] = {}

                for value in SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]:
                    data[" "][value] = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue][value]()

            element = document.getElementById(f'{SP.currentPage}_nav_options_bulkadd')
            element.disabled = True
            element = document.getElementById(f'{SP.currentPage}_nav_options_active')
            element.disabled = True
            element = document.getElementById(f'{SP.currentPage}_nav_options_compact')
            element.disabled = True

            if type(SP.knownFiles[f'/{SP.currentSub}.json'][list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]]) is dict:
                element = document.getElementById(f'{SP.currentPage}_nav_options_bulkadd')
                element.disabled = False
                element = document.getElementById(f'{SP.currentPage}_nav_options_active')
                element.disabled = False
                element = document.getElementById(f'{SP.currentPage}_nav_options_compact')
                element.disabled = False

            return data

        def newRow(rowC, form: bool = False):
            element = document.getElementById(f'{SP.currentPage}_page')

            if form:
                element.innerHTML += f'<form id="{SP.currentPage}_page_row{rowC}" align="left" onsubmit="return false"></form>'

            else:
                element.innerHTML += f'<div id="{SP.currentPage}_page_row{rowC}" align="left"></div>'

            element = document.getElementById(f'{SP.currentPage}_page_row{rowC}')
            element.style.display = "flex"

            return element, rowC + 1

        def addHeader(data, rowC, colC):
            mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]

            for record in data:
                element, rowC = newRow(rowC)
                colC += 0.5

                element.innerHTML += f'<p class="{SP.currentPage}_page_header" id="header_{mainValue}"><b>{mainValue}</b></p>'

                if mainValue in SP.halfView:
                    colC += 0.5
                else:
                    colC += 1

                for value in data[record]:
                    if (SP.compactView and value in SP.excludeView) or (SP.hideInactive and value == "Active"):
                        continue

                    element.innerHTML += f'<p class="{SP.currentPage}_page_header" id="header_{value}"><b>{value}</b></p>'

                    if value in SP.halfView:
                        colC += 0.5
                        continue

                    colC += 1

                element.innerHTML += f'<p class="{SP.currentPage}_page_header" id="header_Action"><b>Action</b></p>'
                colC += 0.5

                element = document.getElementsByClassName(f'{SP.currentPage}_page_header')

                for i in range(0, element.length):
                    if element.item(i).id.split("_")[1] in SP.halfView:
                        element.item(i).style.width = f'{110 / (colC * 2)}%'
                        continue

                    element.item(i).style.width = f'{110 / colC}%'

                return rowC, colC

        def addInputRow(data, rowC, colC):
            mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
            knownValues = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]

            for record in data:
                element, rowC = newRow(rowC, form=True)
                element.innerHTML += f'<input class="{SP.currentPage}_page_new" name={mainValue} type="text">'

                for value in data[record]:
                    if (SP.compactView and value in SP.excludeView) or (SP.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is int:
                            if value in SP.dates:
                                element.innerHTML += f'<input class="{SP.currentPage}_page_new" name="{value}" type="date">'
                                continue

                        elif knownValues[value] is bool:
                            element.innerHTML += f'<input class="{SP.currentPage}_page_new" name="{value}" type="checkbox" checked>'
                            continue

                        elif knownValues[value] is list:
                            if SP.optionsList == []:
                                try:
                                    allData = ws.msgDict()[f'/{value}.json']
                                except ConnectionError:
                                    func.connectionError()
                                    return None
                            else:
                                allData = SP.optionsList

                            optionsHtml = f''

                            for option in allData:
                                optionsHtml += f'<option value="{option}">{option}</option>'

                            element.innerHTML += f'<select class="{SP.currentPage}_page_new" name="{value}_{len(allData)}" size="1" multiple>{optionsHtml}</select>'
                            continue

                    element.innerHTML += f'<input class="{SP.currentPage}_page_new" name="{value}" type="text">'

                element.innerHTML += f'<button id="{SP.currentPage}_page_add" type="submit">Add</button>'

                element = document.getElementById(f'{SP.currentPage}_page_add')
                element.style.width = f'{110 / (colC * 2)}%'

                break

            element = document.getElementsByClassName(f'{SP.currentPage}_page_new')

            for i in range(0, element.length):
                name = element.item(i).name.split("_")[0]
                localName = element.item(i).localName

                if name in SP.disabledInputs:
                    element.item(i).disabled = True

                if localName == "select" and name in SP.halfView:
                    element.item(i).style.width = f'{(110 / (colC * 2)) + 0.645}%'
                    continue

                elif localName == "select":
                    element.item(i).style.width = f'{(110 / colC) + 0.645}%'
                    continue

                elif name in SP.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC

        def addRows(data, rowC, colC):
            mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
            knownValues = SP.knownFiles[f'/{SP.currentSub}.json'][mainValue]
            buttons = []

            for record in data:
                if SP.hideInactive and not data[record]["Active"]:
                    continue

                element, rowC = newRow(rowC)
                element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{mainValue}">{record}</p>'

                for value in data[record]:
                    if (SP.compactView and value in SP.excludeView) or (SP.hideInactive and value == "Active"):
                        continue

                    if value in knownValues:
                        if knownValues[value] is int:
                            if value in SP.dates:
                                element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">{datetime.fromtimestamp(data[record][value]).strftime("%d %b %y")}</p>'
                                continue

                            element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">{data[record][value]}</p>'
                            continue

                        if knownValues[value] is bool:
                            if data[record][value]:
                                element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">Yes</p>'
                                continue

                            element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">No</p>'
                            continue

                        if knownValues[value] is list:
                            element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">{", ".join(data[record][value])}</p>'
                            continue

                    element.innerHTML += f'<p class="{SP.currentPage}_page_records" id="{record}_{value}">{data[record][value]}</p>'

                element.innerHTML += f'<button id="{SP.currentPage}_page_del_{record}" type="button">Del</button>'
                buttons.append(f'{SP.currentPage}_page_del_{record}')

            element = document.getElementsByClassName(f'{SP.currentPage}_page_records')

            for i in range(0, element.length):
                if element.item(i).id.split("_")[1] in SP.halfView:
                    element.item(i).style.width = f'{110 / (colC * 2)}%'
                    continue

                element.item(i).style.width = f'{110 / colC}%'

            return rowC, buttons

        def addEvents(buttons, colC):
            func.addEvent(f'{SP.currentPage}_page_add', SP.addRecord)

            for button in buttons:
                element = document.getElementById(button)
                element.style.width = f'{110 / (colC * 2)}%'

                func.addEvent(button, SP.delRecord)

            mainValue = list(SP.knownFiles[f'/{SP.currentSub}.json'])[-1]
            element = document.getElementsByClassName(f'{SP.currentPage}_page_records')

            for i in range(0, element.length):
                if not element.item(i).id.split("_")[1] == mainValue:
                    func.addEvent(element.item(i), SP.editRecord, "dblclick", True)

        element = document.getElementById(f'{SP.currentPage}_page')
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
        element = document.getElementById(f'{SP.currentPage}')
        element.innerHTML = f'<div id="{SP.currentPage}_nav" align="center"></div>'
        element.innerHTML += f'<div id="{SP.currentPage}_page" align="center"></div>'

        element = document.getElementById(f'{SP.currentPage}_nav')
        element.innerHTML += f'<div id="{SP.currentPage}_nav_main" align="left"></div>'
        element.innerHTML += f'<div id="{SP.currentPage}_nav_options" align="right"></div>'

        element = document.getElementById(f'{SP.currentPage}_nav_main')

        try:
            data = ws.msgDict()
        except ConnectionError:
            func.connectionError()
            return None

        if data == {}:
            element.innerHTML += f'<h2>Unauthorized!</h2>'

        for file in data:
            if file in SP.knownFiles:
                element.innerHTML += f'<button id="{SP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}" type="button">{file.replace("/", "").replace(".json", "").replace(".dmp", "")}</button>'

        SP.hideInactive = True
        SP.compactView = True

        element = document.getElementById(f'{SP.currentPage}_nav_options')
        element.innerHTML += f'<button id="{SP.currentPage}_nav_options_bulkadd" type="button" align=right disabled>Bulk Add</button>'
        element.innerHTML += f'<button id="{SP.currentPage}_nav_options_active" type="button" align=right disabled>Inactive</button>'
        element.innerHTML += f'<button id="{SP.currentPage}_nav_options_compact" type="button" align=right disabled>Expand</button>'

        for file in data:
            if file in SP.knownFiles:
                func.addEvent(f'{SP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', SP.pageSub)
                func.addEvent(f'{SP.currentPage}_nav_main_{file.replace("/", "").replace(".json", "")}', SP.getData, f'mousedown')

        func.addEvent(f'{SP.currentPage}_nav_options_bulkadd', SP.bulkAdd)
        func.addEvent(f'{SP.currentPage}_nav_options_active', SP.pageSub)
        func.addEvent(f'{SP.currentPage}_nav_options_compact', SP.pageSub)

        if sub is not None:
            SP.currentSub = sub
            SP.pageSub(args)
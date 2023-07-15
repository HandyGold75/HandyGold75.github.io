from WebKit import HTML, CSS, JS, Widget
from WebKit.WebSocket import WS
from rsa import encrypt
from json import dumps, loads
from datetime import datetime, timedelta
import math


class invoke:
    def TP(args=None):
        glb.subPages = ["Plugs", "Config"]

        glb.lastUpdate = 0

        WS.send(f'tapo history')
        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        WS.send(f'tapo state')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    subPages = []

    lastUpdate = 0

    config = {}
    knownConfig = {"costPerKw": float, "costFormat": str, "lineResolution": int, "useMonthly": bool, ":D": bool}
    optionsList = []


def pageSub(args=None):
    def setup(args):
        if JS.cache("page_portal_tapo") is None or JS.cache("page_portal_tapo") == "":
            JS.cache("page_portal_tapo", dumps({"costPerKw": 0.00, "costFormat": "$", "lineResolution": 25, "useMonthly": False, ":D": False}))

        glb.config = loads(JS.cache("page_portal_tapo"))

        if not args is None and f'{args.target.id.split("_")[-1]}' in glb.subPages:
            JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

    def login():
        usr = JS.popup(f'prompt', f'Tapo Username')
        if usr is None:
            return None

        psw = JS.popup(f'prompt', f'Tapo Password')
        if psw is None:
            return None

        WS.onMsg("{\"tapo\":", pageSub, oneTime=True)
        WS.onMsg("Failed", login, oneTime=True)
        WS.send(f'tapo login {usr.replace(" ", "%20")} {str(encrypt(psw.encode(), WS.PK)).replace(" ", "%20")}')

    def plugs():
        def getDur(dur):
            for applyValue, correctionValue, format, round in [(7884000, 2628000, "M", False), (259200, 86400, "d", False), (10800, 3600, "h", False), (180, 60, "m", True)]:
                if not dur > applyValue:
                    continue

                if round:
                    dur = f'{int(dur / correctionValue)} {format}'
                    break

                dur = f'{(dur / correctionValue):.2f} {format}'
                break

            if type(dur) is int:
                dur = f'{dur} s'

            return dur

        def verySlowUIRefresh():
            def update(data):
                for plug in data:
                    HTML.setElementRaw(f'Details_{plug}_todayCost', f'{((data[plug]["todayPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}')
                    HTML.setElementRaw(f'Details_{plug}_monthlyCost', f'{((data[plug]["monthlyPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}')
                    HTML.setElementRaw(f'Details_{plug}_todayPower', f'{(data[plug]["todayPower"] / 1000):.2f} kW')
                    HTML.setElementRaw(f'Details_{plug}_monthlyPower', f'{(data[plug]["monthlyPower"] / 1000):.2f} kW')
                    HTML.setElementRaw(f'Details_{plug}_todayTime', f'{getDur(data[plug]["todayTime"] * 60)}')
                    HTML.setElementRaw(f'Details_{plug}_monthlyTime', f'{getDur(data[plug]["monthlyTime"] * 60)}')

                    if data[plug]["overheated"]:
                        CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'100%')
                    else:
                        CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'0%')

            if not JS.cache("page_portalSub") == "Plugs":
                return False

            data = WS.dict()["tapo"]["current"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(verySlowUIRefresh, 10000)

        def slowUIRefresh():
            def update(data):
                for plug in data:
                    HTML.setElementRaw(f'Gauge_{plug}_power', f'{(data[plug]["currentPower"] / 1000):.2f}<br>Wh')
                    HTML.setElementRaw(f'Gauge_{plug}_uptime', f'{getDur(data[plug]["duration"])}')

                    if not data[plug]["state"]:
                        for i in range(0, 101):
                            CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'0%')

                        CSS.setStyles(f'Power_{plug}', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                        continue

                    for i in range(0, 101):
                        if data[plug]["currentPower"] > i * 10000:
                            CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'100%')
                            continue

                        CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'0%')

            if not JS.cache("page_portalSub") == "Plugs":
                return False

            data = WS.dict()["tapo"]["current"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(getData, 500)
            JS.afterDelay(slowUIRefresh, 1000)

        def fastUIRefresh():
            def update(data):
                for plug in data:
                    if not data[plug]["state"]:
                        continue

                    CSS.setStyles(f'Power_{plug}', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))

            if not JS.cache("page_portalSub") == "Plugs":
                return False

            data = WS.dict()["tapo"]["current"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(fastUIRefresh, 250)

        def addGraph(plug: str):
            def drawLines():
                def getDur(dur):
                    for applyValue, correctionValue, format, round in [(7884000, 2628000, "M", False), (259200, 86400, "d", False), (10800, 3600, "h", False), (180, 60, "m", True)]:
                        if not dur > applyValue:
                            continue

                        if round:
                            dur = f'{int(dur / correctionValue)} {format}'
                            break

                        dur = f'{(dur / correctionValue):.2f} {format}'
                        break

                    if type(dur) is int:
                        dur = f'{dur} s'

                    return dur

                if glb.config[":D"]:
                    Widget.graphDraw(f'graph_usage_{plug}', ((1, 2, ":D"), (1, 3, ":D"), (2, 4, ":D"), (3, 4, ":D"), (4, 3, ":D"), (4, 2, ":D"), (3, 1, ":D"), (2, 1, ":D"), (1, 2, ":D")), lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_usage_{plug}', ((5, 1, ":D"), (4.5, 2, ":D"), (7.5, 2, ":D"), (7, 1, ":D"), (5, 1, ":D")), lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_usage_{plug}', ((8, 2, ":D"), (8, 3, ":D"), (9, 4, ":D"), (10, 4, ":D"), (11, 3, ":D"), (11, 2, ":D"), (10, 1, ":D"), (9, 1, ":D"), (8, 2, ":D")), lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_cost_{plug}', ((1, 2, ":D"), (1, 3, ":D"), (2, 4, ":D"), (3, 4, ":D"), (4, 3, ":D"), (4, 2, ":D"), (3, 1, ":D"), (2, 1, ":D"), (1, 2, ":D")), lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_cost_{plug}', ((5, 1, ":D"), (4.5, 2, ":D"), (7.5, 2, ":D"), (7, 1, ":D"), (5, 1, ":D")), lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_cost_{plug}', ((8, 2, ":D"), (8, 3, ":D"), (9, 4, ":D"), (10, 4, ":D"), (11, 3, ":D"), (11, 2, ":D"), (10, 1, ":D"), (9, 1, ":D"), (8, 2, ":D")), lineRes=glb.config["lineResolution"])

                    return None

                data = WS.dict()["tapo"]["history"][plug]

                usageDivision, costDivision, rowLimit, colLimit = (50, 10, 6, 13)
                if not glb.config["useMonthly"]:
                    usageDivision, costDivision, rowLimit, colLimit = (5, 1, 4, 4)

                date = datetime.now()
                dates = []
                for i in range(0, colLimit):
                    dates.append(date)
                    date = date - timedelta(days=date.day)

                cordsUsage = []
                cordsCost = []
                for time in data:
                    dataDate = datetime.fromtimestamp(int(time))
                    col = None

                    for i, date in enumerate(reversed(dates)):
                        if dataDate.year != date.year or dataDate.month != date.month:
                            continue

                        col = i + 1 - (31 - dataDate.day) / 31
                        break

                    if col is None:
                        continue
                    elif col >= colLimit:
                        col = colLimit - 0.01
                    elif col < 0.01:
                        col = 0.01

                    txt = f'date: {dataDate.strftime("%d %b %y")}<br>'
                    for key in data[time]:
                        if key == "duration":
                            txt += f'{key}:	{getDur(data[time][key])}<br>'
                            continue
                        if key == "currentPower":
                            txt += f'{key}:	{(data[time][key] / 1000):.2f} W<br>'
                            continue
                        elif "Power" in key:
                            txt += f'{key}:	{(data[time][key] / 1000):.2f} kW<br>'
                            continue
                        elif "Time" in key:
                            txt += f'{key}:	{getDur(data[time][key] * 60)}<br>'
                            continue

                        txt += f'{key}:	{data[time][key]}<br>'

                    txt += f'todayCost: {((data[time]["todayPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}<br>'
                    txt += f'monthlyCost: {((data[time]["monthlyPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}<br>'

                    dataPower = data[time]["monthlyPower"]
                    if not glb.config["useMonthly"]:
                        dataPower = data[time]["todayPower"]

                    row = dataPower / (1000 * usageDivision)
                    if row >= rowLimit:
                        row = rowLimit - 0.01
                    elif row < 0.01:
                        row = 0.01
                    cordsUsage.append((float(col), float(row), txt))

                    row = (dataPower / (1000 * costDivision)) * glb.config["costPerKw"]
                    if row >= rowLimit:
                        row = rowLimit - 0.01
                    elif row < 0.01:
                        row = 0.01
                    cordsCost.append((float(col), float(row), txt))

                Widget.graphDraw(f'graph_usage_{plug}', cordsUsage, lineRes=glb.config["lineResolution"])
                Widget.graphDraw(f'graph_cost_{plug}', cordsCost, lineRes=glb.config["lineResolution"])

            data = WS.dict()["tapo"]["current"]

            if not data[plug]["model"] in ["P115", "P110", "total"]:
                return None

            usageStep, costStep, rowLimit, colLimit = (50, 10, 6, 13)
            if not glb.config["useMonthly"]:
                usageStep, costStep, rowLimit, colLimit = (5, 1, 4, 4)

            date = datetime.now()
            dates = []
            for i in range(0, colLimit):
                dates.append(date.strftime("%b (%y)"))
                date = date - timedelta(days=date.day)

            txt = HTML.genElement("h1", nest=f'Usage - Montly', style=f'headerBig')
            if not glb.config["useMonthly"]:
                txt = HTML.genElement("h1", nest=f'Usage - Daily', style=f'headerBig')

            HTML.setElement(f'div',
                     f'SubPage_page_graph',
                     nest=txt + Widget.graph(f'graph_usage_{plug}', rowHeight=f'75px', rows=rowLimit, rowStep=usageStep, cols=colLimit, origin=("power", "date"), rowAfterfix=" kW", colNames=tuple(reversed(dates)), smallHeaders=True),
                     id=f'SubPage_page_graph_usage',
                     style=f'divNormal')

            txt = HTML.genElement("h1", nest=f'Cost - Montly', style=f'headerBig')
            if not glb.config["useMonthly"]:
                txt = HTML.genElement("h1", nest=f'Cost - Daily', style=f'headerBig')

            HTML.addElement(f'div',
                     f'SubPage_page_graph',
                     nest=txt +
                     Widget.graph(f'graph_cost_{plug}', rowHeight=f'75px', rows=rowLimit, rowStep=costStep, cols=colLimit, origin=("cost", "date"), rowAfterfix=f' {glb.config["costFormat"]}', colNames=tuple(reversed(dates)), smallHeaders=True),
                     id=f'SubPage_page_graph_cost',
                     style=f'divNormal')

            JS.aSync(drawLines)

        def addPlugs():
            def togglePower(args):
                data = WS.dict()["tapo"]["current"]
                plug = args.target.id.split("_")[-1]

                if not plug in data:
                    return None

                if not data[plug]["state"]:
                    WS.send(f'tapo on {plug}')

                elif JS.popup(f'confirm', f'Are you sure you want to turn off this device?\nDevice: {plug}'):
                    WS.send(f'tapo off {plug}')

            def getInfo(args):
                data = WS.dict()["tapo"]["history"]
                plug = args.target.id.split("_")[-1]

                if not plug in data:
                    return None

                addGraph(plug)

            def header(plug):
                img = HTML.genElement(f'img', id=f'Info_img_{plug}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Tapo/Info.png" alt="Info"')
                btn = HTML.genElement(f'button', nest=f'{img}', id=f'Info_{plug}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                info = HTML.genElement(f'div', nest=f'{btn}', align=f'center', style=f'width: 15%; min-width: 30px; margin: auto;')

                txt = HTML.genElement(f'h1', nest=f'{plug}', style=f'headerMedium %% width: 70%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;')

                img = HTML.genElement(f'img', id=f'Power_img_{plug}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Tapo/Power.png" alt="Power"')
                btn = HTML.genElement(f'button', nest=f'{img}', id=f'Power_{plug}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                power = HTML.genElement(f'div', nest=f'{btn}', align=f'center', style=f'width: 15%; min-width: 30px; margin: auto;')

                return HTML.genElement(f'div', nest=f'{info}{txt}{power}', style=f'flex %% padding-bottom: 10px; border-bottom: 4px dotted #111;')

            def body(plug):
                img = HTML.genElement(f'img', style=f'z-index: 1; width: 100%; margin: auto; position: relative; user-select:none;', custom=f'src="docs/assets/Portal/Tapo/Gauge.png" alt="Gauge"')

                svg = ""
                for i in range(0, 101):
                    if i < 50:
                        r, g = (int(255 * (i / 50)), 255)
                    else:
                        r, g = (255, int(255 * ((50 - i % 50) / 50)))

                    svg += HTML.genElement(f'line',
                                    id=f'Gauge_{plug}_{i}',
                                    style=f'z-index: 0; stroke: {"#{:02x}{:02x}{:02x}".format(r, g, 0)}; stroke-width: 5; opacity: 0%; transition: opacity 0.25s;',
                                    custom=f'x1="50%" y1="50%" x2="{i}%" y2="{256.3 * math.sin(math.pi * ((i - 50) / 100)**4)}%"')

                svg = HTML.genElement(f'svg', nest=f'{svg}', style=f'width: 80%; height: 110px; margin: auto auto auto -80%; left: -10%; top: -5px; position: relative; user-select:none;')

                txt = HTML.genElement(f'p', nest=f'0.00<br>Wh', id=f'Gauge_{plug}_power', style=f'z-index: 24; width: 100%; margin: auto auto auto -100%; padding: 0px 0px 5% 0px; line-height: 100%; font-weight: bold; position: relative; user-select:none;')
                txt += HTML.genElement(f'p', nest=f'0.00 s', id=f'Gauge_{plug}_uptime', style=f'z-index: 25; width: 100%; margin: auto auto auto -100%; padding: 50% 0px 0px 0px; font-weight: bold; position: relative; user-select:none;')
                txt += HTML.genElement(f'h1',
                                nest=f'Overheated!',
                                id=f'Gauge_{plug}_overheat',
                                style=f'headerMedium %% z-index: 26; width: 100%; margin: auto auto -20px -100%; color: #F00; position: relative; opacity: 0%; transition: opacity 0.25s; user-select:none;')

                return HTML.genElement(f'div', nest=f'{img}{svg}{txt}', style=f'flex %% padding: 20px 10px; border-bottom: 4px dotted #111;')

            def footer(plug):
                div = ""

                for visKey, key, format in (("Today", "", ""), ("Cost:", "todayCost", f'0 {glb.config["costFormat"]}'), ("Power:", "todayPower", "0 kW"), ("Time:", "todayTime", "0 s"), ("Monthly", "", ""),
                                            ("Cost:", "monthlyCost", f'0 {glb.config["costFormat"]}'), ("Power:", "monthlyPower", "0 kW"), ("Time:", "monthlyTime", "0 s")):

                    txt = HTML.genElement(f'p', nest=f'{visKey}', style=f'width: 45%; margin: auto; font-weight: bold; user-select:none;')

                    if not key == "":
                        txt += HTML.genElement(f'p', nest=f'{format}', id=f'Details_{plug}_{key}', style=f'width: 55%; margin: auto; font-weight: bold;')

                    div += HTML.genElement(f'div', nest=f'{txt}', align=f'center', style=f'flex')

                return HTML.genElement(f'div', nest=f'{div}', style=f'padding-top: 10px;')

            data = WS.dict()["tapo"]["current"]

            for plug in data:
                if not data[plug]["model"] in ["P115", "P110", "total"]:
                    continue

                HTML.addElement(f'div',
                         f'SubPage_page_main',
                         nest=f'{header(plug)}{body(plug)}{footer(plug)}',
                         id=f'SubPage_page_main_{plug}',
                         style=f'divNormal %% min-width: 150px; margin: 15px; padding: 5px 15px 15px 15px; border: 4px solid #55F; border-radius: 4px;')

            for plug in data:
                if not data[plug]["model"] in ["P115", "P110", "total"]:
                    continue

                JS.addEvent(f'Info_{plug}', getInfo)
                CSS.onHoverClick(f'Info_{plug}', f'imgHover', f'imgClick')

                JS.addEvent(f'Power_{plug}', togglePower)
                CSS.onHoverClick(f'Power_{plug}', f'imgHover', f'imgClick')

        HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_main', style=f'divNormal %% flex %% margin: 15px 30px 15px auto; overflow-y: hidden;')
        HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_graph', style=f'divNormal %% margin: 0px; padding 0px;')

        addPlugs()

        JS.afterDelay(fastUIRefresh, 250)
        JS.afterDelay(slowUIRefresh, 500)
        JS.afterDelay(verySlowUIRefresh, 750)

    def config():
        def editRecord(args):
            def submit(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = HTML.getElement(args.target.id)

                if "_" in el.id:
                    mainValue = list(glb.knownConfig)[-1]
                    knownValues = glb.knownConfig[mainValue]
                    value = el.id.split("_")[1]

                else:
                    mainValue = None
                    knownValues = glb.knownConfig
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

                        html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{", ".join(data).replace(" ", "%20")}</p>'

                glb.config[value] = data
                JS.cache("page_portal_tapo", dumps(glb.config))

                el.outerHTML = html

                JS.addEvent(el.id, editRecord, "dblclick")
                CSS.setStyle(f'{el.id}', f'width', f'{width}')

            el = HTML.getElement(args.target.id)
            width = el.style.width
            parantHeight = HTML.getElement(el.parentElement.id).offsetHeight

            if "_" in el.id:
                value = el.id.split("_")[1]
                mainValue = list(glb.knownConfig)[-1]
                knownValues = glb.knownConfig[mainValue]

            else:
                value = el.id
                mainValue = None
                knownValues = glb.knownConfig

            if el.innerHTML == " ":
                el.innerHTML = ""

            styleInp = f'margin: -1px -1px; padding: 1px 1px 4px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
            styleSlc = f'height: {parantHeight + 4}px; margin: -1px -1px; padding: 1px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
            html = HTML.genElement(f'input', id=f'{el.id}', clas=f'{el.className}', type=f'text', style=f'inputMedium %% {styleInp}', custom=f'name="{value}" value="{el.innerHTML}"')

            if value in knownValues:
                if knownValues[value] is bool:
                    if el.innerHTML == "No":
                        glb.config[value] = True
                        JS.cache("page_portal_tapo", dumps(glb.config))

                        el.innerHTML = "Yes"
                        return None

                    glb.config[value] = False
                    JS.cache("page_portal_tapo", dumps(glb.config))

                    el.innerHTML = "No"
                    return None

                elif knownValues[value] is list:
                    optionsHtml = f''

                    for option in glb.optionsList:
                        optionsHtml += HTML.genElement(f'option', nest=f'{option}', custom=f'value="{option}"')

                    html = HTML.genElement(f'select', nest=f'{optionsHtml}', id=f'{el.id}', clas=f'{el.className}', style=f'selectSmall %% {styleSlc}', custom=f'name="{value}_{len(glb.optionsList)}" size="1" multiple')

            el.outerHTML = html

            el = HTML.getElement(el.id)
            el.style.width = width

            if el.localName == "select":
                el.style.width = f'{float(width.replace("%", "")) + 0.5}%'
                CSS.onHoverFocus(el.id, f'selectHover %% margin-bottom: { - 105 + parantHeight}px;', f'selectFocus %% margin-bottom: { - 105 + parantHeight}px;')
            else:
                CSS.onHoverFocus(el.id, f'inputHover', f'inputFocus')

            JS.addEvent(el.id, submit, "keyup")

        def addMinimal(data):
            def addHeader():
                rowC = 0
                HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

                for header in ["Key", "Value"]:
                    HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{header}', clas=f'SubPage_page_keys', style=f'{styleP}')

                return rowC

            def addRows(data, rowC):
                knownValues = glb.knownConfig
                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

                HTMLrows = f''
                for key in data:
                    rowC += 1
                    HTMLcols = HTML.genElement(f'p', nest=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')
                    value = data[key]

                    if knownValues[key] is int:
                        HTMLcols += HTML.genElement(f'p', nest=f'{value}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    elif knownValues[key] is bool:
                        if value:
                            HTMLcols += HTML.genElement(f'p', nest=f'Yes', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                        else:
                            HTMLcols += HTML.genElement(f'p', nest=f'No', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    elif knownValues[key] is list:
                        HTMLcols += HTML.genElement(f'p', nest=f'{", ".join(value)}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    else:
                        HTMLcols += HTML.genElement(f'p', nest=f'{value}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    HTMLrows += HTML.genElement(f'div', nest=f'{HTMLcols}', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                HTML.addElementRaw(f'SubPage_page', f'{HTMLrows}')

                return rowC

            rowC = addHeader()
            rowC = addRows(data, rowC)

            for item in HTML.getElements("SubPage_page_keys"):
                item.style.width = "50%"

            for item in HTML.getElements("SubPage_page_keys"):
                if item.id != "":
                    JS.addEvent(item, editRecord, "dblclick", isClass=True)

        addMinimal(glb.config)

    pageSubMap = {"Plugs": plugs, "Config": config}

    HTML.clrElement(f'SubPage_page')

    setup(args)

    if not "tapo" in WS.dict():
        login()
        return None

    pageSubMap[JS.cache("page_portalSub")]()


def main(args=None, sub=None):
    HTML.setElement(f'div', f'SubPage', id=f'SubPage_nav', align=f'center', style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.addElement(f'div', f'SubPage', id=f'SubPage_page', align=f'center', style=f'margin: 10px 10px 10px 0px;')

    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_main', align=f'left', style=f'width: 60%')
    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_options', align=f'right', style=f'width: 40%')

    for subPage in glb.subPages:
        HTML.addElement(f'button', f'SubPage_nav_main', nest=f'{subPage}', id=f'SubPage_nav_main_{subPage}', type=f'button', style=f'buttonSmall')

    for subPage in glb.subPages:
        JS.addEvent(f'SubPage_nav_main_{subPage}', pageSub)
        CSS.onHoverClick(f'SubPage_nav_main_{subPage}', f'buttonHover', f'buttonClick')

    if sub is not None:
        JS.cache("page_portalSub", f'{sub}')
        pageSub(args)

import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.JS as JS
from rsa import encrypt
from json import dumps, loads
from datetime import datetime, timedelta


class invoke:
    def TP(args=None):
        glb.mainPage = "Tapo"
        glb.currentSub = ""
        glb.subPages = ["Plugs", "Config"]

        glb.lastUpdate = 0

        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        ws.send(f'tapo state')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    mainPage = ""
    currentSub = ""
    subPages = []

    lastUpdate = 0

    config = {}
    knownConfig = {}
    optionsList = []


def pageSub(args=None):
    def setup(args):
        if JS.cache("page_portal_tapo") is None or JS.cache("page_links") == "":
            pass
            # JS.cache("page_portal_tapo", dumps({}))

        glb.config = {}
        # glb.config = loads(JS.cache("page_portal_tapo"))

        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def login():
        usr = JS.popup(f'prompt', f'Tapo Username')
        if usr is None:
            return None

        psw = JS.popup(f'prompt', f'Tapo Password')
        if psw is None:
            return None

        ws.send(f'<RAW>tapo<SPLIT>login<SPLIT>{usr}<SPLIT>{str(encrypt(psw.encode(), JS.glb.pk))}')

        JS.afterDelay(pageSub, 2000)

    def plugs():
        def slowUIRefresh():
            def update(data):
                for plug in data:
                    HTML.setRaw(f'Gauge_{plug}_power', f'{(data[plug]["currentPower"] / 1000):.2f}<br>Wh')

                    dur = data[plug]["duration"]

                    for applyValue, correctionValue, format, round in [(7884000, 2628000, "M", False), (259200, 86400, "d", False), (10800, 3600, "h", False), (180, 60, "m", True)]:
                        if not dur > applyValue:
                            continue

                        if round:
                            dur = f'{int(dur / correctionValue)}{format}'
                            break

                        dur = f'{(dur / correctionValue):.2f}{format}'
                        break

                    if type(dur) is int:
                        dur = f'{dur}s'

                    HTML.setRaw(f'Gauge_{plug}_uptime', f'{dur}')

                    if data[plug]["overheated"]:
                        CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'100%')
                    else:
                        CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'0%')

                    if not data[plug]["state"]:
                        for i in range(1, 24):
                            CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'0%')

                        CSS.setStyle(f'Power_{plug}', f'background', f'#222')
                        CSS.setStyle(f'Power_{plug}', f'border', f'2px solid #222')
                        continue

                    CSS.setStyle(f'Gauge_{plug}_1', f'opacity', f'100%')

                    for i in range(1, 23):
                        if data[plug]["currentPower"] > i * 20000:
                            CSS.setStyle(f'Gauge_{plug}_{i + 1}', f'opacity', f'100%')
                            continue

                        CSS.setStyle(f'Gauge_{plug}_{i + 1}', f'opacity', f'0%')

            if not glb.currentSub == "Plugs":
                return False

            data = ws.msgDict()["tapo"]

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

                    CSS.setStyle(f'Power_{plug}', f'background', f'#444')
                    CSS.setStyle(f'Power_{plug}', f'border', f'3px solid #FBDF56')

            if not glb.currentSub == "Plugs":
                return False

            data = ws.msgDict()["tapo"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(fastUIRefresh, 250)

        def addPlugs():
            def togglePower(args):
                data = ws.msgDict()["tapo"]
                plug = args.target.id.split("_")[-1]

                if not plug in data:
                    return None

                if not data[plug]["state"]:
                    ws.send(f'tapo on {plug}')

                elif JS.popup(f'confirm', f'Are you sure you want to turn off this device?\nDevice: {plug}'):
                    ws.send(f'tapo off {plug}')

            data = ws.msgDict()["tapo"]

            for plug in data:
                if not data[plug]["model"] in ["P115", "P110"]:
                    continue

                txt = HTML.add(f'h1', _nest=f'{plug}', _style=f'headerMedium %% width: 85%;')
                img = HTML.add(f'img', _id=f'Power_img_{plug}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Tapo/Power.png" alt="Power"')
                btn = HTML.add(f'button', _nest=f'{img}', _id=f'Power_{plug}', _style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                power = HTML.add(f'div', _nest=f'{btn}', _align=f'center', _style=f'width: 15%; min-width: 30px; margin: auto;')

                header = HTML.add(f'div', _nest=f'{txt}{power}', _style=f'flex %% padding-bottom: 10px; border-bottom: 4px dotted #111;')

                img = HTML.add(f'img', _style=f'z-index: 0; width: 100%; margin: auto; position: relative; user-select:none;', _custom=f'src="docs/assets/Portal/Tapo/Gauge/Gauge.png" alt="Gauge"')
                for i in range(1, 24):
                    img += HTML.add(f'img',
                                    _id=f'Gauge_{plug}_{i}',
                                    _style=f'z-index: {i}; width: 100%; margin: auto auto auto -100%; position: relative; opacity: 0%; transition: opacity 0.25s; user-select:none;',
                                    _custom=f'src="docs/assets/Portal/Tapo/Gauge/Gauge_{i}.png" alt="Gauge {i}"')
                txt = HTML.add(f'p', _nest=f'0.00<br>Wh', _id=f'Gauge_{plug}_power', _style=f'z-index: 24; width: 100%; margin: auto auto auto -100%; padding: 0px 0px 5% 0px; line-height: 100%; font-weight: bold; position: relative; user-select:none;')
                txt += HTML.add(f'p', _nest=f'0.00h', _id=f'Gauge_{plug}_uptime', _style=f'z-index: 25; width: 100%; margin: auto auto auto -100%; padding: 50% 0px 0px 0px; font-weight: bold; position: relative; user-select:none;')
                txt += HTML.add(f'h1',
                                _nest=f'Overheated!',
                                _id=f'Gauge_{plug}_overheat',
                                _style=f'headerMedium %% z-index: 26; width: 100%; margin: auto auto -20px -100%; color: #F00; position: relative; opacity: 0%; transition: opacity 0.25s; user-select:none;')

                body = HTML.add(f'div', _nest=f'{img}{txt}', _style=f'flex %% padding: 20px 10px; border-bottom: 4px dotted #111;')

                HTML.add(f'div', f'SubPage_page_main', _nest=f'{header}{body}', _id=f'SubPage_page_main_{plug}', _style=f'divNormal %% min-width: 150px; margin: 15px; padding: 5px 15px 15px 15px; border: 4px solid #55F; border-radius: 4px;')

            for plug in data:
                if not data[plug]["model"] in ["P115", "P110"]:
                    continue

                JS.addEvent(f'Power_{plug}', togglePower)
                CSS.onHover(f'Power_{plug}', f'imgHover')
                CSS.onClick(f'Power_{plug}', f'imgClick')

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal %% flex %% margin: 15px 30px 15px auto; overflow-y: hidden;')

        addPlugs()

        JS.afterDelay(fastUIRefresh, 250)
        JS.afterDelay(slowUIRefresh, 1000)

    def config():
        def editRecord(args):
            def submit(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = HTML.get(f'{args.target.id}')

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

                    elif knownValues[value] is list:
                        data = []

                        for i in range(0, int(args.target.name.split("_")[1])):
                            if args.target.item(i).selected is True:
                                data.append(args.target.item(i).value)

                        data = ", ".join(data).replace(" ", "%20")
                        html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{data.replace("%20", " ")}</p>'

                glb.config[value] = data
                JS.cache("page_portal_sonos", dumps(glb.config))

                el.outerHTML = html

                CSS.setStyle(f'{el.id}', f'width', f'{width}')

                JS.addEvent(el.id, editRecord, "dblclick")

            el = HTML.get(f'{args.target.id}')
            width = el.style.width
            parantHeight = HTML.get(el.parentElement.id).offsetHeight

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
            html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{el.innerHTML}"')

            if value in knownValues:
                if knownValues[value] is int:
                    html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{el.innerHTML}"')

                elif knownValues[value] is bool:
                    if el.innerHTML == "No":
                        glb.config[value] = True
                        JS.cache("page_portal_sonos", dumps(glb.config))

                        el.innerHTML = "Yes"
                        return None

                    glb.config[value] = False
                    JS.cache("page_portal_sonos", dumps(glb.config))

                    el.innerHTML = "No"
                    return None

                elif knownValues[value] is list:
                    optionsHtml = f''

                    for option in glb.optionsList:
                        optionsHtml += HTML.add(f'option', _nest=f'{option}', _custom=f'value="{option}"')

                    html = HTML.add(f'select', _nest=f'{optionsHtml}', _id=f'{el.id}', _class=f'{el.className}', _style=f'selectSmall %% {styleSlc}', _custom=f'name="{value}_{len(glb.optionsList)}" size="1" multiple')

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

            JS.addEvent(el.id, submit, "keyup")

        def addMinimal(data):
            def addHeader():
                rowC = 0
                HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

                for header in ["Key", "Value"]:
                    HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{header}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                return rowC

            def addRows(data, rowC):
                knownValues = glb.knownConfig
                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

                HTMLrows = f''
                for key in data:
                    rowC += 1
                    HTMLcols = HTML.add(f'p', _nest=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')
                    value = data[key]

                    if knownValues[key] is int:
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

        addMinimal(glb.config)

    pageSubMap = {"Plugs": plugs, "Config": config}

    HTML.clear(f'SubPage_page')

    if not args is None:
        setup(args)

    if not "tapo" in ws.msgDict():
        login()
        return None

    pageSubMap[glb.currentSub]()


def main(args=None, sub=None):
    HTML.set(f'div', f'SubPage', _id=f'SubPage_nav', _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.add(f'div', f'SubPage', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')

    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'left', _style=f'width: 60%')
    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_options', _align=f'right', _style=f'width: 40%')

    for subPage in glb.subPages:
        HTML.add(f'button', f'SubPage_nav_main', _nest=f'{subPage}', _id=f'SubPage_nav_main_{subPage}', _type=f'button', _style=f'buttonSmall')

    for subPage in glb.subPages:
        JS.addEvent(f'SubPage_nav_main_{subPage}', pageSub)
        CSS.onHover(f'SubPage_nav_main_{subPage}', f'buttonHover')
        CSS.onClick(f'SubPage_nav_main_{subPage}', f'buttonClick')

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

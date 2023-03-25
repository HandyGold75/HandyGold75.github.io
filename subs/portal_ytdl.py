import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.JS as JS
from rsa import encrypt
from json import dumps, loads
from datetime import datetime, timedelta


class invoke:
    def YTDL(args=None):
        glb.mainPage = "YT-DL"
        glb.currentSub = ""
        glb.subPages = ["Download", "History", "Config"]

        glb.lastUpdate = 0

        glb.dates = ["Modified"]

        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        ws.send(f'yt state')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    mainPage = ""
    currentSub = ""
    subPages = []

    lastUpdate = 0
    lastDownload = 0

    dates = []

    config = {}
    knownConfig = {"costPerKw": float, "costFormat": str}
    optionsList = []


def pageSub(args=None):
    def setup(args):
        if JS.cache("page_portal_ytdl") is None or JS.cache("page_links") == "":
            # JS.cache("page_portal_ytdl", dumps({}))
            pass

        # glb.config = loads(JS.cache("page_portal_ytdl"))

        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def download():
        def slowUIRefresh():
            def update(data):
                records = ""
                for index in reversed(data["downloads"]):
                    values = ""

                    for key in data["downloads"][index]:
                        txt = HTML.add("p", _nest=f'{key}', _style=f'width: 50%; margin: 0px auto')

                        if not key in glb.dates:
                            txt += HTML.add("p", _nest=f'{data["downloads"][index][key]}', _style=f'width: 50%; margin: 0px auto')
                        else:
                            txt += HTML.add("p", _nest=f'{datetime.fromtimestamp(data["downloads"][index][key]).strftime("%d %b %y - %H:%M")}', _style=f'width: 50%; margin: 0px auto')

                        values += HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% margin: 0px auto')

                    records += HTML.add("div", _nest=f'{values}', _style=f'divNormal %% margin: 0px auto; border: 4px solid #111; border-radius: 4px;')

                HTML.set("div", f'SubPage_page_results_out', _nest=f'{records}', _style=f'divNormal')

            if not glb.currentSub == "Download":
                return False

            data = ws.msgDict()["yt"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(getData, 4000)
            JS.afterDelay(slowUIRefresh, 5000)

        def addHeader():
            HTML.add(f'h1', f'SubPage_page_header', _nest=f'YouTube Downloader', _style=f'headerBig %% margin: 0px auto;')

        def addDownload():
            def submitDownload(args):
                if hasattr(args, "key") and not args.key in ["Enter"]:
                    return None

                input = HTML.get(f'download_input').value

                if not input.startswith("https://www.youtube.com/watch?v=") and not input.startswith("https://www.youtube.com/shorts/"):
                    return None

                if (datetime.now() - timedelta(seconds=15)).timestamp() < glb.lastDownload:
                    JS.popup("alert", f'Please wait {int(glb.lastDownload - (datetime.now() - timedelta(seconds=15)).timestamp())} seconds until starting the next download.')
                    return None

                glb.lastDownload = datetime.now().timestamp()
                ws.send(f'yt download {input}')

            HTML.add(f'input', f'SubPage_page_download', _id=f'download_input', _type=f'text', _style=f'inputMedium %% width: 75%;')
            HTML.add(f'button', f'SubPage_page_download', _nest=f'Download', _id=f'download_button', _type=f'button', _style=f'buttonMedium %% width: 25%;')

            JS.addEvent(f'download_input', submitDownload, "keyup")
            CSS.onHover(f'download_input', f'inputHover')
            CSS.onFocus(f'download_input', f'inputFocus')

            JS.addEvent(f'download_button', submitDownload)
            CSS.onHover(f'download_button', f'buttonHover')
            CSS.onClick(f'download_button', f'buttonClick')

        def addResults():
            data = ws.msgDict()["yt"]

            HTML.add(f'h1', f'SubPage_page_results', _nest=f'Recent Downloads', _style=f'headerBig %% margin: 0px auto;')
            HTML.add(f'div', f'SubPage_page_results', _id=f'SubPage_page_results_out', _style=f'divNormal')

            for index in data["downloads"]:
                JS.log(str(data["downloads"][index]))

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_header', _style=f'divNormal %% flex')
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_download', _style=f'divNormal %% flex %% width: 75%;')
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_results', _style=f'divNormal %% border: 4px solid #111; border-radius: 4px;')

        addHeader()
        addDownload()
        addResults()

        JS.afterDelay(slowUIRefresh, 500)

    def history():
        def addPage():
            pass

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal')

        addPage()

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

                glb.config[value] = data
                JS.cache("page_portal_tapo", dumps(glb.config))

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

    pageSubMap = {"Download": download, "History": history, "Config": config}

    HTML.clear(f'SubPage_page')

    if not args is None:
        setup(args)

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

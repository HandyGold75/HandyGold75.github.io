from WebKit import HTML, CSS, JS
from WebKit.WebSocket import WS
from json import dumps, loads
from datetime import datetime, timedelta


class invoke:
    def YTDL(args=None):
        glb.subPages = ["Download", "History", "Config"]
        glb.dates = ["Modified"]

        glb.lastUpdate = 0

        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        WS.send(f'yt state')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    subPages = []
    dates = []

    lastUpdate = 0
    lastDownload = 0

    config = {}
    knownConfig = {"quality": list, "audioOnly": bool}
    optionsList = ["Low", "Medium", "High"]

    lastDataPackage = {}


def pageSub(args=None):
    def setup(args):
        if JS.cache("page_portal_ytdl") is None or JS.cache("page_portal_ytdl") == "":
            JS.cache("page_portal_ytdl", dumps({"quality": ["Medium"], "audioOnly": False}))
            pass

        glb.config = loads(JS.cache("page_portal_ytdl"))

        if not args is None and f'{args.target.id.split("_")[-1]}' in glb.subPages:
            JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

    def download():
        def slowUIRefresh():
            def update(data):
                def removeFromDownload(args):
                    el = args.target

                    for i in range(0, 6):
                        if el.id == "":
                            el = el.parentElement
                            continue

                        try:
                            int(el.id.split("_")[-1])
                        except ValueError:
                            el = el.parentElement
                            continue

                        WS.send(f'yt remove {el.id.split("_")[-1]}')
                        return None

                records = ""

                if data == glb.lastDataPackage:
                    return None

                glb.lastDataPackage = data

                for index in reversed(data["downloads"]):
                    values = HTML.genElement("h1", nest=f'{index}', style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                    remImg = HTML.genElement(f'img', id=f'SubPage_page_results_rem_img_{index}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                    remBtn = HTML.genElement(f'button', nest=f'{remImg}', id=f'SubPage_page_results_rem_{index}', style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                    rem = HTML.genElement(f'div', nest=f'{remBtn}', align=f'right', style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                    values += HTML.genElement(f'div', nest=f'{rem}', style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                    if type(data["downloads"][index]["Modified"]) is int:
                        data["downloads"][index]["Modified"] = f'{datetime.fromtimestamp(data["downloads"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                    for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                        if not key2 is None:
                            txt = HTML.genElement("p", nest=key1, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            if key1 == "State":
                                if data["downloads"][index][key1] == "Done":
                                    txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                                elif data["downloads"][index][key1] == "Failed":
                                    txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                                else:
                                    txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                            else:
                                txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                        else:
                            txt = HTML.genElement("p", nest=key1, style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                            div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                        if not key2 is None:
                            txt = HTML.genElement("p", nest=key2, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.genElement("p", nest=f'{data["downloads"][index][key2]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div += HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                            values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                            continue

                        values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    if not data["downloads"][index]["Error"] == "":
                        txt = HTML.genElement("p", nest=f'Error', style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.genElement("p", nest=f'{data["downloads"][index]["Error"]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                        div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                        values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    records += HTML.genElement("div", nest=f'{values}', style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

                HTML.setElement("div", f'SubPage_page_results_out', nest=f'{records}', style=f'divNormal')

                for index in reversed(data["downloads"]):
                    JS.addEvent(f'SubPage_page_results_rem_{index}', removeFromDownload)
                    CSS.onHoverClick(f'SubPage_page_results_rem_{index}', f'imgHover', f'imgClick')

            if not JS.cache("page_portalSub") == "Download":
                return False

            data = WS.dict()["yt"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(getData, 2000)
            JS.afterDelay(slowUIRefresh, 2500)

        def addHeader():
            HTML.addElement(f'h1', f'SubPage_page_header', nest=f'YouTube Downloader', style=f'headerBig %% margin: 0px auto;')

        def addDownload():
            def submitDownload(args):
                if hasattr(args, "key") and not args.key in ["Enter"]:
                    return None

                input = HTML.getElement("download_input").value

                if not input.startswith("https://www.youtube.com/watch?v=") and not input.startswith("https://www.youtube.com/shorts/"):
                    return None

                if (datetime.now() - timedelta(seconds=15)).timestamp() < glb.lastDownload:
                    JS.popup("alert", f'Please wait {int(glb.lastDownload - (datetime.now() - timedelta(seconds=15)).timestamp())} seconds until starting the next download.')
                    return None

                glb.lastDownload = datetime.now().timestamp()

                if glb.config["audioOnly"]:
                    WS.send(f'yt download audio {glb.config["quality"][0]} {input}')
                else:
                    WS.send(f'yt download video {glb.config["quality"][0]} {input}')

            HTML.addElement(f'input', f'SubPage_page_download', id=f'download_input', type=f'text', style=f'inputMedium %% width: 75%;')
            HTML.addElement(f'button', f'SubPage_page_download', nest=f'Download', id=f'download_button', type=f'button', style=f'buttonMedium %% width: 25%;')

            JS.addEvent(f'download_input', submitDownload, "keyup")
            CSS.onHoverFocus(f'download_input', f'inputHover', f'inputFocus')

            JS.addEvent(f'download_button', submitDownload)
            CSS.onHoverClick(f'download_button', f'buttonHover', f'buttonClick')

        def addResults():
            data = WS.dict()["yt"]

            HTML.addElement(f'h1', f'SubPage_page_results', nest=f'Recent Downloads', style=f'headerBig %% margin: 0px auto;')
            HTML.addElement(f'div', f'SubPage_page_results', id=f'SubPage_page_results_out', style=f'divNormal %% margin-bottom: 0px;')

        HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_header', style=f'divNormal %% flex %% width: 95%;')
        HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_download', style=f'divNormal %% flex %% width: 75%;')
        HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_results', style=f'divNormal %% width: 95%; margin-top: 50px;')

        addHeader()
        addDownload()
        addResults()

        JS.afterDelay(slowUIRefresh, 50)

    def history():
        def update(data):
            def removeFromDownload(args):
                el = args.target

                for i in range(0, 6):
                    if el.id == "":
                        el = el.parentElement
                        continue

                    try:
                        int(el.id.split("_")[-1])
                    except ValueError:
                        el = el.parentElement
                        continue

                    WS.send(f'yt remove {el.id.split("_")[-1]}')
                    return None

            records = ""

            if data == glb.lastDataPackage:
                return None

            glb.lastDataPackage = data

            for index in reversed(data["history"]):
                values = HTML.genElement("h1", nest=f'{index}', style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                remImg = HTML.genElement(f'img', id=f'SubPage_page_results_rem_img_{index}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                remBtn = HTML.genElement(f'button', nest=f'{remImg}', id=f'SubPage_page_results_rem_{index}', style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                rem = HTML.genElement(f'div', nest=f'{remBtn}', align=f'right', style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                values += HTML.genElement(f'div', nest=f'{rem}', style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                if type(data["history"][index]["Modified"]) is int:
                    data["history"][index]["Modified"] = f'{datetime.fromtimestamp(data["history"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                    if not key2 is None:
                        txt = HTML.genElement("p", nest=key1, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        if key1 == "State":
                            if data["history"][index][key1] == "Done":
                                txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                            elif data["history"][index][key1] == "Failed":
                                txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                            else:
                                txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                        else:
                            txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                        div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                    else:
                        txt = HTML.genElement("p", nest=key1, style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                        div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                    if not key2 is None:
                        txt = HTML.genElement("p", nest=key2, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.genElement("p", nest=f'{data["history"][index][key2]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                        div += HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                        values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                        continue

                    values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                if not data["history"][index]["Error"] == "":
                    txt = HTML.genElement("p", nest=f'Error', style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                    txt += HTML.genElement("p", nest=f'{data["history"][index]["Error"]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                    div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                    values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                records += HTML.genElement("div", nest=f'{values}', style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

            HTML.setElement("div", f'SubPage_page_results_out', nest=f'{records}', style=f'divNormal')

            for index in reversed(data["history"]):
                JS.addEvent(f'SubPage_page_results_rem_{index}', removeFromDownload)
                CSS.onHoverClick(f'SubPage_page_results_rem_{index}', f'imgHover', f'imgClick')

        def addHeader():
            HTML.addElement(f'h1', f'SubPage_page_header', nest=f'History', style=f'headerBig %% margin: 0px auto;')

        def addResults():
            data = WS.dict()["yt"]

            HTML.addElement(f'div', f'SubPage_page_results', id=f'SubPage_page_results_out', style=f'divNormal %% margin-bottom: 0px;')
            update(data)

        HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_header', style=f'divNormal %% flex %% width: 95%;')
        HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_results', style=f'divNormal %% width: 95%; margin-top: 50px;')

        addHeader()
        addResults()

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
                JS.cache("page_portal_ytdl", dumps(glb.config))

                el.outerHTML = html

                CSS.setStyle(el.id, "width", str(width))

                JS.addEvent(el.id, editRecord, "dblclick")

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
                        JS.cache("page_portal_ytdl", dumps(glb.config))

                        el.innerHTML = "Yes"
                        return None

                    glb.config[value] = False
                    JS.cache("page_portal_ytdl", dumps(glb.config))

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

    pageSubMap = {"Download": download, "History": history, "Config": config}

    HTML.clrElement(f'SubPage_page')
    glb.lastDataPackage = {}

    setup(args)

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

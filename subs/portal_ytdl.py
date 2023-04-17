from WebKit import HTML, CSS, JS, WS
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
        WS.send(f'yt state')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    mainPage = ""
    currentSub = ""
    subPages = []

    lastUpdate = 0
    lastDownload = 0

    dates = []

    config = {}
    knownConfig = {"quality": list, "audioOnly": bool}
    optionsList = ["Low", "Medium", "High"]

    lastDataPackage = {}


def pageSub(args=None):
    def setup(args):
        if JS.cache("page_portal_ytdl") is None or JS.cache("page_links") == "":
            JS.cache("page_portal_ytdl", dumps({"quality": ["Medium"], "audioOnly": False}))
            pass

        glb.config = loads(JS.cache("page_portal_ytdl"))

        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

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
                    values = HTML.add("h1", _nest=f'{index}', _style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                    remImg = HTML.add(f'img', _id=f'SubPage_page_results_rem_img_{index}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                    remBtn = HTML.add(f'button', _nest=f'{remImg}', _id=f'SubPage_page_results_rem_{index}', _style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                    rem = HTML.add(f'div', _nest=f'{remBtn}', _align=f'right', _style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                    values += HTML.add(f'div', _nest=f'{rem}', _style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                    if type(data["downloads"][index]["Modified"]) is int:
                        data["downloads"][index]["Modified"] = f'{datetime.fromtimestamp(data["downloads"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                    for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                        if not key2 is None:
                            txt = HTML.add("p", _nest=key1, _style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            if key1 == "State":
                                if data["downloads"][index][key1] == "Done":
                                    txt += HTML.add("p", _nest=f'{data["downloads"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                                elif data["downloads"][index][key1] == "Failed":
                                    txt += HTML.add("p", _nest=f'{data["downloads"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                                else:
                                    txt += HTML.add("p", _nest=f'{data["downloads"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                            else:
                                txt += HTML.add("p", _nest=f'{data["downloads"][index][key1]}', _style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                        else:
                            txt = HTML.add("p", _nest=key1, _style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.add("p", _nest=f'{data["downloads"][index][key1]}', _style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                            div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                        if not key2 is None:
                            txt = HTML.add("p", _nest=key2, _style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.add("p", _nest=f'{data["downloads"][index][key2]}', _style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div += HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                            values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                            continue

                        values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    if not data["downloads"][index]["Error"] == "":
                        txt = HTML.add("p", _nest=f'Error', _style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.add("p", _nest=f'{data["downloads"][index]["Error"]}', _style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                        div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                        values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    records += HTML.add("div", _nest=f'{values}', _style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

                HTML.set("div", f'SubPage_page_results_out', _nest=f'{records}', _style=f'divNormal')

                for index in reversed(data["downloads"]):
                    JS.addEvent(f'SubPage_page_results_rem_{index}', removeFromDownload)
                    CSS.onHover(f'SubPage_page_results_rem_{index}', f'imgHover')
                    CSS.onClick(f'SubPage_page_results_rem_{index}', f'imgClick')

            if not glb.currentSub == "Download":
                return False

            data = WS.dict()["yt"]

            try:
                update(data)
            except AttributeError:
                return None

            JS.afterDelay(getData, 2000)
            JS.afterDelay(slowUIRefresh, 2500)

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

                if glb.config["audioOnly"]:
                    WS.send(f'yt download audio {glb.config["quality"][0]} {input}')
                else:
                    WS.send(f'yt download video {glb.config["quality"][0]} {input}')

            HTML.add(f'input', f'SubPage_page_download', _id=f'download_input', _type=f'text', _style=f'inputMedium %% width: 75%;')
            HTML.add(f'button', f'SubPage_page_download', _nest=f'Download', _id=f'download_button', _type=f'button', _style=f'buttonMedium %% width: 25%;')

            JS.addEvent(f'download_input', submitDownload, "keyup")
            CSS.onHover(f'download_input', f'inputHover')
            CSS.onFocus(f'download_input', f'inputFocus')

            JS.addEvent(f'download_button', submitDownload)
            CSS.onHover(f'download_button', f'buttonHover')
            CSS.onClick(f'download_button', f'buttonClick')

        def addResults():
            data = WS.dict()["yt"]

            HTML.add(f'h1', f'SubPage_page_results', _nest=f'Recent Downloads', _style=f'headerBig %% margin: 0px auto;')
            HTML.add(f'div', f'SubPage_page_results', _id=f'SubPage_page_results_out', _style=f'divNormal %% margin-bottom: 0px;')

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_header', _style=f'divNormal %% flex %% width: 95%;')
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_download', _style=f'divNormal %% flex %% width: 75%;')
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_results', _style=f'divNormal %% width: 95%; margin-top: 50px;')

        addHeader()
        addDownload()
        addResults()

        JS.afterDelay(slowUIRefresh, 500)

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
                values = HTML.add("h1", _nest=f'{index}', _style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                remImg = HTML.add(f'img', _id=f'SubPage_page_results_rem_img_{index}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                remBtn = HTML.add(f'button', _nest=f'{remImg}', _id=f'SubPage_page_results_rem_{index}', _style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                rem = HTML.add(f'div', _nest=f'{remBtn}', _align=f'right', _style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                values += HTML.add(f'div', _nest=f'{rem}', _style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                if type(data["history"][index]["Modified"]) is int:
                    data["history"][index]["Modified"] = f'{datetime.fromtimestamp(data["history"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                    if not key2 is None:
                        txt = HTML.add("p", _nest=key1, _style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        if key1 == "State":
                            if data["history"][index][key1] == "Done":
                                txt += HTML.add("p", _nest=f'{data["history"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                            elif data["history"][index][key1] == "Failed":
                                txt += HTML.add("p", _nest=f'{data["history"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                            else:
                                txt += HTML.add("p", _nest=f'{data["history"][index][key1]}', _style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                        else:
                            txt += HTML.add("p", _nest=f'{data["history"][index][key1]}', _style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                        div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                    else:
                        txt = HTML.add("p", _nest=key1, _style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.add("p", _nest=f'{data["history"][index][key1]}', _style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                        div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                    if not key2 is None:
                        txt = HTML.add("p", _nest=key2, _style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.add("p", _nest=f'{data["history"][index][key2]}', _style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                        div += HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                        values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                        continue

                    values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                if not data["history"][index]["Error"] == "":
                    txt = HTML.add("p", _nest=f'Error', _style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                    txt += HTML.add("p", _nest=f'{data["history"][index]["Error"]}', _style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                    div = HTML.add("div", _nest=f'{txt}', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                    values += HTML.add("div", _nest=f'{div}', _style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                records += HTML.add("div", _nest=f'{values}', _style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

            HTML.set("div", f'SubPage_page_results_out', _nest=f'{records}', _style=f'divNormal')

            for index in reversed(data["history"]):
                JS.addEvent(f'SubPage_page_results_rem_{index}', removeFromDownload)
                CSS.onHover(f'SubPage_page_results_rem_{index}', f'imgHover')
                CSS.onClick(f'SubPage_page_results_rem_{index}', f'imgClick')

        def addHeader():
            HTML.add(f'h1', f'SubPage_page_header', _nest=f'History', _style=f'headerBig %% margin: 0px auto;')

        def addResults():
            data = WS.dict()["yt"]

            HTML.add(f'div', f'SubPage_page_results', _id=f'SubPage_page_results_out', _style=f'divNormal %% margin-bottom: 0px;')
            update(data)

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_header', _style=f'divNormal %% flex %% width: 95%;')
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_results', _style=f'divNormal %% width: 95%; margin-top: 50px;')

        addHeader()
        addResults()

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

                        html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{", ".join(data).replace(" ", "%20")}</p>'

                glb.config[value] = data
                JS.cache("page_portal_ytdl", dumps(glb.config))

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
    glb.lastDataPackage = {}

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

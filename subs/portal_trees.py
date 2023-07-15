from WebKit import HTML, CSS, JS
from WebKit.WebSocket import WS
from datetime import datetime, timedelta


class invoke:
    def MO(args=None):
        glb.knownTree = {"Current": {"sId": int, "cl": dict, "wsAuth": dict, "logStack": dict}, "All": {"cl": dict, "wsAuth": dict, "logStack": dict}}
        glb.dates = ["Expires", "Modified", "time"]
        glb.svcoms = {"main": "monitor", "read": "read"}

        glb.lastUpdate = 0

        getData()


class glb:
    knownTree = {}
    dates = []
    svcoms = {}

    lastUpdate = 0


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        WS.send(f'{glb.svcoms["main"]} {glb.svcoms["read"]}')

        glb.lastUpdate = datetime.now().timestamp()


def pageSub(args):
    def setup(args):
        data = WS.dict()[glb.svcoms["main"]]

        if not args is None and f'{args.target.id.split("_")[-1]}' in glb.knownTree:
            JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

        if not JS.cache("page_portalSub") in data:
            return None

        data = data[JS.cache("page_portalSub")]

        if data == {}:
            data[" "] = {}
            mainValue = list(glb.knownTree[JS.cache("page_portalSub")])[-1]
            data[" "] = {}

            for value in glb.knownTree[JS.cache("page_portalSub")][mainValue]:
                data[" "][value] = glb.knownTree[JS.cache("page_portalSub")][mainValue][value]()

        return data

    def addTree(data):
        def recursive(data, rowC, colC, layer, prtSpc={}):
            if layer + 2 > colC:
                colC = layer + 2

            styleP = f'margin: 0px; padding: 0px; text-align: left; font-size: 75%; white-space: nowrap;'
            prtChar = "bCross"
            prtSpc[f'{layer}'] = True

            for i, record in enumerate(data):
                if len(data) - 1 == i:
                    prtChar = "bEnd"

                    if record == list(data)[-1]:
                        prtSpc[f'{layer}'] = False

                spacer = ""

                if layer > 1:
                    for i1 in range(1, layer):
                        if prtSpc[str(i1)]:
                            spacer += HTML.genElement(f'p', clas=f'SubPage_page_bLeft', style=f'{styleP}')
                            continue

                        spacer += HTML.genElement(f'p', clas=f'SubPage_page_rows_p1', style=f'{styleP}')

                if layer > 0:
                    if prtChar == "bCross":
                        spacer += HTML.genElement(f'p', nest=f'───────────────', clas=f'SubPage_page_bCross', style=f'{styleP}')
                    elif prtChar == "bEnd":
                        spacer += HTML.genElement(f'p', clas=f'SubPage_page_bEnd', style=f'{styleP}')

                if type(data[record]) is dict:
                    HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                    HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{record}', prepend=f'{spacer}', clas=f'SubPage_page_rows_p1', style=f'{styleP.replace("left", "center")}')

                    rowC, colC = recursive(data[record], rowC + 1, colC, layer + 1, prtSpc)

                else:
                    HTML.addElement(f'div', f'SubPage_page', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                    value = data[record]

                    if record in glb.dates:
                        value = datetime.fromtimestamp(value).strftime("%d-%m-%y %H:%M")

                    if layer > 0:
                        HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{record}:', prepend=f'{spacer}', clas=f'SubPage_page_rows_p1', style=f'{styleP}')
                    else:
                        HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{record}:', prepend=f'{spacer}', clas=f'SubPage_page_rows_p1', style=f'{styleP.replace("left", "center")}')

                    HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{value}', clas=f'SubPage_page_rows_p2', style=f'{styleP}')

                    rowC += 1

            return rowC, colC

        rowC, colC = recursive(data, 0, 0, 0)

        for item in HTML.getElements("SubPage_page_rows_p1"):
            item.style.width = f'{80 / colC}%'
            item.style.marginTop = "3px"

        for item in HTML.getElements("SubPage_page_rows_p2"):
            item.style.width = f'{140 / colC}%'
            item.style.marginTop = "3px"
            item.style.whiteSpace = "normal"
            item.style.wordWrap = "break-word"

        for item in HTML.getElements("SubPage_page_bCross"):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.fontSize = "100%"
            item.style.overflow = "hidden"
            item.style.borderLeft = "2px solid #44F"
            item.style.userSelect = "none"

        for item in HTML.getElements("SubPage_page_bEnd"):
            item.style.width = f'{40/ colC}%'
            item.style.height = "12px"
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = "2px solid #44F"
            item.style.borderBottom = "2px solid #44F"

        for item in HTML.getElements("SubPage_page_bLeft"):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = "2px solid #44F"

        for item in HTML.getElements("SubPage_page_bBottom"):
            item.style.width = f'{80/ colC}%'
            item.style.height = "9px"
            item.style.borderBottom = "2px solid #44F"

    HTML.clrElement(f'SubPage_page')

    data = setup(args)

    if data is None:
        return None

    addTree(data)


def main(args=None, sub=None):
    HTML.setElement(f'div', f'SubPage', id=f'SubPage_nav', align=f'center', style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.addElement(f'div', f'SubPage', id=f'SubPage_page', align=f'center', style=f'margin: 10px 10px 10px 0px;')

    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_main', align=f'left', style=f'width: 60%')
    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_options', align=f'right', style=f'width: 40%')

    data = WS.dict()[glb.svcoms["main"]]

    foundFile = False

    for file in data:
        if file in glb.knownTree:
            fileName = f'{file.replace("/", "").replace(".json", "").replace(".log", "")}'
            HTML.addElement(f'button', f'SubPage_nav_main', nest=f'{fileName}', id=f'SubPage_nav_main_{fileName}', type=f'button', style=f'buttonSmall')
            foundFile = True

    if not foundFile:
        HTML.setElement(f'div', f'SubPage_nav', id=f'SubPage_nav_main', align=f'center', style=f'width: 100%')
        HTML.addElement(f'h2', f'SubPage_nav_main', nest=f'Unauthorized!', style=f'margin: 10px auto; text-align: center;')
        HTML.disableElement(f'page_portal_{JS.cache("page_portal")}')

        return None

    for tree in data:
        if tree in glb.knownTree:
            JS.addEvent(f'SubPage_nav_main_{tree}', pageSub)
            JS.addEvent(f'SubPage_nav_main_{tree}', getData, f'mousedown')
            CSS.onHoverClick(f'SubPage_nav_main_{tree}', f'buttonHover', f'buttonClick')

    if sub is not None:
        JS.cache("page_portalSub", f'{sub}')
        pageSub(args)

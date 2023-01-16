import mod.HTML as HTML
import mod.ws as ws
import mod.functions as f
from datetime import datetime, timedelta


class invoke:
    def MO(args=None):
        glb.mainPage = "Monitor"
        glb.currentSub = ""

        glb.lastUpdate = 0
        glb.knownTree = {"Current": {"sId": int, "cl": dict, "wsAuth": dict, "logStack": dict}, "All": {"cl": dict, "wsAuth": dict, "logStack": dict}}

        glb.dates = ["Expires", "Modified", "time"]

        glb.svcoms = {"main": "monitor", "read": "read"}

        getData()


class glb:
    mainPage = ""
    currentSub = ""

    lastUpdate = 0
    knownTree = {}

    dates = []

    svcoms = {}


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        try:
            ws.send(f'{glb.svcoms["main"]} {glb.svcoms["read"]}')
        except ConnectionError:
            f.connectionError()

        glb.lastUpdate = datetime.now().timestamp()


def pageSub(args):
    def setup(args):
        try:
            data = ws.msgDict()[glb.svcoms["main"]]
        except ConnectionError:
            f.connectionError()
            return None

        if f'{args.target.id.split("_")[-1]}' in glb.knownTree:
            glb.currentSub = args.target.id.split("_")[-1]

        if not glb.currentSub in data:
            return None

        data = data[glb.currentSub]

        if data == {}:
            data[" "] = {}
            mainValue = list(glb.knownTree[glb.currentSub])[-1]
            data[" "] = {}

            for value in glb.knownTree[glb.currentSub][mainValue]:
                data[" "][value] = glb.knownTree[glb.currentSub][mainValue][value]()

        return data

    def addRow(rowC):
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

        return HTML.get(f'SubPage_page_row{rowC}'), rowC + 1

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
                            spacer += HTML.add(f'p', _class=f'SubPage_page_bLeft', _style=f'{styleP}')
                            continue

                        spacer += HTML.add(f'p', _class=f'SubPage_page_rows_p1', _style=f'{styleP}')

                if layer > 0:
                    if prtChar == "bCross":
                        spacer += HTML.add(f'p', _nest=f'───────────────', _class=f'SubPage_page_bCross', _style=f'{styleP}')
                    elif prtChar == "bEnd":
                        spacer += HTML.add(f'p', _class=f'SubPage_page_bEnd', _style=f'{styleP}')

                if type(data[record]) is dict:
                    HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                    HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{record}', _prepend=f'{spacer}', _class=f'SubPage_page_rows_p1', _style=f'{styleP.replace("left", "center")}')

                    rowC, colC = recursive(data[record], rowC + 1, colC, layer + 1, prtSpc)

                else:
                    HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                    value = data[record]

                    if record in glb.dates:
                        value = datetime.fromtimestamp(value).strftime("%d-%m-%y %H:%M")

                    if layer > 0:
                        HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{record}:', _prepend=f'{spacer}', _class=f'SubPage_page_rows_p1', _style=f'{styleP}')
                    else:
                        HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{record}:', _prepend=f'{spacer}', _class=f'SubPage_page_rows_p1', _style=f'{styleP.replace("left", "center")}')

                    HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{value}', _class=f'SubPage_page_rows_p2', _style=f'{styleP}')

                    rowC += 1

            return rowC, colC

        rowC, colC = recursive(data, 0, 0, 0)

        for item in HTML.get(f'SubPage_page_rows_p1', isClass=True):
            item.style.width = f'{80 / colC}%'
            item.style.marginTop = f'3px'

        for item in HTML.get(f'SubPage_page_rows_p2', isClass=True):
            item.style.width = f'{140 / colC}%'
            item.style.marginTop = f'3px'
            item.style.whiteSpace = f'normal'
            item.style.wordWrap = f'break-word'

        for item in HTML.get(f'SubPage_page_bCross', isClass=True):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.fontSize = f'100%'
            item.style.overflow = f'hidden'
            item.style.borderLeft = f'2px solid #44F'

        for item in HTML.get(f'SubPage_page_bEnd', isClass=True):
            item.style.width = f'{40/ colC}%'
            item.style.height = f'12px'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = f'2px solid #44F'
            item.style.borderBottom = f'2px solid #44F'

        for item in HTML.get(f'SubPage_page_bLeft', isClass=True):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = f'2px solid #44F'

        for item in HTML.get(f'SubPage_page_bBottom', isClass=True):
            item.style.width = f'{80/ colC}%'
            item.style.height = f'9px'
            item.style.borderBottom = f'2px solid #44F'

    HTML.clear(f'SubPage_page')

    data = setup(args)

    if data is None:
        return None

    addTree(data)


def main(args=None, sub=None):
    HTML.set(f'div', f'SubPage', _id=f'SubPage_nav', _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.add(f'div', f'SubPage', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')

    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'left', _style=f'width: 60%')
    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_options', _align=f'right', _style=f'width: 40%')

    try:
        data = ws.msgDict()[glb.svcoms["main"]]
    except ConnectionError:
        f.connectionError()
        return None

    foundFile = False

    for file in data:
        if file in glb.knownTree:
            fileName = f'{file.replace("/", "").replace(".json", "").replace(".dmp", "")}'
            HTML.add(f'button', f'SubPage_nav_main', _nest=f'{fileName}', _id=f'SubPage_nav_main_{fileName}', _type=f'button', _style=f'border: 2px solid #44F; font-size: 75%;')
            foundFile = True

    if not foundFile:
        HTML.set(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'center', _style=f'width: 100%')
        HTML.add(f'h2', f'SubPage_nav_main', _nest=f'Unauthorized!', _style=f'margin: 10px auto; text-align: center;')
        HTML.enable(f'page_portal_{glb.mainPage}', False)

        return None

    for tree in data:
        if tree in glb.knownTree:
            f.addEvent(f'SubPage_nav_main_{tree}', pageSub)
            f.addEvent(f'SubPage_nav_main_{tree}', getData, f'mousedown')

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

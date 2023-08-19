from js import document, console
from WebKit import CSS 
from json import load
from os import path as osPath


class glb:
    onHoverStyles = CSS.glb.onHoverStyles
    onClickStyles = CSS.glb.onClickStyles
    onFocusStyles = CSS.glb.onFocusStyles
    disabledStyles = {}

    with open(f'{osPath.split(__file__)[0]}/styleMap.json', "r", encoding="UTF-8") as fileR:
        styleMap = load(fileR)["HTML"]

    def expandStyle(style):
        if style is None or not style.split(" %% ")[0] in glb.styleMap:
            return style

        subStyleMerged = ""
        styleTmp = style.split(" %% ")

        for styleKey in styleTmp:
            if not styleKey in glb.styleMap:
                continue

            for subStyle in glb.styleMap[styleKey].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in style:
                    continue
                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            style = style.replace(styleKey, "")

        return f'{subStyleMerged}{style.split(" %% ")[-1]}'

    def constructHTML(tag: str, nest: str = "", prepend: str = "", id: str = "", classes: str = "", type: str = "", src: str = "", alt: str = "", align: str = "", style: str = "", custom: str = ""):
        args = {"id": id, "class": classes, "type": type, "src": src, "alt": alt, "align": align, "style": glb.expandStyle(style)}
        additionsStr = ""
        for arg in args:
            if args[arg] == "":
                continue

            additionsStr += f' {arg}="{args[arg]}"'

        additionsStr += f' {custom}'

        nest = nest.replace("\n", "<br>")
        htmlStr = f'{prepend}<{tag}{additionsStr}>{nest}'
        if not tag in ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]:
            htmlStr += f'</{tag}>'

        return htmlStr


def getElement(id: str):
    return document.getElementById(id)


def getElements(classId: str):
    return list(document.getElementsByClassName(classId))


def genElement(tag: str, nest: str = "", prepend: str = "", id: str = "", classes: str = "", type: str = "", src: str = "", alt: str = "", align: str = "", style: str = "", custom: str = ""):
    return glb.constructHTML(tag, nest, prepend, id, classes, type, src, alt, align, style, custom)


def setElement(tag: str, targetId: str, nest: str = "", prepend: str = "", id: str = "", classes: str = "", type: str = "", src: str = "", alt: str = "", align: str = "", style: str = "", custom: str = ""):
    document.getElementById(targetId).innerHTML = glb.constructHTML(tag, nest, prepend, id, classes, type, src, alt, align, style, custom)


def setElementRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML = HTML


def addElement(tag: str, targetId: str, nest: str = "", prepend: str = "", id: str = "", classes: str = "", type: str = "", src: str = "", alt: str = "", align: str = "", style: str = "", custom: str = ""):
    document.getElementById(targetId).innerHTML += glb.constructHTML(tag, nest, prepend, id, classes, type, src, alt, align, style, custom)


def addElementRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML += HTML


def copyElement(sourceId: str, targetId: str):
    el = document.getElementById(sourceId).cloneNode(True)
    el.id = f'{el.id}_Copy'
    document.getElementById(targetId).appendChild(el)


def copyElements(pairs: tuple):
    for sourceId, targetId in enumerate(pairs):
        el = document.getElementById(sourceId).cloneNode(True)
        el.id = f'{el.id}_Copy'
        document.getElementById(targetId).appendChild(el)


def moveElement(sourceId: str, targetId: str):
    document.getElementById(targetId).appendChild(document.getElementById(sourceId))


def moveElements(pairs: tuple):
    for sourceId, targetId in enumerate(pairs):
        document.getElementById(targetId).appendChild(document.getElementById(sourceId))


def remElement(id: str):
    document.getElementById(id).remove()


def remElements(classId: str):
    for item in document.getElementsByClassName(classId):
        item.remove()


def clrElement(id: str):
    document.getElementById(id).innerHTML = ""


def clrElements(classId: str):
    for item in document.getElementsByClassName(classId):
        item.innerHTML = ""


def linkWrap(href: str, nest: str = "", prepend: str = "", id: str = "", classes: str = "", align: str = "", style: str = "", custom: str = ""):
    return glb.constructHTML("a", nest, prepend, id, classes, "", "", "", align, f'{style} color: #44F;', f'{custom} href="{href}" target="_blank"')


def disableElement(id: str):
    el = document.getElementById(id)
    if el.disabled is True:
        return None

    onStyles = {"onHover": {"style": glb.onHoverStyles, "actions": ["mouseover", "mouseout"]}, "onClick": {"style": glb.onClickStyles, "actions": ["mousedown", "mouseup"]}, "onFocus": {"style": glb.onFocusStyles, "actions": ["focusout", "focusin"]}}
    el.disabled = True

    glb.disabledStyles[id] = {"color": el.style.color, "background": el.style.background, "events": {}}

    for onStyle in onStyles:
        for action in onStyles[onStyle]["actions"]:
            if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                continue

            glb.disabledStyles[id]["events"][f'{id}_{action}'] = {}
            itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])
            for i, item in enumerate(itemListTmp):
                if item.startswith("color: "):
                    glb.disabledStyles[id]["events"][f'{id}_{action}']["color"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = "color: #88B"

                elif item.startswith("background: "):
                    glb.disabledStyles[id]["events"][f'{id}_{action}']["background"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = "background: #222"

    el.style.color = "#88B"
    el.style.background = "#222"


def enableElement(id: str):
    el = document.getElementById(id)
    if el.disabled is False:
        return None

    onStyles = {"onHover": {"style": glb.onHoverStyles, "actions": ["mouseover", "mouseout"]}, "onClick": {"style": glb.onClickStyles, "actions": ["mousedown", "mouseup"]}, "onFocus": {"style": glb.onFocusStyles, "actions": ["focusout", "focusin"]}}
    el.disabled = False

    if not id in glb.disabledStyles:
        return None

    for onStyle in onStyles:
        for action in onStyles[onStyle]["actions"]:
            if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                continue
            if not f'{id}_{action}' in glb.disabledStyles[id]["events"]:
                continue

            itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])
            for i, item in enumerate(itemListTmp):
                if item.startswith("color: ") and "color" in glb.disabledStyles[id]["events"][f'{id}_{action}']:
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = glb.disabledStyles[id]["events"][f'{id}_{action}']["color"]

                elif item.startswith("background: ") and "background" in glb.disabledStyles[id]["events"][f'{id}_{action}']:
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = glb.disabledStyles[id]["events"][f'{id}_{action}']["background"]

    el.style.color = glb.disabledStyles[id]["color"]
    el.style.background = glb.disabledStyles[id]["background"]
    glb.disabledStyles.pop(id)

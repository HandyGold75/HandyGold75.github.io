from js import document
from pyodide.ffi import create_proxy # type: ignore


class glb:
    onHoverStyles = {}
    onClickStyles = {}
    onFocusStyles = {}
    styleMap = {
        "buttonHover": "z-index: 101; color: #FFF; background: #444; transition: 0.25s",
        "buttonClick": "z-index: 102; color: #55F; background: #BBF; transition: 0.1s",
        "inputHover": "z-index: 111; color: #FFF; background: #444; transition: 0.25s",
        "inputFocus": "z-index: 112; color: #FFF; background: #444; transition: 0.1s",
        "selectHover": "z-index: 121; margin-bottom: -80px; height: 108px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.25s",
        "selectFocus": "z-index: 122; margin-bottom: -80px; height: 108px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.1s",
        "imgHover": "z-index: 101; color: #FFF; background: #444; border: 3px solid #FBDF56; transition: 0.25s",
        "imgClick": "z-index: 102; color: #55F; background: #550; border: 3px solid #FBDF56; transition: 0.1s",
        "disabled": f'color: #88B; background: #222'
    }


def get(id: str, key: str):
    return getattr(document.getElementById(id), key)


def set(id: str, key: str, value: str):
    try:
        getattr(document.getElementById(id), key)
    except AttributeError:
        return None

    setattr(document.getElementById(id), key, value)


def getStyle(id: str, key: str):
    return getattr(document.getElementById(id).style, key)


def setStyle(id: str, key: str, value: str):
    try:
        getattr(document.getElementById(id).style, key)
    except AttributeError:
        return None

    setattr(document.getElementById(id).style, key, value)


def onHover(id: str, style: str):
    def mouseover(args=None):
        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        for prop in glb.onHoverStyles[f'{id}_mouseover']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    def mouseout(args=None):

        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        if document.getElementById(id).tagName != f'BUTTON' and document.activeElement == args.target:
            return None

        for prop in glb.onHoverStyles[f'{id}_mouseout']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    glb.onHoverStyles[f'{id}_mouseover'] = []
    glb.onHoverStyles[f'{id}_mouseout'] = []

    if style.split(" %% ")[0] in glb.styleMap:
        subStyleMerged = ""
        styleTmp = style.split(f' %% ')

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

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(f';')[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        if styleKey == f'transition':
            el.style.transition = f'{prop.split(": ")[1]}'
            continue

        glb.onHoverStyles[f'{id}_mouseout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        glb.onHoverStyles[f'{id}_mouseover'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener(f'mouseover', create_proxy(mouseover))
    el.addEventListener(f'mouseout', create_proxy(mouseout))


def onClick(id: str, style: str):
    def mousedown(args=None):
        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        for prop in glb.onClickStyles[f'{id}_mousedown']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    def mouseup(args=None):
        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        for prop in glb.onClickStyles[f'{id}_mouseup']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    glb.onClickStyles[f'{id}_mousedown'] = []
    glb.onClickStyles[f'{id}_mouseup'] = []

    if style.split(" %% ")[0] in glb.styleMap:
        subStyleMerged = ""
        styleTmp = style.split(f' %% ')

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

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(f';')[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        if styleKey == f'transition':
            el.style.transition = f'{prop.split(": ")[1]}'
            continue

        glb.onClickStyles[f'{id}_mouseup'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        glb.onClickStyles[f'{id}_mousedown'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener(f'mousedown', create_proxy(mousedown))
    el.addEventListener(f'mouseup', create_proxy(mouseup))


def onFocus(id: str, style: str):
    def focusin(args=None):
        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        for prop in glb.onFocusStyles[f'{id}_focusin']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    def focusout(args=None):
        id = args.target.id

        if id == "":
            id = args.target.parentElement.id

        for prop in glb.onFocusStyles[f'{id}_focusout']:
            setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    glb.onFocusStyles[f'{id}_focusin'] = []
    glb.onFocusStyles[f'{id}_focusout'] = []

    if style.split(" %% ")[0] in glb.styleMap:
        subStyleMerged = ""
        styleTmp = style.split(f' %% ')

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

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(f';')[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        if styleKey == f'transition':
            el.style.transition = f'{prop.split(": ")[1]}'
            continue

        glb.onFocusStyles[f'{id}_focusout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        glb.onFocusStyles[f'{id}_focusin'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener(f'focusin', create_proxy(focusin))
    el.addEventListener(f'focusout', create_proxy(focusout))

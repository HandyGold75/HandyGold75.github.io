import mod.functions as f
from js import document
from pyodide.ffi import create_proxy


class glb:
    onHoverStyles = {}
    styleMap = {"buttonHover": "z-index: 102; color: #FFF; background: #444; transition: 0.25s"}


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
        for prop in glb.onHoverStyles[f'{args.target.id}_mouseover']:
            setattr(document.getElementById(args.target.id).style, prop.split(": ")[0], prop.split(": ")[1])

    def mouseout(args=None):
        for prop in glb.onHoverStyles[f'{args.target.id}_mouseout']:
            setattr(document.getElementById(args.target.id).style, prop.split(": ")[0], prop.split(": ")[1])

    glb.onHoverStyles[f'{id}_mouseover'] = []
    glb.onHoverStyles[f'{id}_mouseout'] = []

    el = document.getElementById(id)

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

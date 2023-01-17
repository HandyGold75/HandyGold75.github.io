import mod.HTML as HTML
from js import document


class glb:
    noClosingHTML = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]
    styleMap = {
        "headerBig": f'margin: 10px auto; text-align: center; font-size: 200%; font-weight: bold; color: #55F; user-select: none',
        "headerMedium": f'margin: 10px auto; text-align: center; font-size: 150%; font-weight: bold; color: #55F; user-select: none',
        "headerSmall": f'margin: 10px auto; text-align: center; font-size: 100%; font-weight: bold; color: #55F; user-select: none',
        "buttonBig": f'z-index: 100; padding: 1px 4px; margin: 4px; text-align: center; font-size: 125%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonMedium": f'z-index: 100; padding: 1px 4px; margin: 4px; text-align: center; font-size: 100%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonSmall": f'z-index: 100; padding: 1px 4px; margin: 4px; text-align: center; font-size: 75%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "flex": f'display: flex',
        "pageLinks_Base": f'width: 95%; color: #55F; margin-bottom: 0px; transition: opacity 0.25s, border-bottom 0.1s; border-radius: 6px; border-right: 4px solid #111; border-left: 4px solid #111; user-select:none'
    }


def get(id: str, isClass: bool = False):
    if isClass:
        return list(document.getElementsByClassName(id))

    return document.getElementById(id)


def getLink(href: str, _nest: str = None):
    htmlStr = f'<a href="{href}" target="_blank" style="color: #44F;">'

    if not _nest is None:
        htmlStr += f'{_nest}'

    htmlStr += f'</a>'

    return f'{htmlStr}'


def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
    if not _style is None and _style.split(" %% ")[0] in glb.styleMap:
        subStyleMerged = ""
        _styleTmp = _style.split(" %% ")

        for style in _styleTmp:
            if not style in glb.styleMap:
                continue

            for subStyle in glb.styleMap[style].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in _style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            _style = _style.replace(style, "")

        _style = f'{subStyleMerged}{_style.split(" %% ")[-1]}'

    args = {"id": _id, "class": _class, "type": _type, "align": _align, "style": _style}
    additionsStr = ""

    for arg in args:
        if args[arg] is None:
            continue

        additionsStr += f' {arg}="{args[arg]}"'

    if not _custom is None:
        additionsStr += f' {_custom}'

    htmlStr = f'<{type}{additionsStr}>'

    if not _nest is None:
        htmlStr += _nest

    if not type in glb.noClosingHTML:
        htmlStr += f'</{type}>'

    if not _prepend is None:
        htmlStr = f'{_prepend}{htmlStr}'

    if not id is None:
        document.getElementById(f'{id}').innerHTML += f'{htmlStr}'

    return f'{htmlStr}'


def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
    htmlStr = add(type, None, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

    if not id is None:
        document.getElementById(f'{id}').innerHTML = htmlStr

    return htmlStr


def addRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML += HTML

def enable(id: str, state: bool = True):
    document.getElementById(id).disabled = not state


def clear(id: str):
    document.getElementById(id).innerHTML = f''


def remove(id: str):
    document.getElementById(id).remove()

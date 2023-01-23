from js import document


class glb:
    noClosingHTML = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]
    styleMap = {
        "headerVeryBig": f'margin: 10px auto; text-align: center; font-size: 175%; font-weight: bold; color: #55F; user-select: none',
        "headerBig": f'margin: 10px auto; text-align: center; font-size: 150%; font-weight: bold; color: #55F; user-select: none',
        "headerMedium": f'margin: 10px auto; text-align: center; font-size: 125%; font-weight: bold; color: #55F; user-select: none',
        "headerSmall": f'margin: 10px auto; text-align: center; font-size: 100%; font-weight: bold; color: #55F; user-select: none',
        "headerVerySmall": f'margin: 10px auto; text-align: center; font-size: 75%; font-weight: bold; color: #55F; user-select: none',
        "buttonBig": f'z-index: 100; padding: 1px 8px 3px 8px; margin: 3px; text-align: center; font-size: 125%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonMedium": f'z-index: 100; padding: 1px 6px 3px 6px; margin: 3px; text-align: center; font-size: 100%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonSmall": f'z-index: 100; padding: 1px 4px 3px 4px; margin: 3px; text-align: center; font-size: 70%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonImg": f'z-index: 100; padding: 4px; color: #55F; background: #222; border: 2px solid #222; border-radius: 8px',
        "inputMedium": f'z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none',
        "inputSmall": f'z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none',
        "selectMedium": f'z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none',
        "selectSmall": f'z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none',
        "divNormal": f'background: #222; padding: 5px; margin: 15px auto; border-radius: 10px',
        "divAlt": f'background: #55F; color: #111; padding: 5px; margin: 15px auto; border-radius: 10px',
        "disabled": f'color: #88B; background: #222',
        "flex": f'display: flex',
        "pageLinks_Base": f'width: 95%; color: #55F; margin-bottom: 0px; transition: opacity 0.25s, border-bottom 0.1s; border-radius: 6px; border-right: 4px solid #111; border-left: 4px solid #111'
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
        _styleTmp = _style.split(f' %% ')

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


def setRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML = HTML


def enable(id: str, state: bool = True):
    document.getElementById(id).disabled = not state


def clear(id: str):
    document.getElementById(id).innerHTML = f''


def remove(id: str):
    document.getElementById(id).remove()

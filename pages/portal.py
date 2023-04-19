from WebKit import HTML, CSS, JS, WS
import subs.portal_sonos as so
import subs.portal_tapo as tp
import subs.portal_ytdl as ytdl
import subs.portal_sheets as ps
import subs.portal_trees as pt


class glb:
    allSubs = {"Admin": ps.main, "Monitor": pt.main, "Sonos": so.main, "Tapo": tp.main, "YT-DL": ytdl.main, "Asset Manager": ps.main, "License Manager": ps.main, "Query": ps.main}
    allInvokes = {"Admin": ps.invoke.AP, "Monitor": pt.invoke.MO, "Sonos": so.invoke.SO, "Tapo": tp.invoke.TP, "YT-DL": ytdl.invoke.YTDL, "Asset Manager": ps.invoke.AM, "License Manager": ps.invoke.LM, "Query": ps.invoke.QR}
    allCommands = {"Admin": "admin", "Monitor": "monitor", "Sonos": "sonos", "Tapo": "tapo", "YT-DL": "yt", "Asset Manager": "am", "License Manager": "lm", "Query": "qr"}

    lastLogin = 0


def pagePortal(args=None, page=None):
    HTML.clear(f'page_portal_body')

    if page in glb.allSubs:
        JS.cache("page_portal", page)
        JS.cache("page_portalSub", f'')

    elif not args is None:
        id = args.target.id
        if id == "":
            id = args.target.parentElement.id

        if id.split("_")[-1] in glb.allSubs:
            JS.cache("page_portal", id.split("_")[-1])
            JS.cache("page_portalSub", f'')

    elif JS.cache("page_portal") != "":
        pass

    else:
        return None

    JS.setTitle(f'HandyGold75 - {JS.cache("page_index")} - {JS.cache("page_portal")}')

    HTML.set(f'div', f'page_portal_body', _id=f'SubPage', _align=f'left')
    HTML.setRaw(f'nav_title', f'HandyGold75 - {JS.cache("page_index")} - {JS.cache("page_portal")}')

    if JS.cache("page_portalSub") != "":
        glb.allSubs[JS.cache("page_portal")](sub=JS.cache("page_portalSub"))
    else:
        glb.allSubs[JS.cache("page_portal")]()

    JS.onResize()


def main():
    HTML.set(f'div', f'page', _id=f'page_portal', _align=f'center', _style="flex")

    if not WS.loggedIn:
        HTML.add(f'h1', f'page_portal', _nest=f'Please log in first!', _style=f'headerBig')
        return None

    allSubsTmp = dict(glb.allSubs)
    for page in allSubsTmp:
        if not glb.allCommands[page] in WS.dict()[f'access']:
            glb.allSubs.pop(page)
            glb.allInvokes.pop(page)

    if glb.allSubs == {}:
        HTML.add(f'h1', f'page_portal', _nest=f'You don\'t have access to any portals!<br>Please request access if you think this is a mistake.', _style=f'headerBig')
        return None

    HTML.add(f'div', f'page_portal', _id=f'page_portal_buttons', _align=f'left', _style="width: 5%; min-width: 50px; font-size: 75%; border-right: 10px solid #111; margin-right: 10px;")
    HTML.add(f'div', f'page_portal', _id=f'page_portal_body', _align=f'left', _style="width: 95%;")

    for page in glb.allSubs:
        img = HTML.add(f'img', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/{page}.png" alt="{page.split(" ")[0]}"')
        btn = HTML.add(f'button', _id=f'page_portal_{page}', _nest=f'{img}', _style=f'buttonImg')
        HTML.add(f'div', f'page_portal_buttons', _nest=f'{btn}', _align=f'center', _style=f'margin: 10px 5px 10px auto;')

    for page in glb.allSubs:
        JS.addEvent(f'page_portal_{page}', pagePortal)
        JS.addEvent(f'page_portal_{page}', glb.allInvokes[page], f'mousedown')
        CSS.onHoverClick(f'page_portal_{page}', f'imgHover', f'imgClick')

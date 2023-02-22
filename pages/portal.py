import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.functions as f
import subs.portal_sonos as so
import subs.portal_sheets as ps
import subs.portal_trees as pt


class glb:
    allSubs = {"Admin": ps.main, "Monitor": pt.main, "Sonos": so.main, "Asset Manager": ps.main, "License Manager": ps.main, "Query": ps.main}
    allInvokes = {"Admin": ps.invoke.AP, "Monitor": pt.invoke.MO, "Sonos": so.invoke.SO, "Asset Manager": ps.invoke.AM, "License Manager": ps.invoke.LM, "Query": ps.invoke.QR}
    allCommands = {"Admin": "admin", "Monitor": "monitor", "Sonos": "sonos", "Asset Manager": "am", "License Manager": "lm", "Query": "qr"}

    lastLogin = 0


def pagePortal(args=None, page=None):
    HTML.clear(f'page_portal_body')

    id = args.target.id

    if id == "":
        id = args.target.parentElement.id

    if page in glb.allSubs:
        f.cache("page_portal", page)

    elif not args is None and id.split("_")[-1] in glb.allSubs:
        f.cache("page_portal", id.split("_")[-1])

    else:
        return None

    f.setTitle(f'HandyGold75 - {f.cache("page_index")} - {f.cache("page_portal")}')

    HTML.set(f'div', f'page_portal_body', _id=f'SubPage', _align=f'left')
    HTML.setRaw(f'nav_title', f'HandyGold75 - {f.cache("page_index")} - {f.cache("page_portal")}')

    glb.allSubs[f.cache("page_portal")]()


def main():
    HTML.set(f'div', f'page', _id=f'page_portal', _align=f'center', _style="flex")

    if not f.glb.loggedIn:
        HTML.add(f'h1', f'page_portal', _nest=f'Please log in first!', _style=f'headerBig')
        return None

    allSubsTmp = dict(glb.allSubs)
    for page in allSubsTmp:
        if not glb.allCommands[page] in ws.msgDict()[f'access']:
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
        f.addEvent(f'page_portal_{page}', pagePortal)
        f.addEvent(f'page_portal_{page}', glb.allInvokes[page], f'mousedown')

        CSS.onHover(f'page_portal_{page}', f'imgHover')
        CSS.onClick(f'page_portal_{page}', f'imgClick')

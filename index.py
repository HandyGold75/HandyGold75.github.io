from WebKit import HTML, JS, CSS
import pages.home as home
import pages.links as links
import pages.portal as portal
import pages.contact as contact
import pages.login as login


class glb:
    allPages = {"Home": home.main, "Links": links.main, "Portal": portal.main, "Contact": contact.main, "Login": login.main}
    exludeMainNav = ["Login"]


def setup():
    for item in ["token", "signin", "server", "page_index", "page_links", "page_portal", "page_portalSub"]:
        if JS.cache(item) is None:
            JS.cache(item, f'')

    if JS.cache(f'page_index') == "":
        JS.cache(f'page_index', f'Home')
        
    if JS.cache("server") == "":
        JS.cache("server", "WSS://wss.HandyGold75.com:6900")

    if JS.cache(f'signin') == "Auto":
        JS.cache(f'page_index', f'Login')

    elif JS.cache(f'signin') in ["", "None"]:
        JS.cache(f'token', f'')


def mainPage():
    def addEvents():
        for page in glb.allPages:
            if page in glb.exludeMainNav:
                continue
            JS.addEvent(f'page_{page}', pageIndex)
            CSS.onHoverClick(f'page_{page}', f'buttonHover', f'buttonClick')

        JS.addEvent(f'footer_toTop', lambda args=None: CSS.get(f'body', f'scrollIntoView')())
        CSS.onHoverClick(f'footer_toTop', f'buttonHover %% background: #66F;', f'buttonClick %% background: #66F;')

        JS.addEvent(f'footer_ClearCache', lambda args=None: JS.clearCache())
        CSS.onHoverClick(f'footer_ClearCache', f'buttonHover %% background: #66F;', f'buttonClick %% background: #66F;')

        JS.addEvent(f'footer_Login', login.main)
        CSS.onHoverClick(f'footer_Login', f'buttonHover %% background: #66F;', f'buttonClick %% background: #66F;')

        JS.addEvent(JS.getWindow(), JS.onResize, f'resize', isClass=True)

    JS.setTitle(f'HandyGold75 - {JS.cache("page_index")}')

    buttons = ""
    for page in glb.allPages:
        if page in glb.exludeMainNav:
            continue
        buttons += HTML.add(f'button', _nest=f'{page}', _id=f'page_{page}', _type=f'button', _style=f'buttonBig')

    nav = HTML.add(f'img', _id=f'nav_logo', _align=f'left', _style=f'width: 20%; max-width: 100px; user-select: none;', _custom=f'src="docs/assets/;D.png"')
    nav += HTML.add(f'h1', _nest=f'HandyGold75 - {JS.cache("page_index")}', _id=f'nav_title', _align=f'center', _style=f'headerBig %% width: 80%;')
    nav += HTML.add(f'div', _nest=buttons, _id=f'nav_buttons', _align=f'center', _style=f'width: 80%; padding: 4px; margin: 0px auto;')

    txt = HTML.add(f'p', _nest=f'HandyGold75 - 2022 / 2023', _style=f'headerVerySmall %% color: #111; text-align: left; padding: 3px; margin: 0px auto;')
    footer = HTML.set(f'div', _nest=txt, _id=f'footer_note', _style=f'width: 50%; padding: 5px; margin: 0px auto;')

    butToTop = HTML.add(f'button', _nest=f'Back to top', _id=f'footer_toTop', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butClearCache = HTML.add(f'button', _nest=f'Clear cache', _id=f'footer_ClearCache', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butLogin = HTML.add(f'button', _nest=f'Login', _id=f'footer_Login', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    footer += HTML.add(f'div', _nest=butLogin + butClearCache + butToTop, _id=f'footer_buttons', _align=f'right', _style=f'width: 50%; padding: 3px; margin: 0px auto;')

    main = HTML.add(f'div', _nest=nav, _id=f'nav', _style=f'divNormal')
    main += HTML.add(f'div', _id=f'page', _style=f'divNormal')
    main += HTML.add(f'div', _nest=footer, _id=f'footer', _style=f'divAlt %% flex')

    HTML.setRaw(f'body', main)
    JS.afterDelay(addEvents, 100)


def pageIndex(args=None, page=None):
    HTML.clear(f'page')

    if page in glb.allPages:
        JS.cache(f'page_index', page)

    elif args.target.id.split(f'_')[-1] in glb.allPages:
        JS.cache("page_index", args.target.id.split(f'_')[-1])
        JS.cache("page_portal", f'')
        JS.cache("page_portalSub", f'')

    elif args.target.parentElement.id.split(f'_')[-1] in glb.allPages:
        JS.cache("page_index", args.target.parentElement.id.split(f'_')[-1])
        JS.cache("page_portal", f'')
        JS.cache("page_portalSub", f'')

    else:
        return None

    JS.setTitle(f'HandyGold75 - {JS.cache("page_index")}')
    HTML.setRaw(f'nav_title', f'HandyGold75 - {JS.cache("page_index")}')

    glb.allPages[JS.cache(f'page_index')]()

    if args != "noResize":
        JS.onResize()


def main():
    setup()
    mainPage()
    pageIndex(page=JS.cache(f'page_index'))


if __name__ == "__main__":
    main()

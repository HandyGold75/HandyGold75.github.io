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
        JS.cache("server", "WSS://wss.HandyGold75.com:17500")

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
        buttons += HTML.genElement(f'button', nest=f'{page}', id=f'page_{page}', type=f'button', style=f'buttonBig')

    nav = HTML.genElement(f'img', id=f'nav_logo', align=f'left', style=f'width: 20%; max-width: 100px; user-select: none;', custom=f'src="docs/assets/;D.png"')
    nav += HTML.genElement(f'h1', nest=f'HandyGold75 - {JS.cache("page_index")}', id=f'nav_title', align=f'center', style=f'headerBig %% width: 80%;')
    nav += HTML.genElement(f'div', nest=buttons, id=f'nav_buttons', align=f'center', style=f'width: 80%; padding: 4px; margin: 0px auto;')

    txt = HTML.genElement(f'p', nest=f'HandyGold75 - 2022 / 2023', style=f'headerVerySmall %% color: #111; text-align: left; padding: 3px; margin: 0px auto;')
    footer = HTML.genElement(f'div', nest=txt, id=f'footer_note', style=f'width: 50%; padding: 5px; margin: 0px auto;')

    butToTop = HTML.genElement(f'button', nest=f'Back to top', id=f'footer_toTop', type=f'button', style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butClearCache = HTML.genElement(f'button', nest=f'Clear cache', id=f'footer_ClearCache', type=f'button', style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butLogin = HTML.genElement(f'button', nest=f'Login', id=f'footer_Login', type=f'button', style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    footer += HTML.genElement(f'div', nest=butLogin + butClearCache + butToTop, id=f'footer_buttons', align=f'right', style=f'width: 50%; padding: 3px; margin: 0px auto;')

    main = HTML.genElement(f'div', nest=nav, id=f'nav', style=f'divNormal')
    main += HTML.genElement(f'div', id=f'page', style=f'divNormal')
    main += HTML.genElement(f'div', nest=footer, id=f'footer', style=f'divAlt %% flex')

    HTML.setElementRaw(f'body', main)
    JS.afterDelay(addEvents, 100)


def pageIndex(args=None, page=None):
    HTML.clrElement(f'page')

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
    HTML.setElementRaw(f'nav_title', f'HandyGold75 - {JS.cache("page_index")}')

    glb.allPages[JS.cache(f'page_index')]()

    if args != "noResize":
        JS.onResize()


def main():
    setup()
    mainPage()
    pageIndex(page=JS.cache(f'page_index'))


if __name__ == "__main__":
    main()

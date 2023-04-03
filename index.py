import mod.HTML as HTML
import mod.CSS as CSS
import mod.JS as JS
import pages.home as home
import pages.links as links
import pages.portal as portal
import pages.contact as contact
import pages.login as login


class glb:
    allPages = {"Home": home.main, "Links": links.main, "Portal": portal.main, "Contact": contact.main, "Login": login.main}
    exludeMainNav = ["Login"]


def setup():
    for item in ["token", "signin", "page_index", "page_links", "page_portal"]:
        if JS.cache(item) is None:
            JS.cache(item, f'')

    if JS.cache(f'page_index') == "":
        JS.cache(f'page_index', f'Home')

    if JS.cache(f'signin') == "Auto":
        JS.cache(f'page_index', f'Login')

    elif JS.cache(f'signin') in ["", "None"]:
        JS.cache(f'token', f'')


def general():
    JS.setTitle(f'HandyGold75 - {JS.cache("page_index")}')

    HTML.set(f'div', f'body', _id=f'nav', _style=f'divNormal')
    HTML.add(f'div', f'body', _id=f'page', _style=f'divNormal')
    HTML.add(f'div', f'body', _id=f'footer', _style=f'divAlt %% flex')

    JS.addEvent(JS.getWindow(), JS.onResize, f'resize', isClass=True)


def navigation():
    HTML.add(f'img', f'nav', _id=f'nav_logo', _align=f'left', _style=f'width: 20%; max-width: 100px; user-select: none;', _custom=f'src="docs/assets/;D.png"')
    HTML.add(f'h1', f'nav', _nest=f'HandyGold75 - {JS.cache("page_index")}', _id=f'nav_title', _align=f'center', _style=f'headerBig %% width: 80%;')
    HTML.add(f'div', f'nav', _id=f'nav_buttons', _align=f'center', _style=f'width: 80%; padding: 4px; margin: 0px auto;')

    for page in glb.allPages:
        if page in glb.exludeMainNav:
            continue

        HTML.add(f'button', f'nav_buttons', _nest=f'{page}', _id=f'page_{page}', _type=f'button', _style=f'buttonBig')

    for page in glb.allPages:
        if page in glb.exludeMainNav:
            continue

        JS.addEvent(f'page_{page}', pageIndex)
        CSS.onHover(f'page_{page}', f'buttonHover')
        CSS.onClick(f'page_{page}', f'buttonClick')


def pageIndex(args=None, page=None):
    HTML.clear(f'page')

    if page in glb.allPages:
        JS.cache(f'page_index', page)

    elif args.target.id.split(f'_')[-1] in glb.allPages:
        JS.cache(f'page_index', args.target.id.split(f'_')[-1])
        JS.cache(f'page_portal', f'')

    elif args.target.parentElement.id.split(f'_')[-1] in glb.allPages:
        JS.cache(f'page_index', args.target.parentElement.id.split(f'_')[-1])
        JS.cache(f'page_portal', f'')

    else:
        return None

    JS.setTitle(f'HandyGold75 - {JS.cache("page_index")}')

    HTML.setRaw(f'nav_title', f'HandyGold75 - {JS.cache("page_index")}')

    glb.allPages[JS.cache(f'page_index')]()

    if args != "noResize":
        JS.onResize()


def footer():
    def toTop(args=None):
        CSS.get(f'body', f'scrollIntoView')()

    def clearCache(args=None):
        JS.clearCache()

    txt = HTML.add(f'p', _nest=f'HandyGold75 - 2022 / 2023', _style=f'headerVerySmall %% color: #111; text-align: left; padding: 3px; margin: 0px auto;')
    HTML.set(f'div', f'footer', _nest=txt, _id=f'footer_note', _style=f'width: 50%; padding: 5px; margin: 0px auto;')

    butToTop = HTML.add(f'button', _nest=f'Back to top', _id=f'footer_toTop', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butClearCache = HTML.add(f'button', _nest=f'Clear cache', _id=f'footer_ClearCache', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    butLogin = HTML.add(f'button', _nest=f'Login', _id=f'footer_Login', _type=f'button', _style=f'buttonSmall %% border: 2px solid #222; background: #44F;')
    HTML.add(f'div', f'footer', _nest=butLogin + butClearCache + butToTop, _id=f'footer_buttons', _align=f'right', _style=f'width: 50%; padding: 3px; margin: 0px auto;')

    JS.addEvent(f'footer_toTop', toTop)
    CSS.onHover(f'footer_toTop', f'buttonHover %% background: #66F;')
    CSS.onClick(f'footer_toTop', f'buttonClick %% background: #66F;')

    JS.addEvent(f'footer_ClearCache', clearCache)
    CSS.onHover(f'footer_ClearCache', f'buttonHover %% background: #66F;')
    CSS.onClick(f'footer_ClearCache', f'buttonClick %% background: #66F;')

    JS.addEvent(f'footer_Login', login.main)
    CSS.onHover(f'footer_Login', f'buttonHover %% background: #66F;')
    CSS.onClick(f'footer_Login', f'buttonClick %% background: #66F;')


def main():
    setup()
    general()

    navigation()
    pageIndex(page=JS.cache(f'page_index'))
    footer()


if __name__ == "__main__":
    main()

import mod.HTML as HTML
import mod.CSS as CSS
import mod.functions as f
import pages.home as home
import pages.links as links
import pages.portal as portal
import pages.contact as contact


class glb:
    allPages = {"Home": home.main, "Links": links.main, "Portal": portal.main, "Contact": contact.main}


for item in ["token", "page_index", "page_portal"]:
    if f.cache(item) is None:
        f.cache(item, f'')

if f.cache(f'page_index') == "":
    f.cache(f'page_index', f'Home')


def general():
    f.setTitle(f'HandyGold75 - {f.cache("page_index")}')

    HTML.set(f'div', f'body', _id=f'main', _style=f'background: #111; max-width: 1080px; min-width: 375px; margin: 0px auto;')

    HTML.set(f'div', f'main', _id=f'nav', _style=f'background: #222; font-size: 150%; padding: 5px; margin: 15px auto; border-radius: 10px;')
    HTML.add(f'div', f'main', _id=f'page', _style=f'background: #222; padding: 5px; margin: 15px auto; border-radius: 10px;')
    HTML.add(f'div', f'main', _id=f'footer', _style=f'font-size: 75%; padding: 5px; margin: 15px auto; background: #55F; color: #111; display: flex; border-radius: 10px;')


def navigation():
    HTML.add(f'img', f'nav', _id=f'nav_logo', _align=f'left', _style=f'width: 12%; min-width: 78px; user-select: none;', _custom=f'src="docs/assets/;D.png"')
    HTML.add(f'h1', f'nav', _nest=f'HandyGold75 - {f.cache("page_index")}', _id=f'nav_title', _align=f'center', _style=f'font-size: 50%; width: 80%; padding: 5px; margin: 0px auto; user-select: none;')
    HTML.add(f'div', f'nav', _id=f'nav_buttons', _align=f'center', _style=f'width: 80%; padding: 4px; margin: 0px auto;')

    for page in glb.allPages:
        HTML.add(f'button', f'nav_buttons', _nest=f'{page}', _id=f'page_{page}', _type=f'button')

    for page in glb.allPages:
        f.addEvent(f'page_{page}', pageIndex)


def pageIndex(args=None, page=None):
    HTML.clear(f'page')

    if page in glb.allPages:
        f.cache(f'page_index', page)

    elif args.target.id.split(f'_')[-1] in glb.allPages:
        f.cache(f'page_index', args.target.id.split(f'_')[-1])
        f.cache(f'page_portal', f'')

    else:
        return None

    f.setTitle(f'HandyGold75 - {f.cache("page_index")}')

    HTML.set(f'h1', f'nav_title', _nest=f'HandyGold75 - {f.cache("page_index")}', _style=f'user-select: none;')

    glb.allPages[f.cache(f'page_index')]()


def footer():
    def toTop(*args):
        CSS.get(f'body', f'scrollIntoView')()

    txt = HTML.add(f'p', _nest=f'HandyGold75 - 2022', _style=f'padding: 3px; margin: 0px auto; user-select: none; font-weight: bold;')
    HTML.set(f'div', f'footer', _nest=txt, _id=f'footer_note', _style=f'width: 50%; padding: 4px; margin: 0px auto;')

    but = HTML.add(f'button', _nest=f'Back to top', _id=f'footer_toTop', _type=f'button')
    HTML.add(f'div', f'footer', _nest=but, _id=f'footer_buttons', _align=f'right', _style=f'width: 50%; padding: 3px; margin: 0px auto;')

    f.addEvent(f'footer_toTop', toTop)


def main():
    general()
    navigation()
    pageIndex(page=f.cache(f'page_index'))
    footer()


if __name__ == "__main__":
    main()

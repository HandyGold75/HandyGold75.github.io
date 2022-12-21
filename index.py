import mod.func as func
import pages.home as home
import pages.links as links
import pages.portal as portal
import pages.contact as contact
from js import document, window, console


class glb:
    allPages = {"Home": home.main, "Links": links.main, "Portal": portal.main, "Contact": contact.main}


for item in ["token", "page_index", "page_portal"]:
    if window.localStorage.getItem(item) is None:
        window.localStorage.setItem(item, "")


def general():
    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

    element = document.getElementById(f'body')
    element.innerHTML = f'<div id="main"></div>'

    element = document.getElementById(f'main')
    element.innerHTML = f'<div id="nav"></div><div id="page"></div><div id="footer"></div>'


def navigation():
    element = document.getElementById(f'nav')
    element.innerHTML += f'<img src="docs/assets/;D.png" id="nav_logo" align="left"><h1 id="nav_title" align="center">HandyGold75 - {window.localStorage.getItem("page_index")}</h1><div id="nav_buttons" align="center"></div>'

    element = document.getElementById(f'nav_buttons')

    for page in glb.allPages:
        element.innerHTML += f'<button id="page_{page}" type="button">{page}</button>'

    for page in glb.allPages:
        func.addEvent(f'page_{page}', pageIndex)


def pageIndex(args=None, page=None):
    element = document.getElementById(f'page')
    element.innerHTML = f''

    if page in glb.allPages:
        window.localStorage.setItem("page_index", page)

    elif args.target.id.split(f'_')[-1] in glb.allPages:
        window.localStorage.setItem("page_index", args.target.id.split(f'_')[-1])

    else:
        return None

    window.localStorage.setItem("page_portal", "")
    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

    element = document.getElementById(f'nav_title')
    element.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")}</h1>'

    glb.allPages[window.localStorage.getItem("page_index")]()


def footer():
    def toTop(*args):
        document.getElementById(f'body').scrollIntoView()

    element = document.getElementById(f'footer')
    element.innerHTML = (f'<div id="footer_note"><p><b>HandyGold75 - 2022</b></p></div><div id="footer_buttons" align="right"><button id="footer_toTop" type="button">Back to top</button></div></div>')

    func.addEvent(f'footer_toTop', toTop)


def main():
    general()
    navigation()
    pageIndex(page=window.localStorage.getItem("page_index"))
    footer()


if __name__ == "__main__":
    main()

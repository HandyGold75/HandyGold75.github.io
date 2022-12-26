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

if window.localStorage.getItem("page_index") == "":
    window.localStorage.setItem("page_index", "Home")


def general():
    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

    el = document.getElementById(f'body')
    el.innerHTML = f'<div id="main" style="background: #111; max-width: 1080px; min-width: 375px; margin: 0px auto;"></div>'

    el = document.getElementById(f'main')
    el.innerHTML = f''
    el.innerHTML += f'<div id="nav" style="background: #222; font-size: 150%; padding: 5px; margin: 15px auto; border-radius: 10px;"></div>'
    el.innerHTML += f'<div id="page" style="background: #222; padding: 5px; margin: 15px auto; border-radius: 10px;"></div>'
    el.innerHTML += f'<div id="footer" style="font-size: 75%; padding: 5px; margin: 15px auto; background: #55F; color: #111; display: flex; border-radius: 10px;"></div>'


def navigation():
    el = document.getElementById(f'nav')
    el.innerHTML += f'<img src="docs/assets/;D.png" id="nav_logo" align="left" style="width: 12%; min-width: 78px; position: relative;">'
    el.innerHTML += f'<h1 id="nav_title" align="center" style="font-size: 50%; width: 80%; padding: 5px; margin: 0px auto;">HandyGold75 - {window.localStorage.getItem("page_index")}</h1>'
    el.innerHTML += f'<div id="nav_buttons" align="center" style="width: 80%; padding: 4px; margin: 0px auto;"></div>'

    el = document.getElementById(f'nav_buttons')

    for page in glb.allPages:
        el.innerHTML += f'<button id="page_{page}" type="button">{page}</button>'

    for page in glb.allPages:
        func.addEvent(f'page_{page}', pageIndex)


def pageIndex(args=None, page=None):
    el = document.getElementById(f'page')
    el.innerHTML = f''

    if page in glb.allPages:
        window.localStorage.setItem("page_index", page)

    elif args.target.id.split(f'_')[-1] in glb.allPages:
        window.localStorage.setItem("page_index", args.target.id.split(f'_')[-1])
        window.localStorage.setItem("page_portal", "")

    else:
        return None

    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

    el = document.getElementById(f'nav_title')
    el.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")}</h1>'

    glb.allPages[window.localStorage.getItem("page_index")]()


def footer():
    def toTop(*args):
        document.getElementById(f'body').scrollIntoView()

    el = document.getElementById(f'footer')
    el.innerHTML = f''
    el.innerHTML += f'<div id="footer_note" style="width: 50%; padding: 4px; margin: 0px auto;"><p style="padding: 3px; margin: 0px auto;"><b>HandyGold75 - 2022</b></p></div>'
    el.innerHTML += f'<div id="footer_buttons" align="right" style="width: 50%; padding: 3px; margin: 0px auto;"><button id="footer_toTop" type="button">Back to top</button></div>'

    func.addEvent(f'footer_toTop', toTop)


def main():
    general()
    navigation()
    pageIndex(page=window.localStorage.getItem("page_index"))
    footer()


if __name__ == "__main__":
    main()

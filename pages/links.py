import mod.func as func
from json import dumps, loads, load
from js import document, window, console


class glb:
    allLinks = {}
    columns = 4


def setup():
    file_R = open(f'pages/links.json', "r", encoding="UTF-8")
    glb.allLinks = load(file_R)
    file_R.close()

    if window.localStorage.getItem("page_links") is None:
        window.localStorage.setItem("page_links", dumps({}))

    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_links" align="center"></div>'


def toggleCat(args: any):
    cats = loads(window.localStorage.getItem("page_links"))
    cats[args.target.id.split("_")[2]] = not cats[args.target.id.split("_")[2]]

    el1 = document.getElementById(f'page_links_{args.target.id.split("_")[2]}_row0')
    el1.style.borderBottom = "2px solid #111"
    el = document.getElementById(f'page_links_{args.target.id.split("_")[2]}')
    el.style.position = "unset"
    el.style.marginTop = "0px"
    el.style.opacity = "1"

    if not cats[args.target.id.split("_")[2]]:
        el1.style.borderBottom = "4px solid #111"
        el.style.position = "absolute"
        el.style.marginTop = "-9999px"
        el.style.opacity = "0"

    window.localStorage.setItem("page_links", dumps(cats))


def main():
    def newRow(cats: dict):
        cats[glb.allLinks[link]["cat"]] += 1

        el = document.getElementById(f'page_links_{glb.allLinks[link]["cat"]}')
        el.innerHTML += f'<div id="page_links_{glb.allLinks[link]["cat"]}_row{cats[glb.allLinks[link]["cat"]]}" align="center" style="display: flex;"></div>'

        return cats

    def newCat(cats: dict, visable: bool):
        tmpCats[glb.allLinks[link]["cat"]] = 0

        el = document.getElementById(f'page_links')
        baseStyle = f'width: 95%; color: #55F; margin-bottom: 0px; transition: opacity 0.25s, border-bottom 0.1s; border-radius: 6px; border-right: 4px solid #111; border-left: 4px solid #111; user-select:none;'

        if visable:
            el.innerHTML += f'<h2 id="page_links_{glb.allLinks[link]["cat"]}_row0" align="center" style="{baseStyle} border-top: 4px solid #111; border-bottom: 2px solid #111;">{glb.allLinks[link]["cat"]}</h2>'
            el.innerHTML += f'<div id="page_links_{glb.allLinks[link]["cat"]}" align="center" style="{baseStyle} border-bottom: 4px solid #111; opacity: 1;""></div>'
        else:
            el.innerHTML += f'<h2 id="page_links_{glb.allLinks[link]["cat"]}_row0" align="center" style="{baseStyle} border-top: 4px solid #111; border-bottom: 4px solid #111;">{glb.allLinks[link]["cat"]}</h2>'
            el.innerHTML += f'<div id="page_links_{glb.allLinks[link]["cat"]}" align="center" style="{baseStyle} border-bottom: 4px solid #111; opacity: 0; margin-top: -9999px; position: absolute;"></div>'

        return cats

    setup()

    cats = loads(window.localStorage.getItem("page_links"))
    tmpCats = {}

    for link in glb.allLinks:
        if not glb.allLinks[link]["cat"] in tmpCats:
            if not glb.allLinks[link]["cat"] in cats:
                cats[glb.allLinks[link]["cat"]] = True

            i = 0
            tmpCats = newCat(tmpCats, cats[glb.allLinks[link]["cat"]])

        if i % glb.columns == 0:
            tmpCats = newRow(tmpCats)

        i += 1

        el = document.getElementById(f'page_links_{glb.allLinks[link]["cat"]}_row{tmpCats[glb.allLinks[link]["cat"]]}')
        img = f'<a href="{glb.allLinks[link]["url"]}" target="_blank"><img id="Image_{glb.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.allLinks[link]["text"]}" style="user-select:none; width: 30%; margin: 15px auto -10px auto;"></a>'
        txt = f'<p><u><a href="{glb.allLinks[link]["url"]}" target="_blank" style="color: #44F; font-size: 75%;">{glb.allLinks[link]["text"]}</a></u></p>'
        el.innerHTML += f'<div style="width: {100 / glb.columns}%; margin: 0px auto;">{img}{txt}</div>'

    for cat in tmpCats:
        func.addEvent(f'page_links_{cat}_row0', toggleCat, "click")

    window.localStorage.setItem("page_links", dumps(cats))

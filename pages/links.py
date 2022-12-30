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
    el.innerHTML = f'<div id="page_links"></div>'


def toggleCat(args: any):
    cats = loads(window.localStorage.getItem("page_links"))
    cats[args.target.id.split("_")[2]] = not cats[args.target.id.split("_")[2]]

    el = document.getElementById(f'page_links_{args.target.id.split("_")[2]}')
    el.style.display = ""

    if not cats[args.target.id.split("_")[2]]:
        el.style.display = "none"

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
        el.innerHTML += f'<h2 id="page_links_{glb.allLinks[link]["cat"]}_row0" align="center" style="color: #55F;">{glb.allLinks[link]["cat"]}</h2>'

        if visable:
            el.innerHTML += f'<div id="page_links_{glb.allLinks[link]["cat"]}" align="center"></div>'
        else:
            el.innerHTML += f'<div id="page_links_{glb.allLinks[link]["cat"]}" align="center" style="display: none;"></div>'

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
        img = f'<a href="{glb.allLinks[link]["url"]}" target="_blank"><img id="Image_{glb.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.allLinks[link]["text"]}" style="width: 30%; margin: 15px auto -10px auto;"></a>'
        txt = f'<p><u><a href="{glb.allLinks[link]["url"]}" target="_blank" style="color: #44F;">{glb.allLinks[link]["text"]}</a></u></p>'
        el.innerHTML += f'<div style="width: {100 / glb.columns}%; margin: 0px auto;">{img}{txt}</div>'

    for cat in tmpCats:
        func.addEvent(f'page_links_{cat}_row0', toggleCat, "dblclick")

    window.localStorage.setItem("page_links", dumps(cats))

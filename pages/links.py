import mod.func as func
from json import dumps, loads, load
from js import document, window, console


class glb:
    links = {}
    columns = 4


def setup():
    file_R = open(f'pages/links.json', "r", encoding="UTF-8")
    glb.links = load(file_R)
    file_R.close()

    if window.localStorage.getItem("page_links") is None:
        window.localStorage.setItem("page_links", dumps({}))

    func.setHTML(f'div', f'page', _id=f'page_links', _align=f'center')


def toggleCat(args: any):
    catStates = loads(window.localStorage.getItem("page_links"))
    catStates[args.target.id.split("_")[2]] = not catStates[args.target.id.split("_")[2]]

    el1 = document.getElementById(f'page_links_{args.target.id.split("_")[2]}_header')
    el1.style.borderBottom = "2px solid #111"
    el = document.getElementById(f'page_links_{args.target.id.split("_")[2]}')
    el.style.position = "unset"
    el.style.marginTop = "0px"
    el.style.opacity = "1"

    if not catStates[args.target.id.split("_")[2]]:
        el1.style.borderBottom = "4px solid #111"
        el.style.position = "absolute"
        el.style.marginTop = "-9999px"
        el.style.opacity = "0"

    window.localStorage.setItem("page_links", dumps(catStates))


def main():
    def newCat(cat: dict, visable: bool):
        if visable:
            func.addHTML(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerMedium %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 2px solid #111;')
            func.addHTML(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 1;')
        else:
            func.addHTML(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerMedium %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 4px solid #111;')
            func.addHTML(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 0; margin-top: -9999px; position: absolute;')

    setup()

    catStates = loads(window.localStorage.getItem("page_links"))
    catObjLens = {}

    for link in glb.links:
        currentCat = glb.links[link]["cat"]

        if not currentCat in catObjLens:
            if not currentCat in catStates:
                catStates[currentCat] = True

            i = 0
            newCat(currentCat, catStates[currentCat])
            catObjLens[currentCat] = 0

        if i % glb.columns == 0:
            catObjLens[currentCat] += 1
            func.addHTML(f'div', f'page_links_{currentCat}', _id=f'page_links_{currentCat}_row{catObjLens[currentCat]}', _align=f'center', _style=f'flex')

        i += 1
        
        img = func.makeLink(glb.links[link]["url"], _nest=f'<img id="Image_{glb.links[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.links[link]["text"]}" style="user-select:none; width: 30%; margin: 15px auto -10px auto;">')
        txt = func.addHTML(f'p', _nest=func.makeLink(glb.links[link]["url"], _nest=glb.links[link]["text"]))
        func.addHTML(f'div', f'page_links_{currentCat}_row{catObjLens[currentCat]}', _nest=f'{img}{txt}', _style=f'width: {100 / glb.columns}%; margin: 0px auto;')

    for cat in catObjLens:
        func.addEvent(f'page_links_{cat}_header', toggleCat, "click")

    window.localStorage.setItem("page_links", dumps(catStates))

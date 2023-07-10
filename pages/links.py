from WebKit import HTML, CSS, JS, WS
from json import dumps, loads, load
from os import path as osPath


class glb:
    allLinks = {}

    with open(f'{osPath.split(__file__)[0]}/config.json', "r", encoding="UTF-8") as fileR:
        defaultLinks = load(fileR)["defaultLinks"]

    columns = 4


def setup():
    glb.allLinks = dict(sorted(glb.defaultLinks.items(), key=lambda x: x[1]['Index']))

    if JS.cache("page_links") is None or JS.cache("page_links") == "":
        JS.cache("page_links", dumps({}))

    if JS.cache("page_links_colums") is None or JS.cache("page_links_colums") == "":
        JS.cache("page_links_colums", 4)

    HTML.set(f'div', f'page', _id=f'page_links', _align=f'center')

    if not WS.glb.loggedIn:
        return None

    msgDict = WS.dict()

    if "qr" in msgDict:
        if " " in msgDict["qr"]["/Links.json"]:
            msgDict["qr"]["/Links.json"].pop(" ")

        glb.allLinks = {**glb.defaultLinks, **msgDict["qr"]["/Links.json"]}

    glb.allLinks = dict(sorted(glb.allLinks.items(), key=lambda x: x[1]['Index']))


def toggleCat(args: any):
    id = args.target.id

    if id == "":
        id = args.target.parentElement.id

    catStates = loads(JS.cache("page_links"))
    catStates[id.split("_")[2]] = not catStates[id.split("_")[2]]

    CSS.setStyle(f'page_links_{id.split("_")[2]}_header', f'borderBottom', f'2px solid #111')
    CSS.setStyles(f'page_links_{id.split("_")[2]}', ((f'position', f'unset'), (f'marginTop', f'0px'), (f'opacity', f'1')))

    if not catStates[id.split("_")[2]]:
        CSS.setStyle(f'page_links_{id.split("_")[2]}_header', f'borderBottom', f'4px solid #111')
        CSS.setStyles(f'page_links_{id.split("_")[2]}', ((f'position', f'absolute'), (f'marginTop', f'-9999px'), (f'opacity', f'0')))

    JS.cache("page_links", dumps(catStates))


def main():
    def newCat(cat: dict, visable: bool):
        if visable:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerBig %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 2px solid #111; user-select: none;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 1;')
        else:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerBig %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 4px solid #111; user-select: none;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 0; margin-top: -9999px; position: absolute;')

    setup()

    catStates = loads(JS.cache("page_links"))
    catRowCount = {}
    catColCount = {}

    for link in glb.allLinks:
        currentCat = glb.allLinks[link]["cat"]

        if not currentCat in catRowCount:
            if not currentCat in catStates:
                catStates[currentCat] = True

            newCat(currentCat, catStates[currentCat])
            catRowCount[currentCat] = 0
            catColCount[currentCat] = 0

        if catColCount[currentCat] % int(JS.cache("page_links_colums")) == 0:
            catRowCount[currentCat] += 1
            HTML.add(f'div', f'page_links_{currentCat}', _id=f'page_links_{currentCat}_row{catRowCount[currentCat]}', _align=f'center', _style=f'flex')

        catColCount[currentCat] += 1

        img = HTML.getLink(glb.allLinks[link]["url"], _nest=f'<img id="Image_{glb.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.allLinks[link]["text"]}" style="width: 30%; margin: 15px auto -10px auto; user-select:none;">')
        txt = HTML.add(f'p', _nest=HTML.getLink(glb.allLinks[link]["url"], _nest=glb.allLinks[link]["text"]))
        HTML.add(f'div', f'page_links_{currentCat}_row{catRowCount[currentCat]}', _nest=f'{img}{txt}', _style=f'width: {100 / int(JS.cache("page_links_colums"))}%; margin: 0px auto;')

    for cat in catRowCount:
        JS.addEvent(f'page_links_{cat}_header', toggleCat, "click")

    JS.cache("page_links", dumps(catStates))

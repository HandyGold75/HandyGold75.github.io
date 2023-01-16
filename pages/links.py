import mod.HTML as HTML
import mod.CSS as CSS
import mod.functions as f
from json import dumps, loads, load


class glb:
    links = {}
    columns = 4


def setup():
    file_R = open(f'pages/links.json', "r", encoding="UTF-8")
    glb.links = load(file_R)
    file_R.close()

    if f.cache("page_links") is None:
        f.cache("page_links", dumps({}))

    HTML.set(f'div', f'page', _id=f'page_links', _align=f'center')


def toggleCat(args: any):
    catStates = loads(f.cache("page_links"))
    catStates[args.target.id.split("_")[2]] = not catStates[args.target.id.split("_")[2]]

    CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}_header', f'borderBottom', f'2px solid #111')

    CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'position', f'unset')
    CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'marginTop', f'0px')
    CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'opacity', f'1')

    if not catStates[args.target.id.split("_")[2]]:
        CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}_header', f'borderBottom', f'4px solid #111')

        CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'position', f'absolute')
        CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'marginTop', f'-9999px')
        CSS.setStyle(f'page_links_{args.target.id.split("_")[2]}', f'opacity', f'0')

    f.cache("page_links", dumps(catStates))


def main():
    def newCat(cat: dict, visable: bool):
        if visable:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerMedium %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 2px solid #111;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 1;')
        else:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerMedium %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 4px solid #111;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 0; margin-top: -9999px; position: absolute;')

    setup()

    catStates = loads(f.cache("page_links"))
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
            HTML.add(f'div', f'page_links_{currentCat}', _id=f'page_links_{currentCat}_row{catObjLens[currentCat]}', _align=f'center', _style=f'flex')

        i += 1

        img = HTML.getLink(glb.links[link]["url"], _nest=f'<img id="Image_{glb.links[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.links[link]["text"]}" style="user-select:none; width: 30%; margin: 15px auto -10px auto;">')
        txt = HTML.add(f'p', _nest=HTML.getLink(glb.links[link]["url"], _nest=glb.links[link]["text"]))
        HTML.add(f'div', f'page_links_{currentCat}_row{catObjLens[currentCat]}', _nest=f'{img}{txt}', _style=f'width: {100 / glb.columns}%; margin: 0px auto;')

    for cat in catObjLens:
        f.addEvent(f'page_links_{cat}_header', toggleCat, "click")

    f.cache("page_links", dumps(catStates))

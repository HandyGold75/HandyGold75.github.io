import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.functions as f


class invoke:
    def SO(args=None):
        glb.mainPage = "Sonos"
        glb.currentSub = ""
        glb.subPages = ["Player", "Config"]

        glb.lastUpdate = 0


class glb:
    mainPage = ""
    currentSub = ""
    subPages = []

    lastUpdate = 0


def state(args=None):
    ws.send(f'sonos state')


def track(args=None):
    ws.send(f'sonos track')


def togglePlay(args=None):
    ws.send(f'sonos togglePlay')


def play(args=None):
    ws.send(f'sonos play')


def pause(args=None):
    ws.send(f'sonos pause')


def pageSub(args):
    def setup(args):
        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def player():
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_buttons', _style=f'divNormal')

        for but in ["state", "track", "togglePlay", "play", "pause"]:
            HTML.add(f'button', f'SubPage_page_buttons', _nest=f'{but}', _id=f'SubPage_page_buttons_{but}', _type=f'button', _style=f'buttonBig')

        f.addEvent(f'SubPage_page_buttons_state', state)
        f.addEvent(f'SubPage_page_buttons_track', track)
        f.addEvent(f'SubPage_page_buttons_togglePlay', togglePlay)
        f.addEvent(f'SubPage_page_buttons_play', play)
        f.addEvent(f'SubPage_page_buttons_pause', pause)

        for but in ["state", "track", "togglePlay", "play", "pause"]:
            CSS.onHover(f'SubPage_page_buttons_{but}', f'buttonHover')
            CSS.onClick(f'SubPage_page_buttons_{but}', f'buttonClick')

    def config():
        pass

    pageSubMap = {"Player": player, "Config": config}

    HTML.clear(f'SubPage_page')

    setup(args)

    pageSubMap[glb.currentSub]()


def main(args=None, sub=None):
    HTML.set(f'div', f'SubPage', _id=f'SubPage_nav', _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.add(f'div', f'SubPage', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')

    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'left', _style=f'width: 60%')
    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_options', _align=f'right', _style=f'width: 40%')

    for subPage in glb.subPages:
        HTML.add(f'button', f'SubPage_nav_main', _nest=f'{subPage}', _id=f'SubPage_nav_main_{subPage}', _type=f'button', _style=f'buttonSmall')

    for subPage in glb.subPages:
        f.addEvent(f'SubPage_nav_main_{subPage}', pageSub)
        CSS.onHover(f'SubPage_nav_main_{subPage}', f'buttonHover')
        CSS.onClick(f'SubPage_nav_main_{subPage}', f'buttonClick')

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

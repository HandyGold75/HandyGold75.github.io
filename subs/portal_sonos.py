import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.functions as f
from datetime import datetime, timedelta


class invoke:
    def SO(args=None):
        glb.mainPage = "Sonos"
        glb.currentSub = ""
        glb.subPages = ["Player", "Config"]

        glb.lastUpdate = 0

        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        try:
            ws.send(f'sonos state')
            ws.send(f'sonos track')
        except ConnectionError:
            f.connectionError()

        glb.lastUpdate = datetime.now().timestamp()


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


def volumeGet(args=None):
    ws.send(f'sonos volume get')


def volumeUp(args=None):
    ws.send(f'sonos volume up')


def volumeDown(args=None):
    ws.send(f'sonos volume down')


def pageSub(args):
    def setup(args):
        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def player():
        def addAlbumArt():
            def updateAlbumArt():
                data = ws.msgDict()["sonos"]

                try:
                    HTML.get(f'Image_AlbumArt').src = data["track"]["album_art"]
                    HTML.get(f'Image_AlbumArt').alt = data["track"]["title"]
                except AttributeError:
                    return None

                f.afterDelay(track, 500)
                f.afterDelay(updateAlbumArt, 1000)

            data = ws.msgDict()["sonos"]

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second

            img = HTML.add(f'img', _id="Image_AlbumArt", _style="width: 50%; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_albumArt', _nest=f'{img}', _style=f'divNormal')

            updateAlbumArt()

        def addVideo():
            data = ws.msgDict()["sonos"]
            f.log(str(data["device"]))
            f.log(str(data["track"]))

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second

            img = HTML.add(f'img', _style=f'z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Transparent.png" alt="Black"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_videoCover', _nest=f'{img}', _style=f'margin-bottom: -42.1875%; position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

            ifr = HTML.add(f'iframe',
                           _id="Image_AlbumArt",
                           _style=f'position: absolute; top: 0; left: 0; width: 100%; height: 100%;',
                           _custom=f'src="https://www.youtube.com/embed/7NK_JOkuSVY?start=5&autoplay=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&rel=0" frameborder="0"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_video', _nest=f'{ifr}', _style=f'position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

        def addOldControls():
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_buttons', _style=f'divNormal')

            for but in ["state", "track", "toggle play", "play", "pause", "volume get", "volume up", "volume down"]:
                HTML.add(f'button', f'SubPage_page_buttons', _nest=f'{but}', _id=f'SubPage_page_buttons_{but}', _type=f'button', _style=f'buttonBig')

            f.addEvent(f'SubPage_page_buttons_state', state)
            f.addEvent(f'SubPage_page_buttons_track', track)
            f.addEvent(f'SubPage_page_buttons_toggle play', togglePlay)
            f.addEvent(f'SubPage_page_buttons_play', play)
            f.addEvent(f'SubPage_page_buttons_pause', pause)
            f.addEvent(f'SubPage_page_buttons_volume get', volumeGet)
            f.addEvent(f'SubPage_page_buttons_volume up', volumeUp)
            f.addEvent(f'SubPage_page_buttons_volume down', volumeDown)

            for but in ["state", "track", "toggle play", "play", "pause", "volume get", "volume up", "volume down"]:
                CSS.onHover(f'SubPage_page_buttons_{but}', f'buttonHover')
                CSS.onClick(f'SubPage_page_buttons_{but}', f'buttonClick')

        def addControls():
            pass

        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal')

        addControls()
        addOldControls()

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

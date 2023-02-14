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

    videoScolling = False
    sendedSeek = True


class sonosControl:
    def state(args=None):
        ws.send(f'sonos state')

    def track(args=None):
        ws.send(f'sonos track')

    def togglePlay(args=None):
        def doAction():
            data = ws.msgDict()["sonos"]

            f.log(str(data["device"]))
            f.log(str(data["track"]))

            if data["device"]["playback"] == "active":
                ws.send(f'sonos pause')
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Play'

            elif data["device"]["playback"] == "standby":
                ws.send(f'sonos play')
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            elif data["device"]["playback"] == "inactive":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            else:
                ws.send(f'sonos state')
                f.afterDelay(doAction, 100)

        ws.send(f'sonos state')
        f.afterDelay(doAction, 100)

    def play(args=None):
        ws.send(f'sonos play')

    def pause(args=None):
        ws.send(f'sonos pause')

    def next(args=None):
        ws.send(f'sonos next')

    def back(args=None):
        ws.send(f'sonos back')

    def volume(args=None, vol: int = None):
        if args is None:
            if vol is None:
                return None

            ws.send(f'sonos volume {vol}')
            return None

        ws.send(f'sonos volume {int(args.target.value)}')

    def seek(args=None, pos: int = None):
        if args is None:
            if pos is None:
                return None

            ws.send(f'sonos seek {pos}')
            glb.sendedSeek = True
            return None

        ws.send(f'sonos seek {int(args.target.value)}')
        glb.sendedSeek = True

    def volumeUp(args=None):
        ws.send(f'sonos volume up')

    def volumeDown(args=None):
        ws.send(f'sonos volume down')


def getPosDur():
    data = ws.msgDict()["sonos"]

    pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
    pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
    dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
    dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

    return pos, dur


def pageSub(args):
    def setup(args):
        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def player():
        def updateUI():
            data = ws.msgDict()["sonos"]
            pos, dur = getPosDur()

            HTML.get(f'Image_AlbumArt').src = data["track"]["album_art"]
            HTML.get(f'Image_AlbumArt').alt = data["track"]["title"]

            if not glb.videoScolling:
                if not glb.sendedSeek:
                    HTML.get(f'SubPage_page_timeline_slider').max = dur
                    HTML.get(f'SubPage_page_timeline_slider').value = pos

                glb.sendedSeek = False

            if data["device"]["playback"] == "active":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Play'

            elif data["device"]["playback"] == "standby":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            elif data["device"]["playback"] == "inactive":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            HTML.get(f'SubPage_page_volume_slider').value = data["device"]["volume"]

            f.afterDelay(sonosControl.track, 500)
            f.afterDelay(sonosControl.state, 500)
            f.afterDelay(updateUI, 1000)

        def addAlbumArt():
            data = ws.msgDict()["sonos"]

            img = HTML.add(f'img', _id="Image_AlbumArt", _style="width: 50%; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_albumArt', _nest=f'{img}', _style=f'divNormal')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% justify-content: center;')

            pos, dur = getPosDur()

            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 50%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')

            def doAction():
                def videoScollFalse(args=None):
                    glb.videoScolling = False

                def videoScollTrue(args=None):
                    glb.videoScolling = True

                f.addEvent(f'SubPage_page_timeline_slider', sonosControl.seek, f'change')
                f.addEvent(f'SubPage_page_timeline_slider', videoScollTrue, f'mousedown')
                f.addEvent(f'SubPage_page_timeline_slider', videoScollFalse, f'mouseup')

            f.afterDelay(doAction, 200)

        def addVideo():
            data = ws.msgDict()["sonos"]
            f.log(str(data["device"]))
            f.log(str(data["track"]))

            pos, dur = getPosDur()

            img = HTML.add(f'img', _style=f'z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Transparent.png" alt="Black"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_videoCover', _nest=f'{img}', _style=f'margin-bottom: -42.1875%; position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

            ifr = HTML.add(f'iframe',
                           _id="Image_AlbumArt",
                           _style=f'position: absolute; top: 0; left: 0; width: 100%; height: 100%;',
                           _custom=f'src="https://www.youtube.com/embed/7NK_JOkuSVY?start=5&autoplay=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&rel=0" frameborder="0"')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_video', _nest=f'{ifr}', _style=f'position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% justify-content: center;')

            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 50%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')

        def addOldControls():
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_buttons', _style=f'divNormal')

            for but in ["state", "track", "toggle play", "play", "pause", "next", "back", "volume get", "volume up", "volume down"]:
                HTML.add(f'button', f'SubPage_page_buttons', _nest=f'{but}', _id=f'SubPage_page_buttons_{but}', _type=f'button', _style=f'buttonBig')

            f.addEvent(f'SubPage_page_buttons_state', sonosControl.state)
            f.addEvent(f'SubPage_page_buttons_track', sonosControl.track)
            f.addEvent(f'SubPage_page_buttons_toggle play', sonosControl.togglePlay)
            f.addEvent(f'SubPage_page_buttons_play', sonosControl.play)
            f.addEvent(f'SubPage_page_buttons_pause', sonosControl.pause)
            f.addEvent(f'SubPage_page_buttons_next', sonosControl.next)
            f.addEvent(f'SubPage_page_buttons_back', sonosControl.back)
            f.addEvent(f'SubPage_page_buttons_volume get', sonosControl.volumeGet)
            f.addEvent(f'SubPage_page_buttons_volume up', sonosControl.volumeUp)
            f.addEvent(f'SubPage_page_buttons_volume down', sonosControl.volumeDown)

            for but in ["state", "track", "toggle play", "play", "pause", "next", "back", "volume get", "volume up", "volume down"]:
                CSS.onHover(f'SubPage_page_buttons_{but}', f'buttonHover')
                CSS.onClick(f'SubPage_page_buttons_{but}', f'buttonClick')

        def addControls():
            data = ws.msgDict()["sonos"]

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_buttons', _style=f'divNormal %% flex %% justify-content: center;')

            for action in ["Back", "Pause", "Next"]:
                img = HTML.add(f'img', _id=f'SubPage_page_buttons_img{action}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.add(f'button', _id=f'SubPage_page_buttons_{action}', _nest=f'{img}', _style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.add(f'div', f'SubPage_page_buttons', _nest=f'{btn}', _align=f'center', _style=f'max-width: 50px; margin: 10px 5px 10px 5px;')

            if data["device"]["playback"] == "active":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Play'

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_volume', _style=f'divNormal %% flex %% margin-top: 0px; justify-content: center;')

            options = ""
            for option in range(0, 101, 10):
                options += HTML.add(f'option', _custom=f'value="{option}" label="{option}"')

            HTML.add(f'datalist', f'SubPage_page_volume', _nest=f'{options}', _id=f'SubPage_page_volume_datalist')

            HTML.add(f'input', f'SubPage_page_volume', _id=f'SubPage_page_volume_slider', _type=f'range', _style=f'inputRange %% width: 25%;', _custom=f'min="0" max="100" value="{data["device"]["volume"]}" list="SubPage_page_volume_datalist"')

            f.addEvent(f'SubPage_page_buttons_Back', sonosControl.back)
            f.addEvent(f'SubPage_page_buttons_Pause', sonosControl.togglePlay)
            f.addEvent(f'SubPage_page_buttons_Next', sonosControl.next)
            f.addEvent(f'SubPage_page_volume_slider', sonosControl.volume, f'input')

            for action in ["Back", "Pause", "Next"]:
                CSS.onHover(f'SubPage_page_buttons_{action}', f'imgHover')
                CSS.onClick(f'SubPage_page_buttons_{action}', f'imgClick')

        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal')

        addAlbumArt()
        addControls()

        updateUI()

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

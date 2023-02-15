import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.functions as f
from json import dumps, loads
from datetime import datetime, timedelta


class invoke:
    def SO(args=None):
        glb.mainPage = "Sonos"
        glb.currentSub = ""
        glb.subPages = ["Player", "QR", "Config"]

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

    config = {}

    videoScolling = False
    skipUiUpdate = True


class sonosControl:
    def state(args=None):
        ws.send(f'sonos state')

    def track(args=None):
        ws.send(f'sonos track')

    def togglePlay(args=None):
        data = ws.msgDict()["sonos"]

        if data["device"]["playback"] == "active":
            ws.send(f'sonos pause')

        elif data["device"]["playback"] == "standby":
            ws.send(f'sonos play')

    def next(args=None):
        ws.send(f'sonos next')

    def back(args=None):
        ws.send(f'sonos back')

    def volume(args=None, vol: int = None):
        if args is None:
            if vol is None or vol > glb.config["volumeMax"]:
                return None

            ws.send(f'sonos volume {vol}')
            return None

        if not int(args.target.value) > glb.config["volumeMax"]:
            ws.send(f'sonos volume {int(args.target.value)}')

    def volumeUp(args=None):
        data = ws.msgDict()["sonos"]

        if data["device"]["volume"] + 5 > glb.config["volumeMax"]:
            ws.send(f'sonos volume {glb.config["volumeMax"]}')
            return None

        ws.send(f'sonos volume up')

    def volumeDown(args=None):
        ws.send(f'sonos volume down')

    def seek(args=None, pos: int = None):
        if args is None:
            if pos is None:
                return None

            ws.send(f'sonos seek {pos}')
            glb.skipUiUpdate = True
            return None

        ws.send(f'sonos seek {int(args.target.value)}')
        glb.skipUiUpdate = True

    def seekForward(args=None):
        data = ws.msgDict()["sonos"]

        newPos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) + glb.config["seekStep"]
        dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
        dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

        if newPos >= dur:
            newPos = dur

        sonosControl.seek(pos=newPos)
        glb.skipUiUpdate = True

    def seekBackward(args=None):
        data = ws.msgDict()["sonos"]

        newPos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) - glb.config["seekStep"]

        if newPos < 0:
            newPos = 0

        sonosControl.seek(pos=newPos)
        glb.skipUiUpdate = True


def setup():
    if f.cache("page_portal_sonos") is None or f.cache("page_links") == "":
        f.cache("page_portal_sonos", dumps({"volumeMax": 50, "seekStep": 10}))

    sonosConfig = loads(f.cache("page_portal_sonos"))

    glb.config = sonosConfig


def pageSub(args):
    def setup(args):
        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def player():
        def updateUI():
            data = ws.msgDict()["sonos"]

            if data["device"]["playback"] == "busy":
                f.afterDelay(sonosControl.state, 500)
                f.afterDelay(updateUI, 1000)

                return None

            if glb.skipUiUpdate:
                glb.skipUiUpdate = False

                f.afterDelay(sonosControl.state, 500)
                f.afterDelay(updateUI, 1000)

                return None

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = ws.msgDict()["sonos"]["track"]["position"]
            if int(ws.msgDict()["sonos"]["track"]["position"].split(":")[0]) == 0:
                posStr = ":".join(ws.msgDict()["sonos"]["track"]["position"].split(":")[1:])

            durStr = ws.msgDict()["sonos"]["track"]["duration"]
            if int(ws.msgDict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(ws.msgDict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.get(f'Image_AlbumArt').src = data["track"]["album_art"]
            HTML.get(f'Image_AlbumArt').alt = data["track"]["title"]

            HTML.get(f'SubPage_page_timeline_position').innerHTML = posStr
            HTML.get(f'SubPage_page_timeline_duration').innerHTML = durStr

            if not glb.videoScolling:
                HTML.get(f'SubPage_page_timeline_slider').max = dur
                HTML.get(f'SubPage_page_timeline_slider').value = pos

            if data["device"]["playback"] == "active":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            elif data["device"]["playback"] == "standby":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Play'

            elif data["device"]["playback"] == "inactive":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Pause.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Pause'

            HTML.get(f'SubPage_page_volume_slider').value = data["device"]["volume"]

            CSS.get(f'SubPage_nav', f'scrollIntoView')()

            f.afterDelay(sonosControl.track, 500)
            f.afterDelay(sonosControl.state, 500)
            f.afterDelay(updateUI, 1000)

        def addAlbumArt():
            data = ws.msgDict()["sonos"]

            img = HTML.add(f'img', _id="Image_AlbumArt", _style="width: 100%; max-width: 69vh; max-height: 69vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_albumArt', _nest=f'{img}', _style=f'divNormal %% width: 100%;')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% width: 100%; max-width: 69vh; justify-content: center;')

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = ws.msgDict()["sonos"]["track"]["position"]
            if int(ws.msgDict()["sonos"]["track"]["position"].split(":")[0]) == 0:
                posStr = ":".join(ws.msgDict()["sonos"]["track"]["position"].split(":")[1:])

            durStr = ws.msgDict()["sonos"]["track"]["duration"]
            if int(ws.msgDict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(ws.msgDict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{posStr}', _id=f'SubPage_page_timeline_position', _style=f'color: #F7E163; width: 10%;')
            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 80%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{durStr}', _id=f'SubPage_page_timeline_duration', _style=f'color: #F7E163; width: 10%;')

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

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            img = HTML.add(f'img', _style=f'z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Transparent.png" alt="Black"')
            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_videoCover', _nest=f'{img}', _style=f'margin-bottom: -42.1875%; position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

            ifr = HTML.add(f'iframe',
                           _id="Image_AlbumArt",
                           _style=f'position: absolute; top: 0; left: 0; width: 100%; height: 100%;',
                           _custom=f'src="https://www.youtube.com/embed/7NK_JOkuSVY?start=5&autoplay=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&rel=0" frameborder="0"')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_main_video', _nest=f'{ifr}', _style=f'position: relative; width: 75%; height: 0px; padding-bottom: 42.1875%;')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% justify-content: center;')

            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{ws.msgDict()["sonos"]["track"]["position"]}', _id=f'SubPage_page_timeline_position', _style=f'color: #F7E163;')
            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 75%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{ws.msgDict()["sonos"]["track"]["duration"]}', _id=f'SubPage_page_timeline_duration', _style=f'color: #F7E163;')

        def addControls():
            data = ws.msgDict()["sonos"]

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_buttons', _style=f'divNormal %% flex %% width: 50%; margin: 0px; padding: 0px;')

            for action in ["VolumeDown", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "VolumeUp"]:
                img = HTML.add(f'img', _id=f'SubPage_page_buttons_img{action}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.add(f'button', _id=f'SubPage_page_buttons_{action}', _nest=f'{img}', _style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.add(f'div', f'SubPage_page_buttons', _nest=f'{btn}', _align=f'center', _style=f'max-width: 50px; margin: 10px auto 10px auto;')

            if data["device"]["playback"] == "standby":
                HTML.get(f'SubPage_page_buttons_imgPause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_imgPause').alt = f'Play'

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_volume', _style=f'divNormal %% flex %% width: 50%; margin: 0px; padding: 0px; justify-content: center;')

            options = ""
            for option in range(0, 101, int(glb.config["volumeMax"] / 10)):
                options += HTML.add(f'option', _custom=f'value="{option}" label="{option}"')

            HTML.add(f'datalist', f'SubPage_page_volume', _nest=f'{options}', _id=f'SubPage_page_volume_datalist')

            HTML.add(f'input',
                     f'SubPage_page_volume',
                     _id=f'SubPage_page_volume_slider',
                     _type=f'range',
                     _style=f'inputRange %% width: 90%; height: 10px',
                     _custom=f'min="0" max="{glb.config["volumeMax"]}" value="{data["device"]["volume"]}" list="SubPage_page_volume_datalist"')

            f.addEvent(f'SubPage_page_buttons_VolumeDown', sonosControl.volumeDown)
            f.addEvent(f'SubPage_page_buttons_SeekBackward', sonosControl.seekBackward)
            f.addEvent(f'SubPage_page_buttons_Back', sonosControl.back)
            f.addEvent(f'SubPage_page_buttons_Pause', sonosControl.togglePlay)
            f.addEvent(f'SubPage_page_buttons_Next', sonosControl.next)
            f.addEvent(f'SubPage_page_buttons_VolumeUp', sonosControl.volumeUp)
            f.addEvent(f'SubPage_page_buttons_SeekForward', sonosControl.seekForward)
            f.addEvent(f'SubPage_page_volume_slider', sonosControl.volume, f'input')

            for action in ["VolumeDown", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "VolumeUp"]:
                CSS.onHover(f'SubPage_page_buttons_{action}', f'imgHover')
                CSS.onClick(f'SubPage_page_buttons_{action}', f'imgClick')

        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal')

        addAlbumArt()
        addControls()

        updateUI()

        # f.afterDelay(CSS.get(f'SubPage_page_main', f'scrollIntoView'), 1000)

    def qr():
        HTML.add(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal %% flex %% justify-content: center;')

        txt = HTML.add(f'h1', _nest=f'Sonos S2 - Android', _style=f'headerBig')
        img = HTML.add(f'img', _id="Image_SonosAndroidQR", _style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="docs/assets/Portal/Sonos/SonosAndroidQR.png" alt="Sonos Android QR"')
        HTML.add(f'div', f'SubPage_page_main', _nest=f'{txt}{img}', _id=f'SubPage_page_main_qrAndroid', _style=f'divNormal %% margin: 15px 50px;')

        txt = HTML.add(f'h1', _nest=f'Sonos S2 - iOS', _style=f'headerBig')
        img = HTML.add(f'img', _id="Image_SonosIosQR", _style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="docs/assets/Portal/Sonos/SonosIosQR.png" alt="Sonos iOS QR"')
        HTML.add(f'div', f'SubPage_page_main', _nest=f'{txt}{img}', _id=f'SubPage_page_main_qrIos', _style=f'divNormal %% margin: 15px 50px;')

    def config():
        pass

    pageSubMap = {"Player": player, "QR": qr, "Config": config}

    HTML.clear(f'SubPage_page')

    setup(args)

    pageSubMap[glb.currentSub]()


def main(args=None, sub=None):
    setup()

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

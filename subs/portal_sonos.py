from WebKit import HTML, CSS, JS, WS
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
        WS.send(f'sonos state')
        WS.send(f'sonos que get')
        WS.send(f'sonos ytinfo')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    mainPage = ""
    currentSub = ""
    subPages = []

    lastUpdate = 0
    ytPlayer = None

    config = {}
    knownConfig = {"volumeMax": int, "seekStep": int, "useAlbumArt": bool, "disableMaxWidth (experimental)": bool}
    optionsList = []
    currentTitle = ""
    currentPosition = ""
    currentQueSize = 0

    useAlbumArt = False
    videoScolling = False
    skipUiUpdate = True


class sonosControl:
    def state(args=None):
        WS.send(f'sonos state')

    def ytinfo(args=None):
        WS.send(f'sonos ytinfo')

    def togglePlay(args=None):
        data = WS.dict()["sonos"]

        if data["device"]["playback"] == "active":
            WS.send(f'sonos pause')

        elif data["device"]["playback"] in ["standby", "inactive"]:
            WS.send(f'sonos play')

    def toggleShuffle(args=None):
        WS.send(f'sonos toggleShuffle')

    def toggleRepeat(args=None):
        WS.send(f'sonos toggleRepeat')

    def next(args=None):
        WS.send(f'sonos next')

    def back(args=None):
        WS.send(f'sonos back')

    def volume(args=None, vol: int = None):
        if args is None:
            if vol is None or vol > glb.config["volumeMax"]:
                return None

            WS.send(f'sonos volume {vol}')
            return None

        if not int(args.target.value) > glb.config["volumeMax"]:
            WS.send(f'sonos volume {int(args.target.value)}')

    def volumeUp(args=None):
        data = WS.dict()["sonos"]

        if data["device"]["volume"] + 5 > glb.config["volumeMax"]:
            WS.send(f'sonos volume {glb.config["volumeMax"]}')
            return None

        WS.send(f'sonos volume up')

    def volumeDown(args=None):
        WS.send(f'sonos volume down')

    def seek(args=None, pos: int = None):
        if args is None:
            if pos is None:
                return None

            WS.send(f'sonos seek {pos}')
            glb.skipUiUpdate = True
            return None

        WS.send(f'sonos seek {int(args.target.value)}')
        glb.skipUiUpdate = True

    def seekForward(args=None):
        data = WS.dict()["sonos"]

        newPos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) + glb.config["seekStep"]
        dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
        dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

        if newPos >= dur:
            newPos = dur

        sonosControl.seek(pos=newPos)
        glb.skipUiUpdate = True

    def seekBackward(args=None):
        data = WS.dict()["sonos"]

        newPos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) - glb.config["seekStep"]

        if newPos < 0:
            newPos = 0

        sonosControl.seek(pos=newPos)
        glb.skipUiUpdate = True

    def getQue():
        WS.send(f'sonos que get')

    def setQue(index: int):
        WS.send(f'sonos que {index}')

    def remQue(index: int):
        WS.send(f'sonos queRemove {index}')

    def addQue(url: str, playNow: bool = False):
        if not url.startswith("https://open.spotify.com/track/"):
            return None

        if not playNow:
            WS.send(f'sonos playNext {url}')
        else:
            WS.send(f'sonos playNow {url}')


def pageSub(args):
    def setup(args):
        if JS.cache("page_portal_sonos") is None or JS.cache("page_links") == "":
            JS.cache("page_portal_sonos", dumps({"volumeMax": 50, "seekStep": 15, "useAlbumArt": False, "disableMaxWidth (experimental)": False}))

        glb.config = loads(JS.cache("page_portal_sonos"))

        if f'{args.target.id.split("_")[-1]}' in glb.subPages:
            glb.currentSub = args.target.id.split("_")[-1]

    def player():
        def slowUIRefresh():
            def controls():
                data = WS.dict()["sonos"]

                pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
                pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
                dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
                dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

                posStr = WS.dict()["sonos"]["track"]["position"]
                if int(WS.dict()["sonos"]["track"]["position"].split(":")[0]) == 0:
                    posStr = ":".join(WS.dict()["sonos"]["track"]["position"].split(":")[1:])
                durStr = WS.dict()["sonos"]["track"]["duration"]
                if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                    durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

                HTML.get(f'SubPage_page_timeline_position').innerHTML = posStr
                HTML.get(f'SubPage_page_timeline_duration').innerHTML = durStr

                if not data["device"]["shuffle"]:
                    CSS.setStyles(f'SubPage_page_buttons_Shuffle', ((f'background', f'#222'), (f'border', f'2px solid #222')))

                if not data["device"]["repeat"]:
                    CSS.setStyles(f'SubPage_page_buttons_Repeat', ((f'background', f'#222'), (f'border', f'2px solid #222')))

                if not glb.videoScolling:
                    HTML.get(f'SubPage_page_timeline_slider').max = dur
                    HTML.get(f'SubPage_page_timeline_slider').value = pos

                if data["device"]["playback"] == "active":
                    HTML.get(f'SubPage_page_buttons_img_Pause').src = f'docs/assets/Portal/Sonos/Pause.png'
                    HTML.get(f'SubPage_page_buttons_img_Pause').alt = f'Pause'
                elif data["device"]["playback"] in ["standby", "inactive"]:
                    HTML.get(f'SubPage_page_buttons_img_Pause').src = f'docs/assets/Portal/Sonos/Play.png'
                    HTML.get(f'SubPage_page_buttons_img_Pause').alt = f'Play'

                HTML.get(f'SubPage_page_volume_slider').value = data["device"]["volume"]

            def que():
                data = WS.dict()["sonos"]

                if data["que"]["position"] != glb.currentPosition or data["que"]["size"] != glb.currentQueSize:
                    addQue()

                    CSS.setStyles(f'SubPage_page_que_{glb.currentPosition}', ((f'background', f'#222'), (f'color', f'#55F'), (f'border', f'5px solid #111'), (f'borderRadius ', f'10px'), (f'zIndex ', f'0')))
                    CSS.setStyles(f'SubPage_page_que_{data["que"]["position"]}', ((f'background', f'#444'), (f'color', f'#F7E163'), (f'border', f'5px solid #F7E163'), (f'borderRadius', f'0px'), (f'zIndex ', f'100')))

                    CSS.get(f'SubPage_page_que_{data["que"]["position"]}', f'scrollIntoView')()

                    glb.currentPosition = data["que"]["position"]
                    glb.currentQueSize = data["que"]["size"]

            def albumArt():
                data = WS.dict()["sonos"]

                HTML.get(f'Image_AlbumArt').src = data["track"]["album_art"]
                HTML.get(f'Image_AlbumArt').alt = data["track"]["title"]

            def video():
                data = WS.dict()["sonos"]

                pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
                pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second

                glb.ytPlayer.setVolume(0)
                glb.ytPlayer.mute(0)

                if not data["ytinfo"]["id"] in glb.ytPlayer.getVideoUrl():
                    glb.ytPlayer.loadVideoById(f'{data["ytinfo"]["id"]}')

                if data["device"]["playback"] == "active" and glb.ytPlayer.getPlayerState() != 1:
                    glb.ytPlayer.playVideo()
                elif data["device"]["playback"] != "active":
                    glb.ytPlayer.pauseVideo()

                newPos = pos + 1
                oldPos = glb.ytPlayer.getCurrentTime()

                if oldPos is None:
                    oldPos = 0

                if not newPos < oldPos + 1 or not newPos > oldPos - 1:
                    glb.ytPlayer.seekTo(newPos)

            if not glb.currentSub == "Player":
                return False

            data = WS.dict()["sonos"]

            if data["track"]["title"] != glb.currentTitle:
                sonosControl.getQue()
                sonosControl.ytinfo()
            glb.currentTitle = data["track"]["title"]

            if data["device"]["playback"] == "busy" or glb.skipUiUpdate:
                glb.skipUiUpdate = False

                JS.afterDelay(sonosControl.state, 500)
                JS.afterDelay(sonosControl.getQue, 500)
                JS.afterDelay(slowUIRefresh, 1000)

                return None

            try:
                controls()
                que()

                if glb.useAlbumArt:
                    albumArt()
                else:
                    video()
            except AttributeError:
                return None

            CSS.get(f'SubPage_nav', f'scrollIntoView')()

            JS.afterDelay(sonosControl.state, 500)
            JS.afterDelay(sonosControl.getQue, 500)
            JS.afterDelay(slowUIRefresh, 1000)

        def fastUIRefresh():
            def controls(data):
                if data["device"]["shuffle"]:
                    CSS.setStyles(f'SubPage_page_buttons_Shuffle', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                if data["device"]["repeat"]:
                    CSS.setStyles(f'SubPage_page_buttons_Repeat', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))

            if not glb.currentSub == "Player":
                return False

            data = WS.dict()["sonos"]

            try:
                controls(data)
            except AttributeError:
                return None

            JS.afterDelay(fastUIRefresh, 250)

        def addAlbumArt():
            glb.useAlbumArt = True
            data = WS.dict()["sonos"]

            HTML.set(f'div', f'SubPage_page_media', _id=f'SubPage_page_art', _style=f'divNormal %% width: 75%; margin: -30px auto 15px auto;')

            img = HTML.add(f'img', _id="Image_AlbumArt", _style="width: 100%; max-width: 69vh; max-height: 69vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"')
            HTML.set(f'div', f'SubPage_page_art', _nest=f'{img}', _id=f'SubPage_page_art_albumArt', _style=f'divNormal %% width: 75%;')

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; justify-content: center;')

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = WS.dict()["sonos"]["track"]["position"]
            if int(WS.dict()["sonos"]["track"]["position"].split(":")[0]) == 0:
                posStr = ":".join(WS.dict()["sonos"]["track"]["position"].split(":")[1:])

            durStr = WS.dict()["sonos"]["track"]["duration"]
            if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{posStr}', _id=f'SubPage_page_timeline_position', _style=f'color: #F7E163; width: 10%;')
            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 80%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{durStr}', _id=f'SubPage_page_timeline_duration', _style=f'color: #F7E163; width: 10%;')

            def doAction():
                def videoScollFalse(args=None):
                    glb.videoScolling = False

                def videoScollTrue(args=None):
                    glb.videoScolling = True

                JS.addEvent(f'SubPage_page_timeline_slider', sonosControl.seek, f'change')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollTrue, f'mousedown')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollFalse, f'mouseup')

            JS.afterDelay(doAction, 200)

        def addVideo():
            glb.useAlbumArt = False
            data = WS.dict()["sonos"]

            pos = datetime.strptime(data["track"]["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = WS.dict()["sonos"]["track"]["position"]
            if int(WS.dict()["sonos"]["track"]["position"].split(":")[0]) == 0:
                posStr = ":".join(WS.dict()["sonos"]["track"]["position"].split(":")[1:])

            durStr = WS.dict()["sonos"]["track"]["duration"]
            if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.set(f'div', f'SubPage_page_media', _id=f'SubPage_page_art', _style=f'divNormal %% width: 75%; margin: 0px auto;')

            img = HTML.add(f'img', _style=f'z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Transparent.png" alt="Black"')
            HTML.set(f'div', f'SubPage_page_art', _nest=f'{img}', _id=f'SubPage_page_art_videoCover', _style=f'margin-bottom: -56.25%; position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;')

            ifr = HTML.add(f'div', _id=f'iframe_YTVideo', _style=f'position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'frameborder="0"')
            HTML.add(f'div', f'SubPage_page_art', _nest=f'{ifr}', _id=f'div_YTVideo', _style=f'position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;')

            def loadYtPlayer():
                glb.ytPlayer = JS.jsEval("new YT.Player('iframe_YTVideo', { videoId: '', playerVars: { 'autoplay': 0, 'controls': 0, 'disablekb': 1, 'fs': 0, 'iv_load_policy': 3, 'modestbranding': 1, 'rel': 0 } } );")

            JS.aSync(loadYtPlayer)

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_timeline', _style=f'divNormal %% flex %% width: 100%; margin: 0px auto; justify-content: center;')

            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{posStr}', _id=f'SubPage_page_timeline_position', _style=f'color: #F7E163; width: 10%;')
            HTML.add(f'input', f'SubPage_page_timeline', _id=f'SubPage_page_timeline_slider', _type=f'range', _style=f'inputRange %% width: 80%; user-select: none;', _custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.add(f'p', f'SubPage_page_timeline', _nest=f'{durStr}', _id=f'SubPage_page_timeline_duration', _style=f'color: #F7E163; width: 10%;')

            def doAction():
                def videoScollFalse(args=None):
                    glb.videoScolling = False

                def videoScollTrue(args=None):
                    glb.videoScolling = True

                JS.addEvent(f'SubPage_page_timeline_slider', sonosControl.seek, f'change')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollTrue, f'mousedown')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollFalse, f'mouseup')

            JS.afterDelay(doAction, 200)

        def addQue():
            def playFromQue(args):
                el = args.target

                for i in range(0, 4):
                    if el.id == "":
                        el = el.parentElement
                        continue

                    try:
                        int(el.id.split("_")[-1])
                    except ValueError:
                        el = el.parentElement
                        continue

                    sonosControl.setQue(f'{el.id.split("_")[-1]}')
                    glb.currentPosition = -1
                    return None

            def removeFromQue(args):
                el = args.target

                for i in range(0, 6):
                    if el.id == "":
                        el = el.parentElement
                        continue

                    try:
                        int(el.id.split("_")[-1])
                    except ValueError:
                        el = el.parentElement
                        continue

                    sonosControl.remQue(f'{el.id.split("_")[-1]}')
                    glb.currentPosition = -1
                    return None

            def playNext(args):
                sonosControl.addQue(HTML.get(f'SubPage_page_queAdd_input').value, False)

            def playNow(args):
                sonosControl.addQue(HTML.get(f'SubPage_page_queAdd_input').value, True)

            data = WS.dict()["sonos"]

            if HTML.get(f'SubPage_page_que') is None:
                que = HTML.add(f'div', _id=f'SubPage_page_queList', _style=f'divNormal %% position: relative; height: 90%; padding: 0px; margin: -5px; border: 5px solid #111; overflow-x: hidden;')
                queAdd = HTML.add(f'div', _id=f'SubPage_page_queAdd', _style=f'divNormal %% position: relative; height: 10%; min-height: 55px; padding: 0px; margin: -5px; border: 5px solid #111;')

                if glb.config["useAlbumArt"]:
                    HTML.add(f'div',
                             f'SubPage_page_media',
                             _id=f'SubPage_page_que',
                             _nest=f'{que}{queAdd}',
                             _style=f'divNormal %% position: relative; width: 50%; height: 37vw; max-height: 540px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')

                else:
                    HTML.add(f'div',
                             f'SubPage_page_media',
                             _id=f'SubPage_page_que',
                             _nest=f'{que}{queAdd}',
                             _style=f'divNormal %% position: relative; width: 25%; height: 36vw; max-height: 545px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')
            else:
                HTML.setRaw(f'SubPage_page_queList', "")

            tracks = data["que"]["tracks"]

            queHTML = ""

            for track in tracks:
                img = HTML.add(f'img', _id=f'SubPage_page_que_{track}_img', _style=f'width: 20%; max-width: 50px; height: 50px;', _align=f'left', _custom=f'src="{tracks[track]["album_art_uri"]}" alt="Art"')

                txt = HTML.add(f'p', _nest=f'{tracks[track]["title"]}', _style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', _align=f'left')
                remImg = HTML.add(f'img', _id=f'SubPage_page_que_rem_img_{track}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                remBtn = HTML.add(f'button', _nest=f'{remImg}', _id=f'SubPage_page_que_rem_{track}', _style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                rem = HTML.add(f'div', _nest=f'{remBtn}', _align=f'right', _style=f'max-width: 24px; max-height: 24px; margin: 0px 0px 0px auto;')
                title = HTML.add(f'div', _nest=f'{txt}{rem}', _style=f'flex %% margin: 0px;')

                txt = HTML.add(f'p', _nest=f'{tracks[track]["creator"]}', _style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', _align=f'left')
                dur = HTML.add(f'p', _nest=f'{tracks[track]["duration"][-5:]}', _style=f'margin: 0px 0px 0px auto;', _align=f'right')
                creator = HTML.add(f'div', _nest=f'{txt}{dur}', _style=f'flex %% font-size: 75%; margin: 0px;')

                txtDiv = HTML.add(f'div', _nest=f'{title}{creator}', _id=f'SubPage_page_que_{track}_txt', _style=f'width: 90%; margin: auto 5px;')

                queHTML += HTML.add(f'div', _nest=f'{img}{txtDiv}', _id=f'SubPage_page_que_{track}', _class=f'SubPage_page_que_tracks', _style=f'divNormal %% flex %% position: relative; margin: -5px -5px; z-index: 0; border: 5px solid #111;')

            HTML.addRaw(f'SubPage_page_queList', queHTML)

            CSS.setStyles(f'SubPage_page_que_{data["que"]["position"]}', ((f'background', f'#444'), (f'color', f'#F7E163'), (f'border', f'5px solid #F7E163'), (f'borderRadius', f'0px'), (f'zIndex', f'100')))

            glb.currentPosition = data["que"]["position"]

            inp = HTML.add(f'input', _id=f'SubPage_page_queAdd_input', _type=f'text', _style=f'inputMedium %% width: 75%; font-size: 75%;')
            btn = HTML.add(f'button', _nest=f'Play Next', _id=f'SubPage_page_queAdd_playNext', _type=f'button', _style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            btn += HTML.add(f'button', _nest=f'Play Now', _id=f'SubPage_page_queAdd_playNow', _type=f'button', _style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            div = HTML.add(f'div', _nest=f'{btn}', _style=f'width: 25%;')
            HTML.set(f'div', f'SubPage_page_queAdd', _nest=f'{inp}{div}', _style=f'flex %% width: 100%; height: 100%; border-radius: 10px; overflow: hidden;')

            CSS.get(f'SubPage_page_que_{data["que"]["position"]}', f'scrollIntoView')()

            def doAction():
                for track in HTML.get(f'SubPage_page_que_tracks', isClass=True):
                    JS.addEvent(track, playFromQue, "dblclick", isClass=True)
                    JS.addEvent(f'{"_".join(track.id.split("_")[:-1])}_rem_{track.id.split("_")[-1]}', removeFromQue)
                    CSS.onHoverClick(f'{"_".join(track.id.split("_")[:-1])}_rem_{track.id.split("_")[-1]}', f'imgHover', f'imgClick')

                CSS.onHoverFocus(f'SubPage_page_queAdd_input', f'inputHover', f'inputFocus')

                JS.addEvent(f'SubPage_page_queAdd_playNext', playNext)
                CSS.onHoverClick(f'SubPage_page_queAdd_playNext', f'buttonHover', f'buttonClick')

                JS.addEvent(f'SubPage_page_queAdd_playNow', playNow)
                CSS.onHoverClick(f'SubPage_page_queAdd_playNow', f'buttonHover', f'buttonClick')

            JS.afterDelay(doAction, 100)

        def addControls():
            data = WS.dict()["sonos"]

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_buttons', _style=f'divNormal %% flex %% width: 100%; max-width: 550px; margin: 0px; padding: 0px;')

            for action in ["VolumeDown", "Repeat", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "Shuffle", "VolumeUp"]:
                img = HTML.add(f'img', _id=f'SubPage_page_buttons_img_{action}', _style=f'width: 100%;', _custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.add(f'button', _nest=f'{img}', _id=f'SubPage_page_buttons_{action}', _style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.add(f'div', f'SubPage_page_buttons', _nest=f'{btn}', _align=f'center', _style=f'max-width: 55px; margin: 10px auto 10px auto;')

            if data["device"]["playback"] in ["standby", "inactive"]:
                HTML.get(f'SubPage_page_buttons_img_Pause').src = f'docs/assets/Portal/Sonos/Play.png'
                HTML.get(f'SubPage_page_buttons_img_Pause').alt = f'Play'

            HTML.add(f'div', f'SubPage_page_main', _id=f'SubPage_page_volume', _style=f'divNormal %% flex %% width: 90%; max-width: 525px; margin: 0px; padding: 0px; justify-content: center;')

            options = ""
            for option in range(0, 101, int(glb.config["volumeMax"] / 10)):
                options += HTML.add(f'option', _custom=f'value="{option}" label="{option}"')

            HTML.add(f'datalist', f'SubPage_page_volume', _nest=f'{options}', _id=f'SubPage_page_volume_datalist')

            HTML.add(f'input',
                     f'SubPage_page_volume',
                     _id=f'SubPage_page_volume_slider',
                     _type=f'range',
                     _style=f'inputRange %% width: 90%; height: 10px;',
                     _custom=f'min="0" max="{glb.config["volumeMax"]}" value="{data["device"]["volume"]}" list="SubPage_page_volume_datalist"')

            JS.addEvent(f'SubPage_page_buttons_VolumeDown', sonosControl.volumeDown)
            JS.addEvent(f'SubPage_page_buttons_Repeat', sonosControl.toggleRepeat)
            JS.addEvent(f'SubPage_page_buttons_SeekBackward', sonosControl.seekBackward)
            JS.addEvent(f'SubPage_page_buttons_Back', sonosControl.back)
            JS.addEvent(f'SubPage_page_buttons_Pause', sonosControl.togglePlay)
            JS.addEvent(f'SubPage_page_buttons_Next', sonosControl.next)
            JS.addEvent(f'SubPage_page_buttons_VolumeUp', sonosControl.volumeUp)
            JS.addEvent(f'SubPage_page_buttons_SeekForward', sonosControl.seekForward)
            JS.addEvent(f'SubPage_page_buttons_Shuffle', sonosControl.toggleShuffle)
            JS.addEvent(f'SubPage_page_volume_slider', sonosControl.volume, f'input')

            for action in ["VolumeDown", "Repeat", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "Shuffle", "VolumeUp"]:
                CSS.onHoverClick(f'SubPage_page_buttons_{action}', f'imgHover', f'imgClick')

        if glb.currentSub != "Player":
            return None

        if glb.config["disableMaxWidth (experimental)"]:
            CSS.setStyle(f'body', f'max-width', f'')
        else:
            CSS.setStyle(f'body', f'max-width', f'1440px')

        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal')
        HTML.set(f'div', f'SubPage_page_main', _id=f'SubPage_page_media', _style=f'divNormal %% flex %% margin: 0px auto;')

        if glb.config["useAlbumArt"]:
            addAlbumArt()
        else:
            addVideo()

        addControls()
        addQue()

        JS.onResize()

        JS.afterDelay(fastUIRefresh, 250)
        JS.afterDelay(slowUIRefresh, 1000)

    def qr():
        HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_main', _style=f'divNormal %% flex %% justify-content: center;')

        txt = HTML.add(f'h1', _nest=f'Sonos S2 - Android', _style=f'headerBig')
        img = HTML.add(f'img', _id="Image_SonosAndroidQR", _style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="docs/assets/Portal/Sonos/SonosAndroidQR.png" alt="Sonos Android QR"')
        HTML.add(f'div', f'SubPage_page_main', _nest=f'{txt}{img}', _id=f'SubPage_page_main_qrAndroid', _style=f'divNormal %% margin: 15px 50px;')

        txt = HTML.add(f'h1', _nest=f'Sonos S2 - iOS', _style=f'headerBig')
        img = HTML.add(f'img', _id="Image_SonosIosQR", _style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", _custom=f'src="docs/assets/Portal/Sonos/SonosIosQR.png" alt="Sonos iOS QR"')
        HTML.add(f'div', f'SubPage_page_main', _nest=f'{txt}{img}', _id=f'SubPage_page_main_qrIos', _style=f'divNormal %% margin: 15px 50px;')

    def config():
        def editRecord(args):
            def submit(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = HTML.get(f'{args.target.id}')

                if "_" in el.id:
                    mainValue = list(glb.knownConfig)[-1]
                    knownValues = glb.knownConfig[mainValue]
                    value = el.id.split("_")[1]

                else:
                    mainValue = None
                    knownValues = glb.knownConfig
                    value = el.id

                data = el.value.replace(" ", "%20")
                width = el.style.width

                if el.localName == "select":
                    width = f'{float(width.replace("%", "")) - 0.5}%'

                if data == "":
                    data = "%20"

                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'
                html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{data.replace("%20", " ")}</p>'

                if value in knownValues:
                    if knownValues[value] is int:
                        try:
                            data = int(data)
                        except ValueError:
                            JS.popup(f'alert', f'{data} is not a number!\nPlease enter a valid number.')
                            return None

                    elif knownValues[value] is float:
                        try:
                            data = float(data)
                        except ValueError:
                            JS.popup(f'alert', f'{data} is not a number!\nPlease enter a valid number.')
                            return None

                    elif knownValues[value] is list:
                        data = []

                        for i in range(0, int(args.target.name.split("_")[1])):
                            if args.target.item(i).selected is True:
                                data.append(args.target.item(i).value)

                        html = f'<p class="{el.className}" id="{el.id}" style="{styleP}">{", ".join(data).replace(" ", "%20")}</p>'

                glb.config[value] = data
                JS.cache("page_portal_sonos", dumps(glb.config))

                el.outerHTML = html

                CSS.setStyle(f'{el.id}', f'width', f'{width}')
                JS.addEvent(el.id, editRecord, "dblclick")

            el = HTML.get(f'{args.target.id}')
            width = el.style.width
            parantHeight = HTML.get(el.parentElement.id).offsetHeight

            if "_" in el.id:
                value = el.id.split("_")[1]
                mainValue = list(glb.knownConfig)[-1]
                knownValues = glb.knownConfig[mainValue]

            else:
                value = el.id
                mainValue = None
                knownValues = glb.knownConfig

            if el.innerHTML == " ":
                el.innerHTML = ""

            styleInp = f'margin: -1px -1px; padding: 1px 1px 4px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
            styleSlc = f'height: {parantHeight + 4}px; margin: -1px -1px; padding: 1px 1px; background: #333; font-size: 75%; border-radius: 0px; border: 2px solid #111;'
            html = HTML.add(f'input', _id=f'{el.id}', _class=f'{el.className}', _type=f'text', _style=f'inputMedium %% {styleInp}', _custom=f'name="{value}" value="{el.innerHTML}"')

            if value in knownValues:
                if knownValues[value] is bool:
                    if el.innerHTML == "No":
                        glb.config[value] = True
                        JS.cache("page_portal_sonos", dumps(glb.config))

                        el.innerHTML = "Yes"
                        return None

                    glb.config[value] = False
                    JS.cache("page_portal_sonos", dumps(glb.config))

                    el.innerHTML = "No"
                    return None

                elif knownValues[value] is list:
                    optionsHtml = f''

                    for option in glb.optionsList:
                        optionsHtml += HTML.add(f'option', _nest=f'{option}', _custom=f'value="{option}"')

                    html = HTML.add(f'select', _nest=f'{optionsHtml}', _id=f'{el.id}', _class=f'{el.className}', _style=f'selectSmall %% {styleSlc}', _custom=f'name="{value}_{len(glb.optionsList)}" size="1" multiple')

            el.outerHTML = html

            el = HTML.get(f'{el.id}')
            el.style.width = width

            if el.localName == "select":
                el.style.width = f'{float(width.replace("%", "")) + 0.5}%'
                CSS.onHoverFocus(el.id, f'selectHover %% margin-bottom: { - 105 + parantHeight}px;', f'selectFocus %% margin-bottom: { - 105 + parantHeight}px;')
            else:
                CSS.onHoverFocus(el.id, f'inputHover', f'inputFocus')

            JS.addEvent(el.id, submit, "keyup")

        def addMinimal(data):
            def addHeader():
                rowC = 0
                HTML.set(f'div', f'SubPage_page', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

                for header in ["Key", "Value"]:
                    HTML.add(f'p', f'SubPage_page_row{rowC}', _nest=f'{header}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                return rowC

            def addRows(data, rowC):
                knownValues = glb.knownConfig
                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

                HTMLrows = f''
                for key in data:
                    rowC += 1
                    HTMLcols = HTML.add(f'p', _nest=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')
                    value = data[key]

                    if knownValues[key] is int:
                        HTMLcols += HTML.add(f'p', _nest=f'{value}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    elif knownValues[key] is bool:
                        if value:
                            HTMLcols += HTML.add(f'p', _nest=f'Yes', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                        else:
                            HTMLcols += HTML.add(f'p', _nest=f'No', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    elif knownValues[key] is list:
                        HTMLcols += HTML.add(f'p', _nest=f'{", ".join(value)}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    else:
                        HTMLcols += HTML.add(f'p', _nest=f'{value}', _id=f'{key}', _class=f'SubPage_page_keys', _style=f'{styleP}')

                    HTMLrows += HTML.add(f'div', _nest=f'{HTMLcols}', _id=f'SubPage_page_row{rowC}', _align=f'left', _style=f'display: flex;')

                HTML.addRaw(f'SubPage_page', f'{HTMLrows}')

                return rowC

            rowC = addHeader()
            rowC = addRows(data, rowC)

            for item in HTML.get(f'SubPage_page_keys', isClass=True):
                item.style.width = "50%"

            for item in HTML.get(f'SubPage_page_keys', isClass=True):
                if item.id != "":
                    JS.addEvent(item, editRecord, "dblclick", isClass=True)

        addMinimal(glb.config)

    pageSubMap = {"Player": player, "QR": qr, "Config": config}

    HTML.clear(f'SubPage_page')

    setup(args)

    if glb.currentSub == "Player":
        getData()
        JS.afterDelay(pageSubMap[glb.currentSub], 1000)

    else:
        pageSubMap[glb.currentSub]()


def main(args=None, sub=None):
    HTML.set(f'div', f'SubPage', _id=f'SubPage_nav', _align=f'center', _style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.add(f'div', f'SubPage', _id=f'SubPage_page', _align=f'center', _style=f'margin: 10px 10px 10px 0px;')

    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_main', _align=f'left', _style=f'width: 60%')
    HTML.add(f'div', f'SubPage_nav', _id=f'SubPage_nav_options', _align=f'right', _style=f'width: 40%')

    for subPage in glb.subPages:
        HTML.add(f'button', f'SubPage_nav_main', _nest=f'{subPage}', _id=f'SubPage_nav_main_{subPage}', _type=f'button', _style=f'buttonSmall')

    for subPage in glb.subPages:
        JS.addEvent(f'SubPage_nav_main_{subPage}', pageSub)
        CSS.onHoverClick(f'SubPage_nav_main_{subPage}', f'buttonHover', f'buttonClick')

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

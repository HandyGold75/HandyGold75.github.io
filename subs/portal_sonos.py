from WebKit import HTML, CSS, JS, Widget
from WebKit.WebSocket import WS
from json import dumps, loads
from datetime import datetime, timedelta
from traceback import format_exc


class invoke:
    def SO(args=None):
        glb.subPages = ["Player", "QR", "Config"]
        glb.lastUpdate = 0

        getData()


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        for txt in ("position", "device", "track", "que get", "playlist", "ytinfo"):
            WS.send(f'sonos {txt}')

        glb.lastUpdate = datetime.now().timestamp()


class glb:
    subPages = []

    lastUpdate = 0
    ytPlayer = None

    config = {}
    knownConfig = {"volumeMax": int, "seekStep": int, "useAlbumArt": bool, "useQue": bool, "usePlaylist": bool, "disableMaxWidth (experimental)": bool}
    optionsList = []
    currentPosition = ""
    currentQueSize = 0

    videoScolling = False
    skipUiUpdate = True


class sonosControl:
    def enableStream(args=None):
        WS.send(f'sonos enableStream')

    def disableStream(args=None):
        WS.send(f'sonos disableStream')

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

        newPos = datetime.strptime(data["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) + glb.config["seekStep"]
        dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
        dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

        if newPos >= dur:
            newPos = dur

        sonosControl.seek(pos=newPos)
        glb.skipUiUpdate = True

    def seekBackward(args=None):
        data = WS.dict()["sonos"]

        newPos = datetime.strptime(data["position"], "%H:%M:%S")
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

    def clearQue():
        WS.send(f'sonos queClear')

    def addQue(url: str, playNow: bool = False):
        if not url.startswith("https://open.spotify.com/track/") and not url.startswith("https://open.spotify.com/playlist/"):
            return None

        if not playNow:
            WS.send(f'sonos playNext {url}')
        else:
            WS.send(f'sonos playNow {url}')

    def addQueUri(uri: str, playNow: bool = False):
        if not uri.startswith("x-rincon-stream:") and not uri.startswith("x-rincon-cpcontainer:"):
            return None

        if not playNow:
            WS.send(f'sonos playNextUri {uri}')
        else:
            WS.send(f'sonos playNowUri {uri}')

    def useAlbum(args=None):
        glb.config = loads(JS.cache("page_portal_sonos"))
        glb.config["useAlbumArt"] = not glb.config["useAlbumArt"]
        JS.cache("page_portal_sonos", dumps(glb.config))

        main(sub=JS.cache("page_portalSub"))

    def useQue(args=None):
        glb.config = loads(JS.cache("page_portal_sonos"))
        glb.config["useQue"] = not glb.config["useQue"]

        if glb.config["useQue"]:
            glb.config["usePlaylist"] = False

        JS.cache("page_portal_sonos", dumps(glb.config))

        main(sub=JS.cache("page_portalSub"))

    def usePlaylist(args=None):
        glb.config = loads(JS.cache("page_portal_sonos"))
        glb.config["usePlaylist"] = not glb.config["usePlaylist"]

        if glb.config["usePlaylist"]:
            glb.config["useQue"] = False

        JS.cache("page_portal_sonos", dumps(glb.config))

        main(sub=JS.cache("page_portalSub"))


def pageSub(args):
    def setup(args):
        if JS.cache("page_portal_sonos") is None or JS.cache("page_portal_sonos") == "":
            JS.cache("page_portal_sonos", dumps({"volumeMax": 50, "seekStep": 15, "useAlbumArt": False, "useQue": True, "usePlaylist": False, "disableMaxWidth (experimental)": False}))

        glb.config = loads(JS.cache("page_portal_sonos"))

        if not args is None and f'{args.target.id.split("_")[-1]}' in glb.subPages:
            JS.cache("page_portalSub", f'{args.target.id.split("_")[-1]}')

    def player():
        def uiRefresh():
            def position():
                if not JS.cache("page_portalSub") == "Player":
                    return False

                data = WS.dict()["sonos"]

                pos = datetime.strptime(data["position"], "%H:%M:%S")
                pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
                dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
                dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

                posStr = WS.dict()["sonos"]["position"]
                if int(WS.dict()["sonos"]["position"].split(":")[0]) == 0:
                    posStr = ":".join(WS.dict()["sonos"]["position"].split(":")[1:])
                durStr = WS.dict()["sonos"]["track"]["duration"]
                if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                    durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

                try:
                    HTML.setElementRaw("SubPage_page_timeline_position", posStr)
                    HTML.setElementRaw("SubPage_page_timeline_duration", durStr)

                    if not glb.videoScolling:
                        CSS.setAttributes("SubPage_page_timeline_slider", (("max", dur), ("value", pos)))

                    if not glb.config["useAlbumArt"]:
                        newPos = pos + 1
                        oldPos = glb.ytPlayer.getCurrentTime()
                        if oldPos is None:
                            oldPos = 0

                        if not glb.ytPlayer.getDuration() is None and newPos <= glb.ytPlayer.getDuration():
                            if not newPos < oldPos + 1 or not newPos > oldPos - 1:
                                glb.ytPlayer.seekTo(newPos)
                except AttributeError:
                    return None

                WS.onMsg("{\"sonos\": {\"position\":", position, oneTime=True)

            def device():
                if not JS.cache("page_portalSub") == "Player":
                    return False

                data = WS.dict()["sonos"]

                try:
                    if not data["device"]["shuffle"]:
                        CSS.setStyles(f'SubPage_page_buttons_Shuffle', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                    if not data["device"]["repeat"]:
                        CSS.setStyles(f'SubPage_page_buttons_Repeat', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                    if not glb.config["useAlbumArt"]:
                        CSS.setStyles(f'SubPage_page_buttons_Album', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                    if not glb.config["usePlaylist"]:
                        CSS.setStyles(f'SubPage_page_buttons_Playlist', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                    if not glb.config["useQue"]:
                        CSS.setStyles(f'SubPage_page_buttons_Que', ((f'background', f'#222'), (f'border', f'2px solid #222')))

                    if data["device"]["playback"] == "active":
                        CSS.setAttributes("SubPage_page_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Pause.png"), ("alt", "Pause")))
                    elif data["device"]["playback"] in ["standby", "inactive"]:
                        CSS.setAttributes("SubPage_page_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Play.png"), ("alt", "Play")))

                    CSS.setAttribute("SubPage_page_volume_slider", "value", data["device"]["volume"])

                    if not glb.config["useAlbumArt"]:
                        if data["device"]["playback"] == "active" and glb.ytPlayer.getPlayerState() != 1:
                            glb.ytPlayer.playVideo()
                        elif data["device"]["playback"] != "active":
                            glb.ytPlayer.pauseVideo()
                except AttributeError:
                    return None

                WS.onMsg("{\"sonos\": {\"device\":", device, oneTime=True)

            def que():
                if not JS.cache("page_portalSub") == "Player":
                    return False

                data = WS.dict()["sonos"]

                try:
                    addQue()
                    CSS.setStyles(f'SubPage_page_que_{data["que"]["position"]}', ((f'background', f'#444'), (f'color', f'#F7E163'), (f'border', f'5px solid #F7E163'), (f'borderRadius', f'0px'), (f'zIndex ', f'100')))
                    CSS.getAttribute(f'SubPage_page_que_{data["que"]["position"]}', f'scrollIntoView')()
                except AttributeError:
                    return None

                WS.onMsg("{\"sonos\": {\"que\":", que, oneTime=True)

            def track():
                if not JS.cache("page_portalSub") == "Player":
                    return False

                data = WS.dict()["sonos"]

                try:
                    if glb.config["useAlbumArt"]:
                        CSS.setAttributes("Image_AlbumArt", (("src", data["track"]["album_art"]), ("alt", data["track"]["title"])))
                except AttributeError:
                    return None

                WS.onMsg("{\"sonos\": {\"track\":", track, oneTime=True)

            def ytinfo():
                if not JS.cache("page_portalSub") == "Player":
                    return False

                data = WS.dict()["sonos"]

                try:
                    if not glb.config["useAlbumArt"]:
                        glb.ytPlayer.setVolume(0)
                        glb.ytPlayer.mute()

                        if not data["ytinfo"]["id"] in glb.ytPlayer.getVideoUrl():
                            glb.ytPlayer.loadVideoById(f'{data["ytinfo"]["id"]}')
                except AttributeError:
                    return None

                WS.onMsg("{\"sonos\": {\"ytinfo\":", ytinfo, oneTime=True)

            if not JS.cache("page_portalSub") == "Player":
                return False

            if not hasattr(glb.ytPlayer, "setVolume"):
                JS.afterDelay(uiRefresh, 50)
                return None

            WS.onMsg("{\"sonos\": {\"position\":", position, oneTime=True)
            WS.onMsg("{\"sonos\": {\"device\":", device, oneTime=True)

            if glb.config["useQue"]:
                WS.onMsg("{\"sonos\": {\"que\":", que, oneTime=True)
            if glb.config["useAlbumArt"]:
                WS.onMsg("{\"sonos\": {\"track\":", track, oneTime=True)
            else:
                WS.onMsg("{\"sonos\": {\"ytinfo\":", ytinfo, oneTime=True)

            sonosControl.enableStream()

        def activeUIRefresh():
            def controls():
                data = WS.dict()["sonos"]

                try:
                    if data["device"]["shuffle"]:
                        CSS.setStyles(f'SubPage_page_buttons_Shuffle', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                    if data["device"]["repeat"]:
                        CSS.setStyles(f'SubPage_page_buttons_Repeat', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                    if glb.config["useAlbumArt"]:
                        CSS.setStyles(f'SubPage_page_buttons_Album', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                    if glb.config["usePlaylist"]:
                        CSS.setStyles(f'SubPage_page_buttons_Playlist', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                    if glb.config["useQue"]:
                        CSS.setStyles(f'SubPage_page_buttons_Que', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))
                except AttributeError:
                    sonosControl.disableStream()
                    return None

            if not JS.cache("page_portalSub") == "Player":
                sonosControl.disableStream()
                return False

            controls()
            JS.afterDelay(activeUIRefresh, 250)

        def addAlbumArt():
            data = WS.dict()["sonos"]

            HTML.setElement(f'div', f'SubPage_page_media', id=f'SubPage_page_art', style=f'divNormal %% width: 75%; margin: -30px auto 15px auto;')

            img = HTML.genElement(f'img', id="Image_AlbumArt", style="width: 100%; max-width: 69vh; max-height: 69vh; margin: 15px auto -10px auto; user-select:none;", custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"')
            HTML.setElement(f'div', f'SubPage_page_art', nest=f'{img}', id=f'SubPage_page_art_albumArt', style=f'divNormal %% width: 75%;')

            HTML.addElement(f'div', f'SubPage_page_main', id=f'SubPage_page_timeline', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; justify-content: center;')

            pos = datetime.strptime(data["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = WS.dict()["sonos"]["position"]
            if int(WS.dict()["sonos"]["position"].split(":")[0]) == 0:
                posStr = ":".join(WS.dict()["sonos"]["position"].split(":")[1:])

            durStr = WS.dict()["sonos"]["track"]["duration"]
            if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.addElement(f'p', f'SubPage_page_timeline', nest=f'{posStr}', id=f'SubPage_page_timeline_position', style=f'color: #F7E163; width: 10%;')
            HTML.addElement(f'input', f'SubPage_page_timeline', id=f'SubPage_page_timeline_slider', type=f'range', style=f'inputRange %% width: 80%; user-select: none;', custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.addElement(f'p', f'SubPage_page_timeline', nest=f'{durStr}', id=f'SubPage_page_timeline_duration', style=f'color: #F7E163; width: 10%;')

            def doAction():
                def videoScollFalse(args=None):
                    glb.videoScolling = False

                def videoScollTrue(args=None):
                    glb.videoScolling = True

                JS.addEvent(f'SubPage_page_timeline_slider', sonosControl.seek, f'change')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollTrue, f'mousedown')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollFalse, f'mouseup')

            JS.afterDelay(doAction, 50)

        def addVideo():
            data = WS.dict()["sonos"]

            pos = datetime.strptime(data["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            posStr = WS.dict()["sonos"]["position"]
            if int(WS.dict()["sonos"]["position"].split(":")[0]) == 0:
                posStr = ":".join(WS.dict()["sonos"]["position"].split(":")[1:])

            durStr = WS.dict()["sonos"]["track"]["duration"]
            if int(WS.dict()["sonos"]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(WS.dict()["sonos"]["track"]["duration"].split(":")[1:])

            HTML.setElementRaw(f'SubPage_page_media', Widget.ytVideo("SonosYTPlayer"))

            def loadYtPlayer():
                glb.ytPlayer = Widget.ytVideoGetControl("SonosYTPlayer")

            JS.aSync(loadYtPlayer)

            HTML.addElement(f'div', f'SubPage_page_main', id=f'SubPage_page_timeline', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; justify-content: center;')

            HTML.addElement(f'p', f'SubPage_page_timeline', nest=f'{posStr}', id=f'SubPage_page_timeline_position', style=f'color: #F7E163; width: 10%;')
            HTML.addElement(f'input', f'SubPage_page_timeline', id=f'SubPage_page_timeline_slider', type=f'range', style=f'inputRange %% width: 80%; user-select: none;', custom=f'min="0" max="{dur}" value="{pos}"')
            HTML.addElement(f'p', f'SubPage_page_timeline', nest=f'{durStr}', id=f'SubPage_page_timeline_duration', style=f'color: #F7E163; width: 10%;')

            def doAction():
                def videoScollFalse(args=None):
                    glb.videoScolling = False

                def videoScollTrue(args=None):
                    glb.videoScolling = True

                JS.addEvent(f'SubPage_page_timeline_slider', sonosControl.seek, f'change')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollTrue, f'mousedown')
                JS.addEvent(f'SubPage_page_timeline_slider', videoScollFalse, f'mouseup')

            JS.afterDelay(doAction, 50)

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
                    return None

            def playNext(args=None):
                sonosControl.addQue(CSS.getAttribute("SubPage_page_queAdd_input", "value"), False)

            def playNow(args=None):
                sonosControl.addQue(CSS.getAttribute("SubPage_page_queAdd_input", "value"), True)

            data = WS.dict()["sonos"]

            if HTML.getElement("SubPage_page_que") is None:
                que = HTML.genElement(f'div', id=f'SubPage_page_queList', style=f'divNormal %% position: relative; height: 90%; padding: 0px; margin: -5px; border: 5px solid #111; overflow-x: hidden;')
                queAdd = HTML.genElement(f'div', id=f'SubPage_page_queAdd', style=f'divNormal %% position: relative; height: 10%; min-height: 55px; padding: 0px; margin: -5px; border: 5px solid #111;')

                if glb.config["useAlbumArt"]:
                    HTML.addElement(f'div',
                                    f'SubPage_page_media',
                                    id=f'SubPage_page_que',
                                    nest=f'{que}{queAdd}',
                                    style=f'divNormal %% position: relative; width: 50%; height: 37vw; max-height: 540px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')

                else:
                    HTML.addElement(f'div',
                                    f'SubPage_page_media',
                                    id=f'SubPage_page_que',
                                    nest=f'{que}{queAdd}',
                                    style=f'divNormal %% position: relative; width: 25%; height: 36vw; max-height: 545px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')
            else:
                HTML.setElementRaw(f'SubPage_page_queList', "")

            tracks = data["que"]["tracks"]

            queHTML = ""

            for track in tracks:
                img = HTML.genElement(f'img', id=f'SubPage_page_que_{track}_img', style=f'width: 7.5vw; height: 7.5vw; max-width: 50px; max-height: 50px;', align=f'left', custom=f'src="{tracks[track]["album_art_uri"]}" alt="Art"')

                txt = HTML.genElement(f'p', nest=f'{tracks[track]["title"]}', style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', align=f'left')
                remImg = HTML.genElement(f'img', id=f'SubPage_page_que_rem_img_{track}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                remBtn = HTML.genElement(f'button', nest=f'{remImg}', id=f'SubPage_page_que_rem_{track}', style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                rem = HTML.genElement(f'div', nest=f'{remBtn}', align=f'right', style=f'width: 5vw; height: 5vw; max-width: 24px; max-height: 24px; margin: 0px 0px 0px auto;')
                title = HTML.genElement(f'div', nest=f'{txt}{rem}', style=f'flex %% margin: 0px;')

                txt = HTML.genElement(f'p', nest=f'{tracks[track]["creator"]}', style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', align=f'left')
                dur = HTML.genElement(f'p', nest=f'{tracks[track]["duration"][-5:]}', style=f'margin: 0px 0px 0px auto;', align=f'right')
                creator = HTML.genElement(f'div', nest=f'{txt}{dur}', style=f'flex %% font-size: 75%; margin: 0px;')

                txtDiv = HTML.genElement(f'div', nest=f'{title}{creator}', id=f'SubPage_page_que_{track}_txt', style=f'width: 90%; margin: auto 5px;')

                queHTML += HTML.genElement(f'div',
                                           nest=f'{img}{txtDiv}',
                                           id=f'SubPage_page_que_{track}',
                                           clas=f'SubPage_page_que_tracks',
                                           style=f'divNormal %% flex %% height: 7.5vw; max-height: 50px; position: relative; margin: -5px; z-index: 0; border: 5px solid #111;')

            HTML.addElementRaw(f'SubPage_page_queList', queHTML)

            inp = HTML.genElement(f'input', id=f'SubPage_page_queAdd_input', type=f'text', style=f'inputMedium %% width: 75%; font-size: 75%;', custom=f'placeholder="Spotify Sharelink"')
            btn = HTML.genElement(f'button', nest=f'Play Next', id=f'SubPage_page_queAdd_playNext', type=f'button', style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            btn += HTML.genElement(f'button', nest=f'Play Now', id=f'SubPage_page_queAdd_playNow', type=f'button', style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            div = HTML.genElement(f'div', nest=f'{btn}', style=f'width: 25%;')
            HTML.setElement(f'div', f'SubPage_page_queAdd', nest=f'{inp}{div}', style=f'flex %% width: 100%; height: 100%; border-radius: 10px; overflow: hidden;')

            if data["que"]["position"] != -1:
                CSS.setStyles(f'SubPage_page_que_{data["que"]["position"]}', ((f'background', f'#444'), (f'color', f'#F7E163'), (f'border', f'5px solid #F7E163'), (f'borderRadius', f'0px'), (f'zIndex', f'100')))
                CSS.getAttribute(f'SubPage_page_que_{data["que"]["position"]}', f'scrollIntoView')()

            def doAction():
                for track in HTML.getElements("SubPage_page_que_tracks"):
                    JS.addEvent(track, playFromQue, "dblclick", isClass=True)
                    JS.addEvent(f'{"_".join(track.id.split("_")[:-1])}_rem_{track.id.split("_")[-1]}', removeFromQue)
                    CSS.onHoverClick(f'{"_".join(track.id.split("_")[:-1])}_rem_{track.id.split("_")[-1]}', f'imgHover', f'imgClick')

                CSS.onHoverFocus("SubPage_page_queAdd_input", "inputHover", "inputFocus")

                JS.addEvent("SubPage_page_queAdd_playNext", playNext)
                CSS.onHoverClick("SubPage_page_queAdd_playNext", "buttonHover", "buttonClick")

                JS.addEvent("SubPage_page_queAdd_playNow", playNow)
                CSS.onHoverClick("SubPage_page_queAdd_playNow", "buttonHover", "buttonClick")

            JS.afterDelay(doAction, 50)

        def addPlaylist():
            def playPlaylist(args):
                el = args.target

                for i in range(0, 4):
                    if el.id == "":
                        el = el.parentElement
                        continue

                    if el.id.split("_")[-1] in ["txt", "img"]:
                        el = el.parentElement
                        continue

                    data = WS.dict()["sonos"]["playlists"]
                    sonosControl.clearQue()
                    sonosControl.addQueUri(f'{data[el.id.split("_")[-1]]["uri"]}', True)

                    return None

            def playNextUri(args=None):
                sonosControl.addQueUri(CSS.getAttribute("SubPage_page_playlistAdd_input", "value"), False)

            def playNowUri(args=None):
                sonosControl.addQueUri(CSS.getAttribute("SubPage_page_playlistAdd_input", "value"), True)

            data = WS.dict()["sonos"]

            if HTML.getElement("SubPage_page_playlist") is None:
                que = HTML.genElement(f'div', id=f'SubPage_page_playlistList', style=f'divNormal %% position: relative; height: 90%; padding: 0px; margin: -5px; border: 5px solid #111; overflow-x: hidden;')
                queAdd = HTML.genElement(f'div', id=f'SubPage_page_playlistAdd', style=f'divNormal %% position: relative; height: 10%; min-height: 55px; padding: 0px; margin: -5px; border: 5px solid #111;')

                if glb.config["useAlbumArt"]:
                    HTML.addElement(f'div',
                                    f'SubPage_page_media',
                                    id=f'SubPage_page_playlist',
                                    nest=f'{que}{queAdd}',
                                    style=f'divNormal %% position: relative; width: 50%; height: 37vw; max-height: 540px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')

                else:
                    HTML.addElement(f'div',
                                    f'SubPage_page_media',
                                    id=f'SubPage_page_playlist',
                                    nest=f'{que}{queAdd}',
                                    style=f'divNormal %% position: relative; width: 25%; height: 36vw; max-height: 545px; padding: 0px; margin: 0px -2.25% 0px auto; border: 5px solid #111;')
            else:
                HTML.setElementRaw(f'SubPage_page_playlistList', "")

            playlists = data["playlists"]

            queHTML = ""

            for playlist in reversed(playlists):
                if playlists[playlist]["album_art"] is None:
                    img = HTML.genElement(f'img', id=f'SubPage_page_playlist_{playlist}_img', style=f'width: 7.5vw; height: 7.5vw; max-width: 50px; max-height: 50px;', align=f'left', custom=f'src="docs/assets/Portal/Sonos/Missing.png" alt="Art"')
                else:
                    img = HTML.genElement(f'img', id=f'SubPage_page_playlist_{playlist}_img', style=f'width: 7.5vw; height: 7.5vw; max-width: 50px; max-height: 50px;', align=f'left', custom=f'src="{playlists[playlist]["album_art"]}" alt="Art"')

                txt = HTML.genElement(f'p', nest=f'{playlist}', style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', align=f'left')
                title = HTML.genElement(f'div', nest=f'{txt}', style=f'flex %% margin: 0px;')

                txt = HTML.genElement(f'p', nest=f'{playlists[playlist]["description"]}', style=f'margin: 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;', align=f'left')
                creator = HTML.genElement(f'div', nest=f'{txt}', style=f'flex %% font-size: 75%; margin: 0px;')

                txtDiv = HTML.genElement(f'div', nest=f'{title}{creator}', id=f'SubPage_page_playlist_{playlist}_txt', style=f'width: 90%; margin: auto 5px;')

                queHTML += HTML.genElement(f'div',
                                           nest=f'{img}{txtDiv}',
                                           id=f'SubPage_page_playlist_{playlist}',
                                           clas=f'SubPage_page_playlist_playlists',
                                           style=f'divNormal %% flex %% height: 7.5vw; max-height: 50px; position: relative; margin: -5px; z-index: 0; border: 5px solid #111;')

            HTML.addElementRaw(f'SubPage_page_playlistList', queHTML)

            CSS.setStyles(f'SubPage_page_playlist_{data["que"]["position"]}', ((f'background', f'#444'), (f'color', f'#F7E163'), (f'border', f'5px solid #F7E163'), (f'borderRadius', f'0px'), (f'zIndex', f'100')))

            inp = HTML.genElement(f'input', id=f'SubPage_page_playlistAdd_input', type=f'text', style=f'inputMedium %% width: 75%; font-size: 75%;', custom=f'placeholder="Sonos URI"')
            btn = HTML.genElement(f'button', nest=f'Play Next', id=f'SubPage_page_playlistAdd_playNext', type=f'button', style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            btn += HTML.genElement(f'button', nest=f'Play Now', id=f'SubPage_page_playlistAdd_playNow', type=f'button', style=f'buttonSmall %% width: 100%; margin: 0px; white-space: nowrap;')
            div = HTML.genElement(f'div', nest=f'{btn}', style=f'width: 25%;')
            HTML.setElement(f'div', f'SubPage_page_playlistAdd', nest=f'{inp}{div}', style=f'flex %% width: 100%; height: 100%; border-radius: 10px; overflow: hidden;')

            def doAction():
                for track in HTML.getElements("SubPage_page_playlist_playlists"):
                    JS.addEvent(track, playPlaylist, "dblclick", isClass=True)

                CSS.onHoverFocus(f'SubPage_page_playlistAdd_input', f'inputHover', f'inputFocus')

                JS.addEvent(f'SubPage_page_playlistAdd_playNext', playNextUri)
                CSS.onHoverClick(f'SubPage_page_playlistAdd_playNext', f'buttonHover', f'buttonClick')

                JS.addEvent(f'SubPage_page_playlistAdd_playNow', playNowUri)
                CSS.onHoverClick(f'SubPage_page_playlistAdd_playNow', f'buttonHover', f'buttonClick')

            JS.afterDelay(doAction, 50)

        def addControls():
            data = WS.dict()["sonos"]

            HTML.addElement(f'div', f'SubPage_page_main', id=f'SubPage_page_buttons', style=f'divNormal %% flex %% margin: 0px; padding: 0px;')
            HTML.addElement(f'div', f'SubPage_page_buttons', id=f'SubPage_page_buttons_left', style=f'divNormal %% flex %% width: 15%; margin: 0px; padding: 0px;')
            HTML.addElement(f'div', f'SubPage_page_buttons', id=f'SubPage_page_buttons_middle', style=f'divNormal %% flex %% width: 70%; margin: 0px; padding: 0px;')
            HTML.addElement(f'div', f'SubPage_page_buttons', id=f'SubPage_page_buttons_right', style=f'divNormal %% flex %% width: 15%; margin: 0px; padding: 0px;')

            leftActions = ["Repeat", "Shuffle"]
            for i, action in enumerate(leftActions):
                margin = " margin: 1%;"
                if i >= len(leftActions) - 1:
                    margin = " margin: 1% auto 1% 1%;"

                img = HTML.genElement(f'img', id=f'SubPage_page_buttons_img_{action}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.genElement(f'button', nest=f'{img}', id=f'SubPage_page_buttons_{action}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.addElement(f'div', f'SubPage_page_buttons_left', nest=f'{btn}', align=f'center', style=f'max-width: 55px;{margin}')

            midActions = ["VolumeDown", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "VolumeUp"]
            for i, action in enumerate(midActions):
                margin = " margin: 1%;"
                if i < 1:
                    margin = " margin: 1% 1% 1% auto;"
                elif i >= len(midActions) - 1:
                    margin = " margin: 1% auto 1% 1%;"

                img = HTML.genElement(f'img', id=f'SubPage_page_buttons_img_{action}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.genElement(f'button', nest=f'{img}', id=f'SubPage_page_buttons_{action}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.addElement(f'div', f'SubPage_page_buttons_middle', nest=f'{btn}', align=f'center', style=f'max-width: 55px;{margin}')

            rightActions = ["Album", "Playlist", "Que"]
            for i, action in enumerate(rightActions):
                margin = " margin: 1%;"
                if i < 1:
                    margin = " margin: 1% 1% 1% auto;"

                img = HTML.genElement(f'img', id=f'SubPage_page_buttons_img_{action}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/{action}.png" alt="{action}"')
                btn = HTML.genElement(f'button', nest=f'{img}', id=f'SubPage_page_buttons_{action}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                HTML.addElement(f'div', f'SubPage_page_buttons_right', nest=f'{btn}', align=f'center', style=f'max-width: 55px;{margin}')

            if data["device"]["playback"] in ["standby", "inactive"]:
                CSS.setAttributes("SubPage_page_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Play.png"), ("alt", "Play")))

            HTML.addElement(f'div', f'SubPage_page_main', id=f'SubPage_page_volume', style=f'divNormal %% flex %% width: 50%; margin: 0px; padding: 0px; justify-content: center;')

            options = ""
            for option in range(0, 101, int(glb.config["volumeMax"] / 10)):
                options += HTML.genElement(f'option', custom=f'value="{option}" label="{option}"')

            HTML.addElement(f'datalist', f'SubPage_page_volume', nest=f'{options}', id=f'SubPage_page_volume_datalist')

            HTML.addElement(f'input',
                            f'SubPage_page_volume',
                            id=f'SubPage_page_volume_slider',
                            type=f'range',
                            style=f'inputRange %% width: 90%; height: 10px;',
                            custom=f'min="0" max="{glb.config["volumeMax"]}" value="{data["device"]["volume"]}" list="SubPage_page_volume_datalist"')

            fmap = {
                "Repeat": sonosControl.toggleRepeat,
                "Shuffle": sonosControl.toggleShuffle,
                "VolumeDown": sonosControl.volumeDown,
                "SeekBackward": sonosControl.seekBackward,
                "Back": sonosControl.back,
                "Pause": sonosControl.togglePlay,
                "Next": sonosControl.next,
                "SeekForward": sonosControl.seekForward,
                "VolumeUp": sonosControl.volumeUp,
                "Album": sonosControl.useAlbum,
                "Playlist": sonosControl.usePlaylist,
                "Que": sonosControl.useQue
            }

            for action in fmap:
                JS.addEvent(f'SubPage_page_buttons_{action}', fmap[action])
                CSS.onHoverClick(f'SubPage_page_buttons_{action}', f'imgHover', f'imgClick')

            JS.addEvent(f'SubPage_page_volume_slider', sonosControl.volume, f'input')

        if JS.cache("page_portalSub") != "Player":
            return None

        if glb.config["disableMaxWidth (experimental)"]:
            CSS.setStyle(f'body', f'max-width', f'')
        else:
            CSS.setStyle(f'body', f'max-width', f'1440px')

        HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_main', style=f'divNormal')
        HTML.setElement(f'div', f'SubPage_page_main', id=f'SubPage_page_media', style=f'divNormal %% flex %% margin: 0px auto;')

        if glb.config["useAlbumArt"]:
            addAlbumArt()
        else:
            addVideo()

        addControls()

        if glb.config["useQue"]:
            addQue()
        elif glb.config["usePlaylist"]:
            addPlaylist()

        JS.onResize()

        JS.afterDelay(uiRefresh, 50)
        JS.afterDelay(activeUIRefresh, 50)

    def qr():
        HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_main', style=f'divNormal %% flex %% justify-content: center;')

        txt = HTML.genElement(f'h1', nest=f'Sonos S2 - Android', style=f'headerBig')
        img = HTML.genElement(f'img', id="Image_SonosAndroidQR", style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", custom=f'src="docs/assets/Portal/Sonos/SonosAndroidQR.png" alt="Sonos Android QR"')
        HTML.addElement(f'div', f'SubPage_page_main', nest=f'{txt}{img}', id=f'SubPage_page_main_qrAndroid', style=f'divNormal %% margin: 15px 50px;')

        txt = HTML.genElement(f'h1', nest=f'Sonos S2 - iOS', style=f'headerBig')
        img = HTML.genElement(f'img', id="Image_SonosIosQR", style="width: 100%; max-width: 75vh; max-height: 75vh; margin: 15px auto -10px auto; user-select:none;", custom=f'src="docs/assets/Portal/Sonos/SonosIosQR.png" alt="Sonos iOS QR"')
        HTML.addElement(f'div', f'SubPage_page_main', nest=f'{txt}{img}', id=f'SubPage_page_main_qrIos', style=f'divNormal %% margin: 15px 50px;')

    def config():
        def editRecord(args):
            def submit(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = HTML.getElement(args.target.id)

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

            el = HTML.getElement(args.target.id)
            width = el.style.width
            parantHeight = CSS.getAttribute(el.parentElement.id, "offsetHeight")

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
            html = HTML.genElement(f'input', id=f'{el.id}', clas=f'{el.className}', type=f'text', style=f'inputMedium %% {styleInp}', custom=f'name="{value}" value="{el.innerHTML}"')

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
                        optionsHtml += HTML.genElement(f'option', nest=f'{option}', custom=f'value="{option}"')

                    html = HTML.genElement(f'select', nest=f'{optionsHtml}', id=f'{el.id}', clas=f'{el.className}', style=f'selectSmall %% {styleSlc}', custom=f'name="{value}_{len(glb.optionsList)}" size="1" multiple')

            el.outerHTML = html

            el = HTML.getElement(el.id)
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
                HTML.setElement(f'div', f'SubPage_page', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 100%; word-wrap: break-word; background: #1F1F1F; color: #44F; font-weight: bold;'

                for header in ["Key", "Value"]:
                    HTML.addElement(f'p', f'SubPage_page_row{rowC}', nest=f'{header}', clas=f'SubPage_page_keys', style=f'{styleP}')

                return rowC

            def addRows(data, rowC):
                knownValues = glb.knownConfig
                styleP = f'margin: -1px -1px; padding: 0px 1px; border: 2px solid #111; text-align: center; font-size: 75%; word-wrap: break-word; background: #1F1F1F; color: #44F;'

                HTMLrows = f''
                for key in data:
                    rowC += 1
                    HTMLcols = HTML.genElement(f'p', nest=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')
                    value = data[key]

                    if knownValues[key] is int:
                        HTMLcols += HTML.genElement(f'p', nest=f'{value}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    elif knownValues[key] is bool:
                        if value:
                            HTMLcols += HTML.genElement(f'p', nest=f'Yes', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                        else:
                            HTMLcols += HTML.genElement(f'p', nest=f'No', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    elif knownValues[key] is list:
                        HTMLcols += HTML.genElement(f'p', nest=f'{", ".join(value)}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    else:
                        HTMLcols += HTML.genElement(f'p', nest=f'{value}', id=f'{key}', clas=f'SubPage_page_keys', style=f'{styleP}')

                    HTMLrows += HTML.genElement(f'div', nest=f'{HTMLcols}', id=f'SubPage_page_row{rowC}', align=f'left', style=f'display: flex;')

                HTML.addElementRaw(f'SubPage_page', f'{HTMLrows}')

                return rowC

            rowC = addHeader()
            rowC = addRows(data, rowC)

            for item in HTML.getElements("SubPage_page_keys"):
                item.style.width = "50%"

            for item in HTML.getElements("SubPage_page_keys"):
                if item.id != "":
                    JS.addEvent(item, editRecord, "dblclick", isClass=True)

        addMinimal(glb.config)

    pageSubMap = {"Player": player, "QR": qr, "Config": config}

    HTML.clrElement(f'SubPage_page')

    setup(args)

    if JS.cache("page_portalSub") == "Player":
        getData()
        JS.afterDelay(pageSubMap[JS.cache("page_portalSub")], 500)

    else:
        pageSubMap[JS.cache("page_portalSub")]()


def main(args=None, sub=None):
    HTML.setElement(f'div', f'SubPage', id=f'SubPage_nav', align=f'center', style=f'width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;')
    HTML.addElement(f'div', f'SubPage', id=f'SubPage_page', align=f'center', style=f'margin: 10px 10px 10px 0px;')

    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_main', align=f'left', style=f'width: 60%')
    HTML.addElement(f'div', f'SubPage_nav', id=f'SubPage_nav_options', align=f'right', style=f'width: 40%')

    for subPage in glb.subPages:
        HTML.addElement(f'button', f'SubPage_nav_main', nest=f'{subPage}', id=f'SubPage_nav_main_{subPage}', type=f'button', style=f'buttonSmall')

    for subPage in glb.subPages:
        JS.addEvent(f'SubPage_nav_main_{subPage}', pageSub)
        CSS.onHoverClick(f'SubPage_nav_main_{subPage}', f'buttonHover', f'buttonClick')

    if sub is not None:
        JS.cache("page_portalSub", f'{sub}')
        pageSub(args)

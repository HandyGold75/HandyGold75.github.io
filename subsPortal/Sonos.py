from datetime import datetime
from json import dumps, loads

from WebKit import CSS, HTML, JS, WS, PortalPage, Widget


class sonos(PortalPage):
    def __init__(self):
        super().__init__()

        self.mainComReadCommands = ["position", "device", "track", "que get", "playlist", "ytinfo"]

        self.onDeload = self.comDisableStream
        self.onSubPageLoad = self.loadSubPage

        self.ytPlayer = None
        self.videoScolling = False
        self.dataStreamState = False
        # self.currentPosition = ""
        # self.currentQueSize = 0

    def loadSubPage(self):
        getattr(self, f'{JS.cache("portalSubPage").lower()}Page')()

    def doOnResize(self):
        configSonos = self.getCachedConfig()
        if configSonos["useQue"]:
            rightId = "portalSubPage_que"
        elif configSonos["usePlaylist"]:
            rightId = "portalSubPage_playlist"
        else:
            rightId = None
        if configSonos["useAlbumArt"]:
            leftId = "portalSubPage_art"
        else:
            leftId = "portalSubPage_vid"

        if JS.getWindow().innerWidth < 500:
            if JS.cache("portalSubPage") == "Player":
                if configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyle(rightId, "height", f'{CSS.getAttribute("Image_AlbumArt", "offsetHeight")}px')
                elif not configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyles(leftId, (("width", "0%"), ("display", "none")))
                    CSS.setStyle(rightId, "width", "95%")
                    CSS.setStyle(rightId, "height", "300px")
                else:
                    CSS.setStyles(leftId, (("width", "100%"), ("display", "")))

                if not rightId is None:
                    CSS.setStyle(f"{rightId}List", "height", f'{CSS.getAttribute(rightId, "clientHeight") - 62}px')
                    CSS.setStyle(f"{rightId}Add_playNext", "margin", "3px 0px 2px 0px")
                    CSS.setStyle(f"{rightId}Add_playNow", "margin", "2px 0px 3px 0px")
                    CSS.setStyle(rightId, "fontSize", "175%")

                if configSonos["useQue"] and not HTML.getElement(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}') is None:
                    CSS.getAttribute(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}', "scrollIntoView")()

            elif JS.cache("portalSubPage") == "QR":
                CSS.setStyle("Header_SonosAndroidQR", "fontSize", "150%")
                CSS.setStyle("Header_SonosIosQR", "fontSize", "150%")

        elif JS.getWindow().innerWidth < 1000:
            if JS.cache("portalSubPage") == "Player":
                if configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyle(rightId, "height", f'{CSS.getAttribute("Image_AlbumArt", "offsetHeight")}px')
                elif not configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyles(leftId, (("width", "50%"), ("display", "")))
                    CSS.setStyle(rightId, "width", "50%")
                    CSS.setStyle(rightId, "height", f'{CSS.getAttribute("SonosYTPlayer", "offsetHeight")}px')
                else:
                    CSS.setStyles(leftId, (("width", "100%"), ("display", "")))

                if not rightId is None:
                    CSS.setStyle(f"{rightId}List", "height", f'{CSS.getAttribute(rightId, "clientHeight") - 62}px')
                    CSS.setStyle(f"{rightId}Add_playNext", "margin", "3px 0px 2px 0px")
                    CSS.setStyle(f"{rightId}Add_playNow", "margin", "2px 0px 3px 0px")
                    CSS.setStyle(rightId, "fontSize", "125%")

                if configSonos["useQue"] and not HTML.getElement(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}') is None:
                    CSS.getAttribute(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}', "scrollIntoView")()

            elif JS.cache("portalSubPage") == "QR":
                CSS.setStyle("Header_SonosAndroidQR", "fontSize", "175%")
                CSS.setStyle("Header_SonosIosQR", "fontSize", "175%")

        else:
            if JS.cache("portalSubPage") == "Player":
                if configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyle(rightId, "height", f'{CSS.getAttribute("Image_AlbumArt", "offsetHeight")}px')
                elif not configSonos["useAlbumArt"] and not rightId is None:
                    CSS.setStyles(leftId, (("width", "75%"), ("display", "")))
                    CSS.setStyle(rightId, "width", "25%")
                    CSS.setStyle(rightId, "height", f'{CSS.getAttribute("SonosYTPlayer", "offsetHeight")}px')
                else:
                    CSS.setStyles(leftId, (("width", "100%"), ("display", "")))

                if not rightId is None:
                    CSS.setStyle(f"{rightId}List", "height", f'{CSS.getAttribute(rightId, "clientHeight") - 62}px')
                    CSS.setStyle(f"{rightId}Add_playNext", "margin", "2.5px 0px")
                    CSS.setStyle(f"{rightId}Add_playNow", "margin", "2.5px 0px")
                    CSS.setStyle(rightId, "fontSize", "100%")

                if configSonos["useQue"] and not HTML.getElement(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}') is None:
                    CSS.getAttribute(f'portalSubPage_que_{WS.dict()[self.mainCom]["que"]["position"]}', "scrollIntoView")()

            elif JS.cache("portalSubPage") == "QR":
                CSS.setStyle("Header_SonosAndroidQR", "fontSize", "200%")
                CSS.setStyle("Header_SonosIosQR", "fontSize", "200%")

    def playerPage(self, firstRun: bool = True):
        if firstRun:
            pass

        configSonos = self.getCachedConfig()
        if configSonos["useQue"] and configSonos["usePlaylist"]:
            self.setCachedConfig("usePlaylist", False)

        div = HTML.genElement("div", id="portalSubPage_media", style=f"divNormalNoEdge %% flex %% margin: 5px auto; border-radius: 0px; overflow: hidden;")
        HTML.setElement("div", "portalSubPage", nest=div, id="portalSubPage_main", style="divNormal")

        if configSonos["useAlbumArt"]:
            self.addAlbumArt()
        else:
            self.addVideo()
        self.addControls()
        if configSonos["useQue"]:
            self.addQue()
        elif configSonos["usePlaylist"]:
            self.addPlaylist()

        JS.afterDelay(self.uiRefresh, delay=50)

        self.onResize = self.doOnResize
        JS.afterDelay(self._onResize, delay=50)

    def uiRefresh(self):
        def position(self):
            if not JS.cache("portalSubPage") == "Player":
                return None

            data = WS.dict()[self.mainCom]
            configSonos = self.getCachedConfig()

            pos = datetime.strptime(data["position"], "%H:%M:%S")
            pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
            dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second
            posStr = WS.dict()[self.mainCom]["position"]
            if int(WS.dict()[self.mainCom]["position"].split(":")[0]) == 0:
                posStr = ":".join(WS.dict()[self.mainCom]["position"].split(":")[1:])
            durStr = WS.dict()[self.mainCom]["track"]["duration"]
            if int(WS.dict()[self.mainCom]["track"]["duration"].split(":")[0]) == 0:
                durStr = ":".join(WS.dict()[self.mainCom]["track"]["duration"].split(":")[1:])

            try:
                HTML.setElementRaw("portalSubPage_timeline_position", posStr)
                HTML.setElementRaw("portalSubPage_timeline_duration", durStr)
                if not self.videoScolling:
                    CSS.setAttributes("portalSubPage_timeline_slider", (("max", dur), ("value", pos)))

                if not configSonos["useAlbumArt"]:
                    newPos = pos + 1
                    oldPos = self.ytPlayer.getCurrentTime()
                    if oldPos is None:
                        oldPos = 0

                    if not self.ytPlayer.getDuration() is None and newPos <= self.ytPlayer.getDuration():
                        if not newPos < oldPos + 1 or not newPos > oldPos - 1:
                            self.ytPlayer.seekTo(newPos)
            except AttributeError:
                return None
            WS.onMsg('{"' + self.mainCom + '": {"position":', position, (self,), oneTime=True)

        def device(self):
            if not JS.cache("portalSubPage") == "Player":
                return None

            data = WS.dict()[self.mainCom]
            configSonos = self.getCachedConfig()

            try:
                JS.clearEvents("portalSubPage_buttons_Repeat")
                JS.addEvent(f"portalSubPage_buttons_Repeat", self.comToggleRepeat)
                if data["device"]["repeat"]:
                    CSS.setStyles("portalSubPage_buttons_Repeat", (("background", "#444"), ("border", "3px solid #FBDF56")))
                    CSS.onClick("portalSubPage_buttons_Repeat", "imgClick")
                else:
                    CSS.setStyles("portalSubPage_buttons_Repeat", (("background", "#222"), ("border", "2px solid #222")))
                    CSS.onHoverClick(f"portalSubPage_buttons_Repeat", "imgHover", "imgClick")

                JS.clearEvents("portalSubPage_buttons_Shuffle")
                JS.addEvent(f"portalSubPage_buttons_Shuffle", self.comToggleShuffle)
                if data["device"]["shuffle"]:
                    CSS.setStyles("portalSubPage_buttons_Shuffle", (("background", "#444"), ("border", "3px solid #FBDF56")))
                    CSS.onClick("portalSubPage_buttons_Shuffle", "imgClick")
                else:
                    CSS.setStyles("portalSubPage_buttons_Shuffle", (("background", "#222"), ("border", "2px solid #222")))
                    CSS.onHoverClick(f"portalSubPage_buttons_Shuffle", "imgHover", "imgClick")

                if data["device"]["playback"] == "active":
                    CSS.setAttributes("portalSubPage_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Pause.svg"), ("alt", "Pause")))
                elif data["device"]["playback"] in ["standby", "inactive"]:
                    CSS.setAttributes("portalSubPage_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Play.svg"), ("alt", "Play")))

                CSS.setAttribute("portalSubPage_volume_slider", "value", data["device"]["volume"])

                if not configSonos["useAlbumArt"]:
                    if data["device"]["playback"] == "active" and self.ytPlayer.getPlayerState() != 1:
                        self.ytPlayer.playVideo()
                    elif data["device"]["playback"] != "active":
                        self.ytPlayer.pauseVideo()
            except AttributeError:
                return None
            WS.onMsg('{"' + self.mainCom + '": {"device":', device, (self,), oneTime=True)

        def que(self):
            if not JS.cache("portalSubPage") == "Player":
                return None

            data = WS.dict()[self.mainCom]

            try:
                self.addQue()
                CSS.setStyles(f'portalSubPage_que_{data["que"]["position"]}', (("background", "#444"), ("color", "#F7E163"), ("border", "5px solid #F7E163"), ("borderRadius", "0px"), ("zIndex", "100")))
                CSS.getAttribute(f'portalSubPage_que_{data["que"]["position"]}', "scrollIntoView")()
            except AttributeError:
                return None
            WS.onMsg('{"' + self.mainCom + '": {"que":', que, (self,), oneTime=True)

        def track(self):
            if not JS.cache("portalSubPage") == "Player":
                return None

            data = WS.dict()[self.mainCom]
            configSonos = self.getCachedConfig()

            try:
                if configSonos["useAlbumArt"]:
                    CSS.setAttributes("Image_AlbumArt", (("src", data["track"]["album_art"]), ("alt", data["track"]["title"])))
            except AttributeError:
                return None
            WS.onMsg('{"' + self.mainCom + '": {"track":', track, (self,), oneTime=True)

        def ytinfo(self):
            if not JS.cache("portalSubPage") == "Player":
                return None

            data = WS.dict()[self.mainCom]
            configSonos = self.getCachedConfig()

            try:
                if not configSonos["useAlbumArt"]:
                    self.ytPlayer.setVolume(0)
                    self.ytPlayer.mute()
                    if not data["ytinfo"]["id"] in self.ytPlayer.getVideoUrl():
                        self.ytPlayer.loadVideoById(f'{data["ytinfo"]["id"]}')
            except AttributeError:
                return None
            WS.onMsg('{"' + self.mainCom + '": {"ytinfo":', ytinfo, (self,), oneTime=True)

        if not JS.cache("portalSubPage") == "Player":
            return None
        if not hasattr(self.ytPlayer, "setVolume"):
            JS.afterDelay(self.uiRefresh, delay=50)
            return None

        WS.onMsg('{"' + self.mainCom + '": {"position":', position, (self,), oneTime=True)
        WS.onMsg('{"' + self.mainCom + '": {"device":', device, (self,), oneTime=True)

        configSonos = self.getCachedConfig()
        if configSonos["useQue"]:
            WS.onMsg('{"' + self.mainCom + '": {"que":', que, (self,), oneTime=True)
        if configSonos["useAlbumArt"]:
            WS.onMsg('{"' + self.mainCom + '": {"track":', track, (self,), oneTime=True)
        else:
            WS.onMsg('{"' + self.mainCom + '": {"ytinfo":', ytinfo, (self,), oneTime=True)

        self.comEnableStream()

    def addAlbumArt(self):
        data = WS.dict()[self.mainCom]

        artImg = HTML.genElement(
            "img", id="Image_AlbumArt", style="max-width: 96%; min-height: 300px; max-height: 500px; margin: auto 1%; border-radius: 10px; user-select: none;", custom=f'src="{data["track"]["album_art"]}" alt="{data["track"]["title"]}"'
        )
        HTML.setElement("div", "portalSubPage_media", nest=artImg, id="portalSubPage_art", style="divNormalNoEdge %% width: 50%; margin: auto;")
        self.addTimeline()

    def addVideo(self):
        vidDiv = HTML.genElement("div", nest=Widget.ytVideo("SonosYTPlayer"), id="portalSubPage_vid", style="divNormalNoEdge %% width: 75%; margin: auto;")
        HTML.setElementRaw("portalSubPage_media", vidDiv)
        self.addTimeline()

        def loadYtPlayer(self):
            self.ytPlayer = Widget.ytVideoGetControl("SonosYTPlayer")

        JS.aSync(loadYtPlayer, (self,))

    def addTimeline(self):
        data = WS.dict()[self.mainCom]

        pos = datetime.strptime(data["position"], "%H:%M:%S")
        pos = (pos.hour * 3600) + (pos.minute * 60) + pos.second
        dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
        dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second
        posStr = WS.dict()[self.mainCom]["position"]
        if int(WS.dict()[self.mainCom]["position"].split(":")[0]) == 0:
            posStr = ":".join(WS.dict()[self.mainCom]["position"].split(":")[1:])
        durStr = WS.dict()[self.mainCom]["track"]["duration"]
        if int(WS.dict()[self.mainCom]["track"]["duration"].split(":")[0]) == 0:
            durStr = ":".join(WS.dict()[self.mainCom]["track"]["duration"].split(":")[1:])

        timeline = HTML.genElement("p", nest=posStr, id="portalSubPage_timeline_position", style="color: #F7E163; width: 10%; margin: 16px 0px;")
        timeline += HTML.genElement("input", id="portalSubPage_timeline_slider", type="range", style="inputRange %% width: 80%; user-select: none;", custom=f'min="0" max="{dur}" value="{pos}"')
        timeline += HTML.genElement("p", nest=durStr, id="portalSubPage_timeline_duration", style="color: #F7E163; width: 10%; margin: 16px 0px;")

        HTML.addElement("div", "portalSubPage_main", nest=timeline, id="portalSubPage_timeline", style="divNormalNoEdge %% flex %% width: 100%; margin: 5px auto; overflow: hidden;")

        def doAction(self):
            JS.addEvent("portalSubPage_timeline_slider", self.comSeek, action="change", includeElement=True)
            JS.addEvent("portalSubPage_timeline_slider", setattr, (self, "videoScolling", True), action="mousedown")
            JS.addEvent("portalSubPage_timeline_slider", setattr, (self, "videoScolling", False), action="mouseup")

        JS.afterDelay(doAction, (self,), delay=50)

    def addQue(self):
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

                self.comSetQue(el.id.split("_")[-1])
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

                self.comRemQue(el.id.split("_")[-1])
                return None

        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        tracks = data["que"]["tracks"]
        queListDivs = ""
        for track in tracks:
            trackImg = HTML.genElement("img", id=f"portalSubPage_que_{track}_img", style="width: 50px; height: 50px; border-radius: 6px;", align="left", custom=f'src="{tracks[track]["album_art_uri"]}" alt="Art"')

            titleTxt = HTML.genElement("p", nest=tracks[track]["title"], style="height: 55%; margin: 2px auto 0px 0px; overflow: hidden; white-space: nowrap; text-align: left; text-overflow: ellipsis;", align="left")
            remImg = HTML.genElement("img", id=f"portalSubPage_que_rem_img_{track}", style="width: 100%;", custom='src="docs/assets/Portal/Sonos/Trash.svg" alt="Rem"')
            remBtn = HTML.genElement("button", nest=remImg, id=f"portalSubPage_que_rem_{track}", style="buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;")
            remDiv = HTML.genElement("div", nest=remBtn, align="right", style="position: absolute; right: 10px; top: 4px; width: 24px; height: 24px;")

            creatorTxt = HTML.genElement("p", nest=tracks[track]["creator"], style="height: 40%; margin: 0px auto 0px 0px; overflow: hidden; white-space: nowrap; text-align: left; text-overflow: ellipsis; font-size: 75%;", align="left")
            creatorDur = HTML.genElement("p", nest=tracks[track]["duration"][-5:], style="position: absolute; right: 8px; bottom: 4px; width: 10%; height: 18px; margin: 0px; font-size: 75%; text-align: right;", align="right")

            trackDiv = HTML.genElement("div", nest=titleTxt + remDiv + creatorTxt + creatorDur, id=f"portalSubPage_que_{track}_txt", style="width: 100%; height: 45px; margin: auto 5px;")
            queListDivs += HTML.genElement("div", nest=trackImg + trackDiv, id=f"portalSubPage_que_{track}", style="divNormal %% flex %% position: relative; height: 50px; padding: 0px 90px 0px 0px; margin: -5px; border: 5px solid #111; overflow: hidden;")

        queInp = HTML.genElement("input", id="portalSubPage_queAdd_input", type="text", style="inputMedium %% width: 75%; font-size: 75%;", custom='placeholder="share link"')
        nextBtn = HTML.genElement("button", nest="Play Next", id="portalSubPage_queAdd_playNext", type="button", style="buttonSmall %% width: 100%; height: 40%; margin: 2.5px 0px; white-space: nowrap;")
        nowBtn = HTML.genElement("button", nest="Play Now", id="portalSubPage_queAdd_playNow", type="button", style="buttonSmall %% width: 100%; height: 40%; margin: 2.5px 0px; white-space: nowrap;")
        btnDivs = HTML.genElement("div", nest=nextBtn + nowBtn, style="width: 25%;")
        queAddDivs = HTML.genElement("div", nest=queInp + btnDivs, style="flex %% height: 100%;")

        if HTML.getElement("portalSubPage_que") is None:
            queListDiv = HTML.genElement("div", nest=queListDivs, id="portalSubPage_queList", style="divNormalNoEdge %% height: 438px; margin: -5px; border: 5px solid #111; overflow-x: hidden;")
            queAddDiv = HTML.genElement("div", nest=queAddDivs, id="portalSubPage_queAdd", style="divNormalNoEdge %% height: 57px; margin: -5px; border: 5px solid #111;")
            if configSonos["useAlbumArt"]:
                quePageStyle = "divNormalNoEdge %% width: 50%; height: 500px; margin: auto; border: 5px solid #111;"
            else:
                quePageStyle = "divNormalNoEdge %% width: 25%; height: 500px; margin: auto; border: 5px solid #111;"
            HTML.addElement("div", "portalSubPage_media", id="portalSubPage_que", nest=queListDiv + queAddDiv, style=quePageStyle)
        else:
            HTML.setElementRaw("portalSubPage_queList", queListDivs)
            HTML.setElementRaw("portalSubPage_queAdd", queAddDivs)

        if data["que"]["position"] >= 0:
            CSS.setStyles(f'portalSubPage_que_{data["que"]["position"]}', (("background", "#444"), ("color", "#F7E163"), ("border", "5px solid #F7E163"), ("borderRadius", "0px"), ("zIndex", "100")))
            CSS.getAttribute(f'portalSubPage_que_{data["que"]["position"]}', "scrollIntoView")()

        def doAction():
            data = WS.dict()[self.mainCom]

            for track in data["que"]["tracks"]:
                JS.addEvent(f"portalSubPage_que_{track}", playFromQue, action="dblclick", includeElement=True)
                JS.addEvent(f'portalSubPage_que_rem_{track.split("_")[-1]}', removeFromQue, includeElement=True)
                CSS.onHoverClick(f'portalSubPage_que_rem_{track.split("_")[-1]}', "imgHover", "imgClick")

            CSS.onHoverFocus("portalSubPage_queAdd_input", "inputHover", "inputFocus")
            JS.addEvent("portalSubPage_queAdd_playNext", lambda: self.comAddQue(CSS.getAttribute("portalSubPage_queAdd_input", "value"), False))
            CSS.onHoverClick("portalSubPage_queAdd_playNext", "buttonHover", "buttonClick")
            JS.addEvent("portalSubPage_queAdd_playNow", lambda: self.comAddQue(CSS.getAttribute("portalSubPage_queAdd_input", "value"), True))
            CSS.onHoverClick("portalSubPage_queAdd_playNow", "buttonHover", "buttonClick")

        JS.afterDelay(doAction, delay=50)

    def addPlaylist(self):
        def playPlaylist(args):
            el = args.target
            for i in range(0, 4):
                if el.id == "":
                    el = el.parentElement
                    continue
                if el.id.split("_")[-1] in ["txt", "img"]:
                    el = el.parentElement
                    continue

                data = WS.dict()[self.mainCom]["playlists"]
                self.comClearQue()
                self.comAddQue(f'{data[el.id.split("_")[-1]]["url"]}', True)
                return None

        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        playlists = data["playlists"]
        plListDivs = ""
        for playlist in reversed(playlists):
            if playlists[playlist]["album_art"] is None:
                plImg = HTML.genElement("img", id=f"portalSubPage_playlist_{playlist}_img", style="width: 75px; height: 75px; border-radius: 6px;", align="left", custom='src="docs/assets/Portal/Sonos/Missing.svg" alt="Art"')
            else:
                plImg = HTML.genElement("img", id=f"portalSubPage_playlist_{playlist}_img", style="width: 75px; height: 75px; border-radius: 6px;", align="left", custom=f'src="{playlists[playlist]["album_art"]}" alt="Art"')

            titleTxt = HTML.genElement("p", nest=playlist, style="height: 55%; margin: 0px auto 0px 0px; overflow: hidden; white-space: nowrap; text-align: left; text-overflow: ellipsis;", align="left")
            discriptionTxt = HTML.genElement("p", nest=playlists[playlist]["description"], style="height: 40%; margin: 0px auto 0px 0px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; font-size: 75%; text-align: left;", align="left")

            plDiv = HTML.genElement("div", nest=titleTxt + discriptionTxt, id=f"portalSubPage_playlist_{playlist}_txt", style="width: 100%; height: 50px; margin: auto 5px;")
            plListDivs += HTML.genElement("div", nest=plImg + plDiv, id=f"portalSubPage_playlist_{playlist}", style="divNormal %% flex %% position: relative; height: 75px; padding: 0px 85px 0px 0px; margin: -5px; border: 5px solid #111; overflow: hidden;")

        plInp = HTML.genElement("input", id="portalSubPage_playlistAdd_input", type="text", style="inputMedium %% width: 75%; font-size: 75%;", custom='placeholder="share link"')
        nextBtn = HTML.genElement("button", nest="Play Next", id="portalSubPage_playlistAdd_playNext", type="button", style="buttonSmall %% width: 100%; height: 40%; margin: -1% 0px; white-space: nowrap;")
        nowBtn = HTML.genElement("button", nest="Play Now", id="portalSubPage_playlistAdd_playNow", type="button", style="buttonSmall %% width: 100%; height: 40%; margin: -1% 0px; white-space: nowrap;")
        btnDivs = HTML.genElement("div", nest=nextBtn + nowBtn, style="width: 25%;")
        plAddDivs = HTML.genElement("div", nest=plInp + btnDivs, style="flex %% height: 100%;")

        if HTML.getElement("portalSubPage_playlist") is None:
            plListDiv = HTML.genElement("div", nest=plListDivs, id="portalSubPage_playlistList", style="divNormalNoEdge %% height: 438px; margin: -5px; border: 5px solid #111; overflow-x: hidden;")
            plAddDiv = HTML.genElement("div", nest=plAddDivs, id="portalSubPage_playlistAdd", style="divNormalNoEdge %% height: 57px; margin: -5px; border: 5px solid #111;")
            if configSonos["useAlbumArt"]:
                plPageStyle = "divNormalNoEdge %% width: 50%; height: 500px; margin: auto; border: 5px solid #111;"
            else:
                plPageStyle = "divNormalNoEdge %% width: 25%; height: 500px; margin: auto; border: 5px solid #111;"
            HTML.addElement("div", "portalSubPage_media", id="portalSubPage_playlist", nest=plListDiv + plAddDiv, style=plPageStyle)
        else:
            HTML.setElementRaw("portalSubPage_playlistList", plListDivs)
            HTML.setElementRaw("portalSubPage_playlistADD", plAddDivs)

        def doAction():
            data = WS.dict()[self.mainCom]
            for playlist in data["playlists"]:
                JS.addEvent(f"portalSubPage_playlist_{playlist}", playPlaylist, action="dblclick", includeElement=True)

            CSS.onHoverFocus("portalSubPage_playlistAdd_input", "inputHover", "inputFocus")
            JS.addEvent("portalSubPage_playlistAdd_playNext", lambda: self.comAddQue(CSS.getAttribute("portalSubPage_playlistAdd_input", "value"), False))
            CSS.onHoverClick("portalSubPage_playlistAdd_playNext", "buttonHover", "buttonClick")
            JS.addEvent("portalSubPage_playlistAdd_playNow", lambda: self.comAddQue(CSS.getAttribute("portalSubPage_playlistAdd_input", "value"), True))
            CSS.onHoverClick("portalSubPage_playlistAdd_playNow", "buttonHover", "buttonClick")

        JS.afterDelay(doAction, delay=50)

    def addControls(self):
        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        btnDivsLeft = ""
        leftActions = ["Repeat", "Shuffle"]
        for i, action in enumerate(leftActions):
            margin = " margin: 0px 0.5%"
            if i >= len(leftActions) - 1:
                margin = " margin: 0px auto 0px 0.5%;"

            img = HTML.genElement("img", id=f"portalSubPage_buttons_img_{action}", style="width: 100%;", custom=f'src="docs/assets/Portal/Sonos/{action}.svg" alt="{action}"')
            btn = HTML.genElement("button", nest=img, id=f"portalSubPage_buttons_{action}", style="buttonImg %% border: 0px solid #222; border-radius: 16px;")
            btnDivsLeft += HTML.genElement("div", nest=btn, align="center", style=f"max-width: 55px;{margin}")
        btnDivLeft = HTML.genElement("div", nest=btnDivsLeft, id="portalSubPage_buttons_left", style="divNormalNoEdge %% flex %% width: 15%;")

        btnDivsMiddle = ""
        midActions = ["VolumeDown", "SeekBackward", "Back", "Pause", "Next", "SeekForward", "VolumeUp"]
        for i, action in enumerate(midActions):
            margin = " margin: 0px 0.5%;"
            if i < 1:
                margin = " margin: 0px 0.5% 0px auto;"
            elif i >= len(midActions) - 1:
                margin = " margin: 0px auto 0px 0.5%;"

            img = HTML.genElement("img", id=f"portalSubPage_buttons_img_{action}", style="width: 100%;", custom=f'src="docs/assets/Portal/Sonos/{action}.svg" alt="{action}"')
            btn = HTML.genElement("button", nest=img, id=f"portalSubPage_buttons_{action}", style="buttonImg %% border: 0px solid #222; border-radius: 16px;")
            btnDivsMiddle += HTML.genElement("div", nest=btn, align="center", style=f"max-width: 55px;{margin}")
        btnDivMiddle = HTML.genElement("div", nest=btnDivsMiddle, id="portalSubPage_buttons_middle", style="divNormalNoEdge %% flex %% width: 70%;")

        btnDivsRight = ""
        rightActions = ["Album", "Que"]
        for i, action in enumerate(rightActions):
            margin = " margin: 0px 0.5%;"
            if i < 1:
                margin = " margin: 0px 0.5% 0px auto;"

            img = HTML.genElement("img", id=f"portalSubPage_buttons_img_{action}", style="width: 100%;", custom=f'src="docs/assets/Portal/Sonos/{action}.svg" alt="{action}"')
            btn = HTML.genElement("button", nest=img, id=f"portalSubPage_buttons_{action}", style="buttonImg %% border: 0px solid #222; border-radius: 16px;")
            btnDivsRight += HTML.genElement("div", nest=btn, align="center", style=f"max-width: 55px;{margin}")
        btnDivRight = HTML.genElement("div", nest=btnDivsRight, id="portalSubPage_buttons_right", style="divNormalNoEdge %% flex %% width: 15%;")

        options = ""
        for option in range(0, 101, int(configSonos["volumeMax"] / 10)):
            options += HTML.genElement("option", custom=f'value="{option}" label="{option}"')
        volDatalist = HTML.genElement("datalist", nest=options, id="portalSubPage_volume_datalist")

        volInp = HTML.genElement(
            "input",
            id="portalSubPage_volume_slider",
            type="range",
            style="inputRange %% width: 100%; height: 10px; margin: 0px auto 5px auto;",
            custom=f'min="0" max="{configSonos["volumeMax"]}" value="{data["device"]["volume"]}" list="portalSubPage_volume_datalist"',
        )

        HTML.addElement("div", "portalSubPage_main", nest=btnDivLeft + btnDivMiddle + btnDivRight, id="portalSubPage_buttons", style="divNormal %% flex %% margin: 5px auto; padding: 0px; overflow: hidden;")
        HTML.addElement("div", "portalSubPage_main", nest=volDatalist + volInp, id="portalSubPage_volume", style="divNormal %% flex %% width: 40%; margin: 5px auto; padding: 0px; overflow: hidden;")

        def doAction(self):
            data = WS.dict()[self.mainCom]

            if data["device"]["playback"] in ["standby", "inactive"]:
                CSS.setAttributes("portalSubPage_buttons_img_Pause", (("src", "docs/assets/Portal/Sonos/Play.svg"), ("alt", "Play")))
            JS.addEvent("portalSubPage_volume_slider", self.comVolume, action="input", includeElement=True)

            fmap = {
                "Repeat": self.comToggleRepeat,
                "Shuffle": self.comToggleShuffle,
                "VolumeDown": self.comVolumeDown,
                "SeekBackward": self.comSeekBackward,
                "Back": self.comBack,
                "Pause": self.comTogglePlay,
                "Next": self.comNext,
                "SeekForward": self.comSeekForward,
                "VolumeUp": self.comVolumeUp,
            }
            for action in fmap:
                JS.addEvent(f"portalSubPage_buttons_{action}", fmap[action])
                CSS.onHoverClick(f"portalSubPage_buttons_{action}", "imgHover", "imgClick")

            JS.addEvent(f"portalSubPage_buttons_Album", self.comUseAlbumArt)
            if configSonos["useAlbumArt"]:
                CSS.setStyles("portalSubPage_buttons_Album", (("background", "#444"), ("border", "3px solid #FBDF56")))
                CSS.onClick("portalSubPage_buttons_Album", "imgClick")
            else:
                CSS.setStyles("portalSubPage_buttons_Album", (("background", "#222"), ("border", "2px solid #222")))
                CSS.onHoverClick(f"portalSubPage_buttons_Album", "imgHover", "imgClick")

            JS.addEvent(f"portalSubPage_buttons_Que", self.comUseQuePlaylist)
            if configSonos["useQue"] or configSonos["usePlaylist"]:
                CSS.setStyles("portalSubPage_buttons_Que", (("background", "#444"), ("border", "3px solid #FBDF56")))
                CSS.onClick("portalSubPage_buttons_Que", "imgClick")
            else:
                CSS.setStyles("portalSubPage_buttons_Que", (("background", "#222"), ("border", "2px solid #222")))
                CSS.onHoverClick(f"portalSubPage_buttons_Que", "imgHover", "imgClick")

            if configSonos["useQue"]:
                CSS.setAttributes("portalSubPage_buttons_img_Que", (("src", "docs/assets/Portal/Sonos/Que.svg"), ("alt", "Que")))
            elif configSonos["usePlaylist"]:
                CSS.setAttributes("portalSubPage_buttons_img_Que", (("src", "docs/assets/Portal/Sonos/Playlist.svg"), ("alt", "Playlist")))

        JS.afterDelay(doAction, (self,), delay=50)

    def qrPage(self):
        def onHover(smallerId, bigerId):
            pass

        txt = HTML.genElement("h1", nest="Sonos S2 - Android", id="Header_SonosAndroidQR", style="headerMain %% white-space: nowrap; overflow: hidden;")
        img = HTML.genElement("img", id="Image_SonosAndroidQR", style="width: 75%; margin: 10px auto; user-select:none;", custom='src="docs/assets/Portal/Sonos/SonosAndroidQR.png" alt="Sonos Android QR"')
        mainDivs = HTML.genElement("div", nest=txt + img, id="portalSubPage_main_qrAndroid", style="divNormalNoEdge %% width: 50%;")

        txt = HTML.genElement("h1", nest="Sonos S2 - iOS", id="Header_SonosIosQR", style="headerMain %% white-space: nowrap; overflow: hidden;")
        img = HTML.genElement("img", id="Image_SonosIosQR", style="width: 75%; margin: 10px auto; user-select:none;", custom='src="docs/assets/Portal/Sonos/SonosIosQR.png" alt="Sonos iOS QR"')
        mainDivs += HTML.genElement("div", nest=txt + img, id="portalSubPage_main_qrIos", style="divNormalNoEdge %% width: 50%;")

        HTML.setElement("div", "portalSubPage", nest=mainDivs, id="portalSubPage_main", style="divNormal %% flex %% margin: 0px auto;")

        def doAction():
            JS.addEvent("portalSubPage_main_qrAndroid", onHover, ("portalSubPage_main_qrIos", "portalSubPage_main_qrAndroid"))
            JS.addEvent("portalSubPage_main_qrIos", onHover, ("portalSubPage_main_qrAndroid", "portalSubPage_main_qrIos"))

        JS.afterDelay(doAction, delay=50)

    def comEnableStream(self):
        if not self.dataStreamState:
            self.dataStreamState = not self.dataStreamState
            WS.send(f"{self.mainCom} enableStream")

    def comDisableStream(self):
        if self.dataStreamState:
            self.dataStreamState = not self.dataStreamState
            WS.send(f"{self.mainCom} disableStream")

    def comTogglePlay(self):
        data = WS.dict()[self.mainCom]

        if data["device"]["playback"] == "active":
            WS.send(f"{self.mainCom} pause")
        elif data["device"]["playback"] in ["standby", "inactive"]:
            WS.send(f"{self.mainCom} play")

    def comToggleRepeat(self):
        WS.send(f"{self.mainCom} toggleRepeat")

    def comToggleShuffle(self):
        WS.send(f"{self.mainCom} toggleShuffle")

    def comNext(self):
        WS.send(f"{self.mainCom} next")

    def comBack(self):
        WS.send(f"{self.mainCom} back")

    def comVolume(self, args=None, vol: int = None):
        configSonos = self.getCachedConfig()
        if args is None:
            if vol is None or vol > configSonos["volumeMax"]:
                return None

            WS.send(f"{self.mainCom} volume {vol}")
            return None

        if not int(args.target.value) > configSonos["volumeMax"]:
            WS.send(f"{self.mainCom} volume {int(args.target.value)}")

    def comVolumeUp(self):
        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        if data["device"]["volume"] + 5 > configSonos["volumeMax"]:
            WS.send(f'{self.mainCom} volume {configSonos["volumeMax"]}')
            return None

        WS.send(f"{self.mainCom} volume up")

    def comVolumeDown(self):
        WS.send(f"{self.mainCom} volume down")

    def comSeek(self, args=None, pos: int = None):
        if args is None:
            if pos is None:
                return None

            WS.send(f"{self.mainCom} seek {pos}")
            return None

        WS.send(f"{self.mainCom} seek {int(args.target.value)}")

    def comSeekForward(self):
        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        newPos = datetime.strptime(data["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) + configSonos["seekStep"]
        dur = datetime.strptime(data["track"]["duration"], "%H:%M:%S")
        dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second
        if newPos >= dur:
            newPos = dur

        self.comSeek(pos=newPos)

    def comSeekBackward(self):
        data = WS.dict()[self.mainCom]
        configSonos = self.getCachedConfig()

        newPos = datetime.strptime(data["position"], "%H:%M:%S")
        newPos = ((newPos.hour * 3600) + (newPos.minute * 60) + newPos.second) - configSonos["seekStep"]
        if newPos < 0:
            newPos = 0

        self.comSeek(pos=newPos)

    def comGetQue(self):
        WS.send(f"{self.mainCom} que get")

    def comSetQue(self, index: int):
        WS.send(f"{self.mainCom} que {index}")

    def comRemQue(self, index: int):
        WS.send(f"{self.mainCom} queRemove {index}")

    def comClearQue(self):
        WS.send(f"{self.mainCom} queClear")

    def comAddQue(self, url: str, playNow: bool = False):
        if not playNow:
            WS.send(f"{self.mainCom} playNext {url}")
        else:
            WS.send(f"{self.mainCom} playNow {url}")

    def comUseAlbumArt(self):
        self.setCachedConfig("useAlbumArt", (not self.getCachedConfig()["useAlbumArt"]))

        self._loadPortalSubPage()

    def comUseQuePlaylist(self):
        configSonos = self.getCachedConfig()
        if configSonos["useQue"]:
            self.setCachedConfig("useQue", False)
            self.setCachedConfig("usePlaylist", True)

        elif configSonos["usePlaylist"]:
            self.setCachedConfig("useQue", False)
            self.setCachedConfig("usePlaylist", False)

        else:
            self.setCachedConfig("useQue", True)
            self.setCachedConfig("usePlaylist", False)

        self._loadPortalSubPage()

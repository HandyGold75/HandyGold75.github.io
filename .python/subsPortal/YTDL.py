from datetime import datetime, timedelta
from json import dumps, loads

from WebKit import CSS, HTML, JS, WS, PortalPage, Widget


class ytdl(PortalPage):
    def __init__(self):
        super().__init__()

        self.mainComReadCommands = ["state"]

        self.onSubPageLoad = self.loadSubPage

        self.lastDownload = 0
        self.lastDataPackage = {}

    def loadSubPage(self):
        getattr(self, f'{JS.cache("portalSubPage").lower()}Page')()

    def uiRefresh(self):
        def slowUIRefresh():
            def download():
                def removeFromDownload(args):
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

                        WS.send(f'{self.mainCom} remove {el.id.split("_")[-1]}')
                        return None

                data = WS.dict()[self.mainCom]
                HTML.setElement("div", "portalSubPage_results_out", nest=self.getRecords(), style="divNormal")
                for index in reversed(data["downloads"]):
                    JS.addEvent(f"portalSubPage_results_rem_{index}", removeFromDownload, includeElement=True)
                    CSS.onHoverClick(f"portalSubPage_results_rem_{index}", "imgHover", "imgClick")

            if not JS.cache("portalSubPage") == "Download":
                return False

            data = WS.dict()[self.mainCom]
            if data != self.lastDataPackage:
                download()
                self.lastDataPackage = data

            JS.afterDelay(self.getData, delay=1000)
            JS.afterDelay(slowUIRefresh, delay=2000)

        self.lastDataPackage = {}
        JS.afterDelay(slowUIRefresh, delay=50)

    def downloadPage(self):
        def submitDownload(args):
            if hasattr(args, "key") and not args.key in ["Enter"]:
                return None

            input = HTML.getElement("download_input").value
            if not input.startswith("https://www.youtube.com/watch?v=") and not input.startswith("https://www.youtube.com/shorts/"):
                return None

            if (datetime.now() - timedelta(seconds=15)).timestamp() < self.lastDownload:
                Widget.popup("warning", f"Download throttled\nPlease wait {int(self.lastDownload - (datetime.now() - timedelta(seconds=15)).timestamp())} seconds until starting the next download.")
                return None
            self.lastDownload = datetime.now().timestamp()

            configYTDL = self.getCachedConfig()
            if configYTDL["audioOnly"]:
                WS.send(f'{self.mainCom} download audio {configYTDL["quality"][-1]} {input}')
            else:
                WS.send(f'{self.mainCom} download video {configYTDL["quality"][-1]} {input}')

        dlHeader = HTML.genElement("h1", nest="YouTube Downloader", style="headerMain %% width: 100%; margin: 0px auto -4px auto;")
        dlInp = HTML.genElement("input", id="download_input", type="text", style="inputMedium %% width: 70%; margin: 10px 3px 10px auto;")
        dlBtn = HTML.genElement("button", nest="Download", id="download_button", type="button", style="buttonMedium %% width: 10%; margin: 10px auto 10px 3px;")
        dlBody = HTML.genElement("div", nest=dlInp + dlBtn, style="background %% flex %% width: 100%;  margin: 0px auto;")
        dl = HTML.genElement("div", nest=dlHeader + dlBody, id="portalSubPage_download", style="divNormal %% width: 95%;")

        resHeader = HTML.genElement("h1", nest="Recent Downloads", style="headerMain %% width: 100%; margin: 0px auto -4px auto;")
        resBody = HTML.genElement("div", id="portalSubPage_results_out", style="background %% width: 100%; min-height: 20px; margin: 0px auto;")
        res = HTML.genElement("div", nest=resHeader + resBody, id="portalSubPage_results", style="divNormal %% width: 95%; margin-top: 50px;")

        HTML.addElementRaw("portalSubPage", dl + res)

        def addEvents():
            JS.addEvent("download_input", submitDownload, action="keyup", includeElement=True)
            CSS.onHoverFocus("download_input", "inputHover", "inputFocus")
            JS.addEvent("download_button", submitDownload, includeElement=True)
            CSS.onHoverClick("download_button", "buttonHover", "buttonClick")

        JS.afterDelay(addEvents, delay=50)
        JS.afterDelay(self.uiRefresh, delay=100)

    def historyPage(self):
        def removeFromDownload(args):
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

                WS.send(f'{self.mainCom} remove {el.id.split("_")[-1]}')
                return None

        resDiv = HTML.genElement("div", nest=self.getRecords(history=True), style="divNormal")

        resHeader = HTML.genElement("h1", nest="History", style="headerMain %% width: 95%; width: 100%;  margin: 0px auto -4px auto;")
        resBody = HTML.genElement("div", nest=resDiv, id="portalSubPage_results_out", style="background %% width: 100%; min-height: 20px; margin: 0px auto;")
        res = HTML.genElement("div", nest=resHeader + resBody, id="portalSubPage_results", style="divNormal %% width: 95%; ")

        HTML.addElementRaw("portalSubPage", res)

        def addEvents():
            data = WS.dict()[self.mainCom]
            for index in reversed(data["history"]):
                JS.addEvent(f"portalSubPage_results_rem_{index}", removeFromDownload, includeElement=True)
                CSS.onHoverClick(f"portalSubPage_results_rem_{index}", "imgHover", "imgClick")

        JS.afterDelay(addEvents, delay=50)

    def getRecords(self, history=False):
        dataKey = "history" if history else "downloads"
        data = WS.dict()[self.mainCom]
        records = ""
        for i, index in enumerate(reversed(data[dataKey])):
            values = HTML.genElement("h1", nest=index, style="headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;")
            remImg = HTML.genElement("img", id=f"portalSubPage_results_rem_img_{index}", style="width: 100%;", custom='src="docs/assets/Portal/Sonos/Trash.svg" alt="Rem"')
            remBtn = HTML.genElement("button", nest=remImg, id=f"portalSubPage_results_rem_{index}", style="buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;")
            rem = HTML.genElement("div", nest=remBtn, align="right", style="max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;")
            values += HTML.genElement("div", nest=rem, style="flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;")

            if type(data[dataKey][index]["Modified"]) is int:
                data[dataKey][index]["Modified"] = datetime.fromtimestamp(data[dataKey][index]["Modified"]).strftime("%d %b %y - %H:%M")

            for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                if not key2 is None:
                    txt = HTML.genElement("p", nest=key1, style="width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    if key1 == "State":
                        if data[dataKey][index][key1] == "Done":
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;")
                        elif data[dataKey][index][key1] == "Failed":
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #F05; overflow: hidden;")
                        else:
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #F85; overflow: hidden;")
                    else:
                        txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;")
                else:
                    txt = HTML.genElement("p", nest=key1, style="width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    if key1 in ["Link", "URL"]:
                        txt += HTML.linkWrap(data[dataKey][index][key1], nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    else:
                        txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 75%; margin: 0px auto; overflow: hidden;")
                    div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;")

                if not key2 is None:
                    txt = HTML.genElement("p", nest=key2, style="width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    txt += HTML.genElement("p", nest=data[dataKey][index][key2], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    div += HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;")
                    values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")
                    continue

                values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")

            if not data[dataKey][index]["Error"] == "":
                txt = HTML.genElement("p", nest="Error", style="width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                txt += HTML.genElement("p", nest=data[dataKey][index]["Error"], style="width: 75%; margin: 0px auto; overflow: hidden;")
                div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;")
                values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")

            if i == 0:
                records += HTML.genElement("div", nest=values, style="divNormal %% margin: 0px auto 6px auto;")
                continue
            records += HTML.genElement("div", nest=values, style="divNormal %% margin: 0px auto 6px auto; padding: 8px 5px 5px 5px; border-top: 3px dashed #55F; border-radius: 0px;")

        return records

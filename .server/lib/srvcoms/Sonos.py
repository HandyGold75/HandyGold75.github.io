from asyncio import run
from datetime import datetime, timedelta
from json import dumps, load
from os import makedirs, path as osPath
from re import sub
from threading import Thread
from time import sleep

from requests import get
from soco.discovery import any_soco
from soco.exceptions import SoCoUPnPException
from soco.music_library import MusicLibrary

# from soco.music_services import MusicService # https://github.com/SoCo/SoCo/issues/557
from soco.plugins.sharelink import ShareLinkPlugin
from youtube_search import YoutubeSearch


class sonos:
    def __init__(self, return_var=None):
        speaker = None
        try:
            with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "") + "/server/config.json", "r", encoding="UTF-8") as fileR:
                speaker = any_soco(allow_network_scan=True, networks_to_scan=load(fileR)["SonosSubnet"], max_threads=1024)
        except (AttributeError, FileNotFoundError):
            print("WARNING: No sonos device was discovered, sonos commands will be unavailable!")

        self.mediaPath = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "/public/Sonos")
        if not osPath.exists(self.mediaPath):
            makedirs(self.mediaPath)

        self.deamon = None
        self.deamon_exit = True

        if speaker is None:
            self.speaker = None
            self.commands = {}
            if not return_var is None:
                return_var[0] = self
            return None

        self.commands = {
            "position": ["Home", sonos.getTrackPosition],
            "device": ["Home", sonos.getDevice],
            "track": ["Home", sonos.getTrack],
            "playlist": ["Home", sonos.getPlaylist],
            "ytinfo": ["Home", sonos.ytinfo],
            "enablestream": ["Home", sonos.enableDataStream],
            "disablestream": ["Home", sonos.disableDataStream],
            "toggleshuffle": ["Home", sonos.toggleShuffle],
            "togglerepeat": ["Home", sonos.toggleRepeat],
            "toggleplay": ["Home", sonos.togglePlay],
            "play": ["Home", sonos.play],
            "pause": ["Home", sonos.pause],
            "next": ["Home", sonos.next],
            "back": ["Home", sonos.back],
            "seek": ["Home", sonos.seek],
            "volume": ["Home", sonos.volume],
            "que": ["Home", sonos.que],
            "queremove": ["Home", sonos.queRemove],
            "queclear": ["Home", sonos.queClear],
            "playnext": ["Home", sonos.playNext],
            "playnow": ["Home", sonos.playNow],
        }

        self.speaker = speaker
        try:
            self.speaker.partymode()
            self.speaker.cross_fade = True
        except SoCoUPnPException as err:
            print(f"WARNING: {err}")

        if not return_var is None:
            return_var[0] = self

    def sanetize(obj, remove: tuple):
        if isinstance(obj, dict):
            return {k: sonos.sanetize(v, remove) for k, v in obj.items() if k not in remove}

        if isinstance(obj, list):
            return [sonos.sanetize(v, remove) for v in obj]

        return obj

    def cacheImg(src: str = "", dst: str = "", pairs: tuple = ()):
        if (src != "" and dst != "") and not osPath.exists(dst):
            for i in range(1, 11):
                if osPath.exists(dst):
                    break

                req = get(src)
                if req.status_code == 200:
                    with open(dst, "wb") as fileW:
                        fileW.write(req.content)
                    break

                sleep(i)

        if pairs == ():
            return None

        for srcPair, dstPair in pairs:
            if (srcPair != "" and dstPair != "") and not osPath.exists(dstPair):
                sonos.cacheImg(srcPair, dstPair)

    async def getTrackPosition(clT):
        return {"position": sonos.sanetize(clT.sonos.speaker.get_current_track_info(), ["metadata"])["position"]}

    async def getDevice(clT):
        return {
            "device": {
                "playback": {"PLAYING": "active", "STOPPED": "inactive", "PAUSED_PLAYBACK": "standby", "TRANSITIONING": "busy"}[clT.sonos.speaker.get_current_transport_info()["current_transport_state"]],
                "volume": clT.sonos.speaker.volume,
                "shuffle": clT.sonos.speaker.shuffle,
                "repeat": clT.sonos.speaker.repeat,
            }
        }

    async def getTrack(clT):
        trackinfo = clT.sonos.speaker.get_current_track_info()
        title = sub("[^A-Za-z0-9]", "!", trackinfo["title"])
        artist = sub("[^A-Za-z0-9]", "!", trackinfo["artist"])

        if not osPath.exists(f"{clT.sonos.mediaPath}/{title}"):
            makedirs(f"{clT.sonos.mediaPath}/{title}")

        dst = f"{clT.sonos.mediaPath}/{artist}/{title}"
        Thread(target=sonos.cacheImg, args=(trackinfo["album_art"], dst)).start()

        with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "") + "/server/config.json", "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)
        trackinfo["album_art"] = f'https://doc.{fileData["Domain"]}:{fileData["PORT"] + 1}/Sonos/{artist}/{title}'

        return {"track": sonos.sanetize(trackinfo, ["metadata", "position"])}

    async def getQue(clT):
        tracks = {}
        start = max(0, int(clT.sonos.speaker.get_current_track_info()["playlist_position"]) - 101)

        for i, track in enumerate(clT.sonos.speaker.get_queue(start=start, max_items=201, full_album_art_uri=True)):
            trackDict = track.to_dict()
            title = sub("[^A-Za-z0-9]", "!", trackDict["title"])
            creator = sub("[^A-Za-z0-9]", "!", trackDict["creator"])

            if not osPath.exists(f"{clT.sonos.mediaPath}/{creator}"):
                makedirs(f"{clT.sonos.mediaPath}/{creator}")

            dst = f"{clT.sonos.mediaPath}/{creator}/{title}"
            Thread(target=sonos.cacheImg, args=(trackDict["album_art_uri"], dst)).start()

            with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "") + "/server/config.json", "r", encoding="UTF-8") as fileR:
                fileData = load(fileR)
            trackDict["album_art_uri"] = f'https://doc.{fileData["Domain"]}:{fileData["PORT"] + 1}/Sonos/{creator}/{title}'

            tracks[f"{i + start}"] = trackDict
            tracks[f"{i + start}"]["duration"] = tracks[f"{i + start}"]["resources"][0]["duration"]


        return {"que": {"size": clT.sonos.speaker.queue_size, "position": int(clT.sonos.speaker.get_current_track_info()["playlist_position"]) - 1, "tracks": sonos.sanetize(tracks, ["parent_id", "item_id", "restricted", "resources", "desc"])}}

    async def ytinfo(clT):
        trackInfo = clT.sonos.speaker.get_current_track_info()
        search = YoutubeSearch(f'{trackInfo["title"]} - {trackInfo["artist"]}', max_results=5).to_dict()

        trackDur = datetime.strptime(trackInfo["duration"], "%H:%M:%S")
        trackDur = (trackDur.hour * 3600) + (trackDur.minute * 60) + trackDur.second

        exactMatch, strictMatch, modestMatch, looseMatch = (None, None, None, None)
        for songData in search:
            songDur = datetime.strptime(f'{ "00:" * (3 -  len(str(songData["duration"]).split(":")))}{songData["duration"]}', "%H:%M:%S")
            songDur = (songDur.hour * 3600) + (songDur.minute * 60) + songDur.second

            artistMatch = trackInfo["artist"].lower() in songData["channel"].lower()
            titleMatch = trackInfo["title"].lower() in songData["title"].lower()

            if artistMatch and titleMatch and songDur == trackDur:
                exactMatch = songData
                break

            elif not songDur < trackDur + 30 or not songDur > trackDur - 30:
                continue

            if strictMatch is None and artistMatch:
                strictMatch = songData
                continue
            elif modestMatch is None and titleMatch:
                modestMatch = songData
                continue
            elif looseMatch is None:
                looseMatch = songData
                continue

        if not exactMatch is None:  # exactMatch -> Artist, Title and exact Duration
            return {
                "ytinfo": {
                    "id": f'{exactMatch["id"]}',
                    "match": f"exact",
                    "title": f'{exactMatch["title"]}',
                    "channel": f'{exactMatch["channel"]}',
                    "duration": f'{exactMatch["duration"]}',
                    "views": f'{str(exactMatch["views"]).replace("weergaven", "views")}',
                    "publish_time": f'{str(exactMatch["publish_time"]).replace("geleden", "ago").replace("jaren", "years").replace("maanden", "months").replace("dagen", "days")}',
                    "thumbnails": f'{exactMatch["thumbnails"]}',
                }
            }

        if not strictMatch is None:  # strictMatch -> Artist and loose Duration
            return {
                "ytinfo": {
                    "id": f'{strictMatch["id"]}',
                    "match": f"strict",
                    "title": f'{strictMatch["title"]}',
                    "channel": f'{strictMatch["channel"]}',
                    "duration": f'{strictMatch["duration"]}',
                    "views": f'{str(strictMatch["views"]).replace("weergaven", "views")}',
                    "publish_time": f'{str(strictMatch["publish_time"]).replace("geleden", "ago").replace("jaren", "years").replace("maanden", "months").replace("dagen", "days")}',
                    "thumbnails": f'{strictMatch["thumbnails"]}',
                }
            }

        elif not modestMatch is None:  # modestMatch -> Title and loose Duration
            return {
                "ytinfo": {
                    "id": f'{modestMatch["id"]}',
                    "match": f"modest",
                    "title": f'{modestMatch["title"]}',
                    "channel": f'{modestMatch["channel"]}',
                    "duration": f'{modestMatch["duration"]}',
                    "views": f'{str(modestMatch["views"]).replace("weergaven", "views")}',
                    "publish_time": f'{str(modestMatch["publish_time"]).replace("geleden", "ago").replace("jaren", "years").replace("maanden", "months").replace("dagen", "days")}',
                    "thumbnails": f'{modestMatch["thumbnails"]}',
                }
            }

        elif not looseMatch is None:  # looseMatch -> loose Duration
            return {
                "ytinfo": {
                    "id": f'{looseMatch["id"]}',
                    "match": f"loose",
                    "title": f'{looseMatch["title"]}',
                    "channel": f'{looseMatch["channel"]}',
                    "duration": f'{looseMatch["duration"]}',
                    "views": f'{str(looseMatch["views"]).replace("weergaven", "views")}',
                    "publish_time": f'{str(looseMatch["publish_time"]).replace("geleden", "ago").replace("jaren", "years").replace("maanden", "months").replace("dagen", "days")}',
                    "thumbnails": f'{looseMatch["thumbnails"]}',
                }
            }

        else:  # anyMatch -> First in query
            return {
                "ytinfo": {
                    "id": f'{search[0]["id"]}',
                    "match": f"any",
                    "title": f'{search[0]["title"]}',
                    "channel": f'{search[0]["channel"]}',
                    "duration": f'{search[0]["duration"]}',
                    "views": f'{str(search[0]["views"]).replace("weergaven", "views")}',
                    "publish_time": f'{str(search[0]["publish_time"]).replace("geleden", "ago").replace("jaren", "years").replace("maanden", "months").replace("dagen", "days")}',
                    "thumbnails": f'{search[0]["thumbnails"]}',
                }
            }

    async def dataStream(clT):
        oldStates = {"getTrackPosition": None, "getDevice": None, "getTrack": None, "getPlaylist": None, "getQue": None, "ytinfo": None}
        nextupdate = datetime.now()

        while not clT.sonos.deamon_exit:
            now = datetime.now()
            sleep(max(0, nextupdate.timestamp() - now.timestamp()))
            nextupdate = datetime.now() + timedelta(seconds=1)

            for func in (sonos.getTrackPosition, sonos.getDevice, sonos.getTrack, sonos.getQue, sonos.ytinfo):
                newState = await func(clT)
                if newState != oldStates[func.__name__]:
                    oldStates[func.__name__] = newState
                    await clT.ws.send(dumps({"sonos": newState}))

    async def enableDataStream(clT):
        def dataStreamWrapper(clT):
            run(sonos.dataStream(clT))

        if not clT.sonos.deamon is None:
            return "Data Stream is already running!"

        clT.sonos.deamon_exit = False
        clT.sonos.deamon = Thread(target=dataStreamWrapper, args=(clT,))
        clT.sonos.deamon.start()

        return "Data stream enabled."

    async def disableDataStream(clT):
        if clT.sonos.deamon is None:
            return "Data Stream is not running!"

        clT.sonos.deamon_exit = True
        clT.sonos.deamon.join()
        clT.sonos.deamon = None

        return "Data stream disabled."

    async def getPlaylist(clT):
        playlists = {}
        for playlist in MusicLibrary(clT.sonos.speaker).get_sonos_favorites():
            if not hasattr(playlist, "description") or playlist.description != "Spotify Playlist":
                continue

            playlists[playlist.title] = {}
            playlists[playlist.title]["description"] = playlist.description
            playlists[playlist.title]["url"] = f'https://open.spotify.com/playlist/{playlist.get_uri().split("%3a")[-1].split("?")[0]}'
            playlists[playlist.title]["album_art"] = playlist.album_art_uri

        return {"playlists": playlists}

    async def toggleShuffle(clT):
        clT.sonos.speaker.shuffle = not (await sonos.getDevice(clT))["device"]["shuffle"]

        return await sonos.getDevice(clT)

    async def toggleRepeat(clT):
        clT.sonos.speaker.repeat = not (await sonos.getDevice(clT))["device"]["repeat"]

        return await sonos.getDevice(clT)

    async def togglePlay(clT):
        if (await sonos.getDevice(clT))["device"]["playback"] == "active":
            clT.sonos.speaker.pause()
        elif (await sonos.getDevice(clT))["device"]["playback"] in ["standby", "inactive"]:
            clT.sonos.speaker.play()

        return await sonos.getDevice(clT)

    async def play(clT):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["standby", "inactive"]:
            clT.sonos.speaker.play()

        return await sonos.getDevice(clT)

    async def pause(clT):
        if (await sonos.getDevice(clT))["device"]["playback"] == "active":
            clT.sonos.speaker.pause()

        return await sonos.getDevice(clT)

    async def next(clT):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"]:
            try:
                clT.sonos.speaker.next()
            except SoCoUPnPException:
                pass

            while (await sonos.getDevice(clT))["device"]["playback"] == "busy":
                pass
            if (await sonos.getDevice(clT))["device"]["playback"] == "standby":
                clT.sonos.speaker.play()

        return await sonos.getTrack(clT)

    async def back(clT):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"]:
            try:
                clT.sonos.speaker.previous()
            except SoCoUPnPException:
                pass

            while (await sonos.getDevice(clT))["device"]["playback"] == "busy":
                pass
            if (await sonos.getDevice(clT))["device"]["playback"] in ["standby", "inactive"]:
                clT.sonos.speaker.play()

        return await sonos.getTrack(clT)

    async def seek(clT, time: int):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"]:
            time = int(time)
            dur = datetime.strptime((await sonos.getTrack(clT))["track"]["duration"], "%H:%M:%S")
            dur = (dur.hour * 3600) + (dur.minute * 60) + dur.second

            if time > dur or time < 0 or time >= 86400:
                return await sonos.getTrackPosition(clT)

            clT.sonos.speaker.seek(str(timedelta(seconds=time)))

            while (await sonos.getDevice(clT))["device"]["playback"] == "busy":
                pass
            if (await sonos.getDevice(clT))["device"]["playback"] in ["standby", "inactive"]:
                clT.sonos.speaker.play()

        return await sonos.getTrackPosition(clT)

    async def volume(clT, vol):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"] and vol != "get":
            if vol == "up":
                clT.sonos.speaker.volume += 5
            elif vol == "down":
                clT.sonos.speaker.volume -= 5
            elif int(vol) >= 0 or int(vol) <= 100:
                clT.sonos.speaker.volume = int(vol)

        return await sonos.getDevice(clT)

    async def que(clT, index):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"] and index != "get":
            clT.sonos.speaker.play_from_queue(int(index))

        return await sonos.getQue(clT)

    async def queRemove(clT, index: str):
        if (await sonos.getDevice(clT))["device"]["playback"] in ["active", "standby", "inactive"]:
            clT.sonos.speaker.remove_from_queue(int(index))

        return await sonos.getQue(clT)

    async def queClear(clT):
        clT.sonos.speaker.clear_queue()

        return await sonos.getQue(clT)

    async def playNext(clT, url):
        slp = ShareLinkPlugin(clT.sonos.speaker)

        if not slp.is_share_link(url):
            return f"Not a valid URL: {url}."

        slp.add_share_link_to_queue(url, int((await sonos.getTrack(clT))["track"]["playlist_position"]) + 1, as_next=True)

        return await sonos.getQue(clT)

    async def playNow(clT, url):
        slp = ShareLinkPlugin(clT.sonos.speaker)

        if not slp.is_share_link(url):
            return f"Not a valid URL: {url}."

        i = slp.add_share_link_to_queue(url, int((await sonos.getTrack(clT))["track"]["playlist_position"]) + 1, as_next=True)
        clT.sonos.speaker.play_from_queue(index=i - 1)

        return await sonos.getQue(clT)

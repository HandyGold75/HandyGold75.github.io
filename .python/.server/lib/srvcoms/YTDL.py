import subprocess
from datetime import datetime, timedelta
from json import dump, load
from json.decoder import JSONDecodeError
from multiprocessing import Process
from os import makedirs, path as osPath, remove
from re import sub
from shutil import move, which
from string import punctuation
from sys import platform
from time import sleep

import ffmpeg
from psutil import Process as psProcess
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError, VideoPrivate, VideoRegionBlocked, VideoUnavailable

if platform == "win32":
    from psutil import BELOW_NORMAL_PRIORITY_CLASS, IOPRIO_LOW
else:
    from psutil import IOPRIO_CLASS_IDLE


class ytdl:
    requiredFiles = {
        "/Downloads.json": {
            "Title": str,
            "Link": str,
            "URL": str,
            "HasVideo": bool,
            "HasAudio": bool,
            "Resolution": str,
            "AudioBitrate": str,
            "State": str,
            "Error": str,
            "Modified": int,
        },
    }
    mainFolder = "YTDL"

    def __init__(self, userData, return_var=None):
        workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{userData["Token"]}/{ytdl.mainFolder}'
        if not osPath.exists(workFolder):
            makedirs(workFolder)
        if not osPath.exists(f"{workFolder}/temp"):
            makedirs(f"{workFolder}/temp")

        self.mediaPath = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "/public/YTDL")
        if not osPath.exists(self.mediaPath):
            makedirs(self.mediaPath)

        for file in ytdl.requiredFiles:
            if len(file.split("/")) > 2:
                if not osPath.exists(f'{workFolder}{"/".join(file.split("/")[:-1])}'):
                    makedirs(f'{workFolder}{"/".join(file.split("/")[:-1])}')

            if not osPath.exists(f"{workFolder}{file}"):
                with open(f"{workFolder}{file}", "w", encoding="UTF-8") as fileW:
                    if type(ytdl.requiredFiles[file]) is dict:
                        dump({}, fileW)
                        continue
                    fileW.write("")

        self.ffmpegLocation = None
        if not which("ffmpeg") is None:
            self.ffmpegLocation = which("ffmpeg")
        elif osPath.exists(f"{osPath.split(__file__)[0]}/ffmpeg.exe"):
            self.ffmpegLocation = f"{osPath.split(__file__)[0]}/ffmpeg.exe"
        else:
            try:
                subprocess.check_output(("ffmpeg", "-version"), stderr=subprocess.STDOUT)
                self.ffmpegLocation = "ffmpeg"
            except OSError:
                pass
        if self.ffmpegLocation is None:
            raise FileNotFoundError(f'Make ffmpeg available in PATH or in "{osPath.split(__file__)[0]}"')

        self.processes = {}
        self.lastDownload = 0
        self.commands = {
            "state": [None, ytdl.state],
            "download": [None, ytdl.download],
            "remove": [None, ytdl.rem],
        }

        if not return_var is None:
            return_var[0] = self

    def verify(file: str, obj: dict):
        for mainObj in obj:
            for check in ytdl.requiredFiles[file]:
                if not check in obj[mainObj]:
                    raise SyntaxError(f"Missing record {check} ({str(mainObj)})")

                if not ytdl.requiredFiles[file][check] is type(obj[mainObj][check]):
                    raise SyntaxError(f"Type mismatch record for {check} {str(ytdl.requiredFiles[file][check])} != {str(type(obj[mainObj][check]))}")

            for check in obj[mainObj]:
                if not check in ytdl.requiredFiles[file]:
                    raise SyntaxError(f"Additional record {check} ({str(mainObj)})")

    def load(clT, file: str):
        workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{clT.token}/{ytdl.mainFolder}'

        fileData = None
        for i in range(0, 10):
            try:
                with open(f"{workFolder}{file}", "r", encoding="UTF-8") as fileR:
                    fileData = load(fileR)
                    break
            except JSONDecodeError:
                sleep(1)

        if fileData is None:
            raise Exception(f"Failed to load file: {workFolder}{file}")
        return fileData

    def write(clT, file: str, obj: dict):
        workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{clT.token}/{ytdl.mainFolder}'

        if not type(ytdl.requiredFiles[file][tuple(ytdl.requiredFiles[file])[-1]]) is dict:
            ytdl.verify(file, obj)
            with open(f"{workFolder}{file}", "w", encoding="UTF-8") as fileW:
                dump(obj, fileW, indent=2)
            return obj

        objSort = {}
        for tag in obj:
            objSort[tag] = {}
            for key in ytdl.requiredFiles[file]:
                if key in obj[tag]:
                    objSort[tag][key] = obj[tag][key]
        objSort = dict(sorted(objSort.items()))

        try:
            objSort = dict(sorted(objSort.items(), key=lambda x: int(x[0])))
        except ValueError:
            objSort = dict(sorted(objSort.items()))

        ytdl.verify(file, objSort)
        with open(f"{workFolder}{file}", "w", encoding="UTF-8") as fileW:
            dump(objSort, fileW, indent=2)

        return objSort

    def updateState(clT, index: int, title: str = None, link: str = None, URL: bool = None, hasVideo: bool = None, hasAudio: bool = None, resolution: str = None, audioBitrate: str = None, state: str = None, error: str = None, remove: bool = False):
        data = ytdl.load(clT, "/Downloads.json")

        if remove:
            if f"{index}" in data:
                data.pop(f"{index}")

            ytdl.write(clT, "/Downloads.json", data)

        if not f"{index}" in data:
            data[f"{index}"] = {"Title": "", "Link": "", "URL": "", "HasVideo": False, "HasAudio": False, "Resolution": "", "AudioBitrate": "", "State": "", "Error": "", "Modified": int(datetime.now().timestamp())}

        for key, value in (("Title", title), ("Link", link), ("URL", URL), ("HasVideo", hasVideo), ("HasAudio", hasAudio), ("Resolution", resolution), ("AudioBitrate", audioBitrate), ("State", state), ("Error", error)):
            if value is None:
                continue

            data[f"{index}"][key] = value

        ytdl.write(clT, "/Downloads.json", data)

    def downloadYT(clT, index, url, quality, format, audioOnly):
        workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/srvcoms", "")}/user/{clT.token}/{ytdl.mainFolder}'
        yt = YouTube(url)

        try:
            yt.check_availability()
            yt.streams.filter(file_extension=format, only_audio=True, only_video=False)
        except (VideoUnavailable, VideoRegionBlocked, VideoPrivate, AgeRestrictedError) as err:
            ytdl.updateState(clT, index, state="Failed", error=str(err))
            raise Exception(str(err))

        selectedAudio = None
        for stream in yt.streams.filter(file_extension=format, only_audio=True, only_video=False):
            if selectedAudio is None:
                selectedAudio = stream

            if quality == "low" and int(stream.abr.replace("kbps", "")) < int(selectedAudio.abr.replace("kbps", "")):
                selectedAudio = stream

            elif quality == "medium" and stream.abr == "160kbps":
                selectedAudio = stream
                break

            elif quality == "high" and int(stream.abr.replace("kbps", "")) > int(selectedAudio.abr.replace("kbps", "")):
                selectedAudio = stream

        if audioOnly:
            title = selectedAudio.title
            for char in punctuation:
                title = title.replace(char, "")

            ytdl.updateState(clT, index, title=title, hasVideo=False, hasAudio=True, audioBitrate=selectedAudio.abr, state="Downloading Audio")

            fileAudio = selectedAudio.download(f"{workFolder}/temp", f'{title}_{index}.{selectedAudio.mime_type.split("/")[-1]}', skip_existing=False)
            move(fileAudio, f'{clT.ytdl.mediaPath}/{sub("[^A-Za-z0-9.]", "!", fileAudio.split("/")[-1].replace(".audio.tmp", ""))}')

            with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "") + "/server/config.json", "r", encoding="UTF-8") as fileR:
                fileData = load(fileR)
            ytdl.updateState(clT, index, link=f'https://pydoc.{fileData["Domain"]}/YTDL/{sub("[^A-Za-z0-9.]", "!", fileAudio.split("/")[-1].replace(".video.tmp", ""))}', state="Done")

            return f'{clT.ytdl.mediaPath}/{sub("[^A-Za-z0-9.]", "!", fileAudio.split("/")[-1].replace(".audio.tmp", ""))}', None

        selectedVideo = None
        for stream in yt.streams.filter(file_extension=format, only_audio=False, only_video=True):
            if selectedVideo is None:
                selectedVideo = stream

            if quality == "low" and int(stream.resolution.replace("p", "")) < int(selectedVideo.resolution.replace("p", "")):
                selectedVideo = stream

            elif quality == "medium" and stream.resolution == "1080p":
                selectedVideo = stream
                break

            elif quality == "high" and int(stream.resolution.replace("p", "")) > int(selectedVideo.resolution.replace("p", "")):
                selectedVideo = stream

        title = selectedVideo.title
        for char in punctuation:
            title = title.replace(char, "")

        ytdl.updateState(clT, index, title=title, hasVideo=True, hasAudio=True, resolution=selectedVideo.resolution, audioBitrate=selectedAudio.abr, state="Downloading Audio")
        fileAudio = selectedAudio.download(f"{workFolder}/temp", f'{title}_{index}.{selectedAudio.mime_type.split("/")[-1]}.audio.tmp', skip_existing=False)
        ytdl.updateState(clT, index, state="Downloading Video")
        fileVideo = selectedVideo.download(f"{workFolder}/temp", f'{title}_{index}.{selectedVideo.mime_type.split("/")[-1]}.video.tmp', skip_existing=False)

        return fileAudio, fileVideo

    def merge(clT, index, fileAudio, fileVideo):
        with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "") + "/server/config.json", "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)
        ytdl.updateState(clT, index, link=f'https://pydoc.{fileData["Domain"]}/YTDL/{sub("[^A-Za-z0-9.]", "!", fileVideo.split("/")[-1].replace(".video.tmp", ""))}', state="Merging")

        try:
            stdout, stderr = (
                ffmpeg.concat(ffmpeg.input(fileVideo), ffmpeg.input(fileAudio), v=1, a=1)
                .output(f'{clT.ytdl.mediaPath}/{sub("[^A-Za-z0-9.]", "!", fileVideo.split("/")[-1].replace(".video.tmp", ""))}', threads=1)
                .overwrite_output()
                .run(cmd=f"{clT.ytdl.ffmpegLocation}", quiet=True)
            )
            ytdl.updateState(clT, index, state="Done")
        except ffmpeg._run.Error as err:
            ytdl.updateState(clT, index, state="Failed", error=str(err.stderr))

        try:
            remove(fileAudio)
            remove(fileVideo)
        except FileNotFoundError as err:
            ytdl.updateState(clT, index, state="Failed", error=err)
            return ytdl.getState(clT)

    def getState(clT):
        data = ytdl.load(clT, "/Downloads.json")

        if data == {}:
            return {"downloads": {}, "history": {}}

        for index in data:
            if data[index]["State"] in ["Done", "Failed"]:
                continue

            if (datetime.now() - timedelta(hours=1)).timestamp() > data[index]["Modified"]:
                ytdl.updateState(clT, index, state="Failed", error="Timeout (When downloading a lot it's possible this still gets completed)")

        data = ytdl.load(clT, "/Downloads.json")

        downloads = {}
        history = {}

        for index in data:
            if (datetime.now() - timedelta(days=1)).timestamp() < data[index]["Modified"]:
                downloads[index] = data[index]
                continue

            history[index] = data[index]

        return {"downloads": downloads, "history": history}

    async def state(clT):
        return ytdl.getState(clT)

    async def download(clT, audioOnlyStr: str, quality: str, url: str):
        if not quality.lower() in ["low", "medium", "high"]:
            raise Exception(f"Not a valid quality: {quality}.")

        if not audioOnlyStr.lower() in ["video", "audio"]:
            raise Exception(f"Not a valid type: {audioOnlyStr}.")

        audioOnly = False
        if audioOnlyStr == "audio":
            audioOnly = True

        if not url.startswith("https://www.youtube.com/watch?v=") and not url.startswith("https://www.youtube.com/shorts/"):
            raise Exception(f"Not a valid URL: {url}.")

        if (datetime.now() - timedelta(seconds=15)).timestamp() < clT.ytdl.lastDownload:
            raise Exception("Please wait 15 seconds until starting the next download.")

        clT.ytdl.lastDownload = datetime.now().timestamp()
        data = ytdl.getState(clT)

        for index in data["downloads"]:
            if data["downloads"][index]["State"] == "Failed":
                continue

            if url == data["downloads"][index]["URL"] and (datetime.now() - timedelta(minutes=1)).timestamp() < data["downloads"][index]["Modified"]:
                raise Exception("Please wait 1 minute until starting the next download of the same URL.")

        fileData = ytdl.load(clT, "/Downloads.json")
        try:
            index = int(list(fileData)[-1]) + 1
        except IndexError:
            index = 0

        while True:
            if index in fileData:
                index += 1
                continue
            break

        ytdl.updateState(clT, index, URL=url, state="Starting")
        clT.ytdl.processes[str(index)] = Process(target=ytdl.main, args=(clT, index, url, quality.lower(), None, audioOnly))
        clT.ytdl.processes[str(index)].start()

        return ytdl.getState(clT)

    async def rem(clT, index: str):
        data = ytdl.load(clT, "/Downloads.json")
        for ind in dict(data):
            if not index in ind:
                continue

            try:
                remove(f'{clT.ytdl.mediaPath}/{data[index]["Link"].split("/")[-1]}')
            except (FileNotFoundError, IsADirectoryError):
                pass

            data.pop(index)
            ytdl.write(clT, "/Downloads.json", data)

            return ytdl.getState(clT)

        return ytdl.getState(clT)

    def main(clT, index: int, url: str, quality: str = "medium", format: str = None, audioOnly: bool = False):
        if platform == "win32":
            psProcess().nice(BELOW_NORMAL_PRIORITY_CLASS)
            psProcess().ionice(IOPRIO_LOW)
        else:
            psProcess().nice(20)
            psProcess().ionice(IOPRIO_CLASS_IDLE)

        try:
            fileAudio, fileVideo = ytdl.downloadYT(clT, index, url, quality, format, audioOnly)
        except Exception:
            clT.ytdl.processes[str(index)].close()
            clT.ytdl.processes.pop(str(index))
            exit(0)

        if not audioOnly:
            ytdl.merge(clT, index, fileAudio, fileVideo)

        clT.ytdl.processes[str(index)].close()
        clT.ytdl.processes.pop(str(index))
        exit(0)

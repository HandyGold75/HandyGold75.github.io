from WebKit import HTML, CSS, JS, WS
from json import dumps, loads


class glb:
    allLinks = {}

    defaultLinks = {
        "Outlook.png": {
            "url": "https://outlook.office.com/",
            "text": "Outlook",
            "cat": "Microsoft/ Google",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "OutlookCalendar.png": {
            "url": "https://outlook.office.com/calendar/",
            "text": "Outlook Calendar",
            "cat": "Microsoft/ Google",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "OneDrive.png": {
            "url": "https://www.office.com/login?ru=%2Flaunch%2Fonedrive",
            "text": "OneDrive",
            "cat": "Microsoft/ Google",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "G-Mail.png": {
            "url": "https://mail.google.com/",
            "text": "Google Mail",
            "cat": "Microsoft/ Google",
            "Index": 104,
            "Active": True,
            "Modified": 0
        },
        "G-Drive.png": {
            "url": "https://drive.google.com/",
            "text": "Google Drive",
            "cat": "Microsoft/ Google",
            "Index": 105,
            "Active": True,
            "Modified": 0
        },
        "G-Photos.png": {
            "url": "https://photos.google.com/",
            "text": "Google Photos",
            "cat": "Microsoft/ Google",
            "Index": 106,
            "Active": True,
            "Modified": 0
        },
        "G-Calendar.png": {
            "url": "https://calendar.google.com/",
            "text": "Google Calendar",
            "cat": "Microsoft/ Google",
            "Index": 107,
            "Active": True,
            "Modified": 0
        },
        "YouTube.png": {
            "url": "https://www.youtube.com/",
            "text": "YouTube",
            "cat": "Media",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "YouTubeMusic.png": {
            "url": "https://music.youtube.com/",
            "text": "YouTube Music",
            "cat": "Media",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "Spotify.png": {
            "url": "https://open.spotify.com/",
            "text": "Spotify",
            "cat": "Media",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "GitHub.png": {
            "url": "https://github.com/",
            "text": "GitHub",
            "cat": "Management",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "Linode.png": {
            "url": "https://cloud.linode.com/",
            "text": "Linode Cloud",
            "cat": "Management",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "UniFi.png": {
            "url": "https://unifi.ui.com/",
            "text": "UniFi Portal",
            "cat": "Management",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "Cloudflare.png": {
            "url": "https://dash.cloudflare.com/",
            "text": "CloudFlare",
            "cat": "Management",
            "Index": 104,
            "Active": True,
            "Modified": 0
        },
        "Sophos.png": {
            "url": "https://my.sophos.com/",
            "text": "Sophos Home",
            "cat": "Management",
            "Index": 105,
            "Active": True,
            "Modified": 0
        },
        "Nord.png": {
            "url": "https://my.nordaccount.com/",
            "text": "Nord Account",
            "cat": "Management",
            "Index": 106,
            "Active": True,
            "Modified": 0
        },
        "OneTimeSecret.png": {
            "url": "https://onetimesecret.com/",
            "text": "One Time Secret",
            "cat": "Tools",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "SpeedTest.png": {
            "url": "https://www.speedtest.net/",
            "text": "SpeedTest Ookla",
            "cat": "Tools",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "DownDetector.png": {
            "url": "https://downdetector.com/",
            "text": "Down Detector",
            "cat": "Tools",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "CloudConvert.png": {
            "url": "https://cloudconvert.com/",
            "text": "Cloud Convert",
            "cat": "Tools",
            "Index": 104,
            "Active": True,
            "Modified": 0
        },
        "NS.png": {
            "url": "https://www.ns.nl/",
            "text": "NS",
            "cat": "Stores",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "Vodafone.png": {
            "url": "https://www.Vodafone.nl/my",
            "text": "Vodafone",
            "cat": "Stores",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "SokPop.png": {
            "url": "https://sokpop.co/patreon",
            "text": "SokPop",
            "cat": "Stores",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "LinusTechTips.png": {
            "url": "https://www.lttstore.com/",
            "text": "Linus Tech Tips",
            "cat": "Stores",
            "Index": 104,
            "Active": True,
            "Modified": 0
        },
        "Megekko.png": {
            "url": "https://www.megekko.nl/",
            "text": "Megekko",
            "cat": "Stores",
            "Index": 105,
            "Active": True,
            "Modified": 0
        },
        "Bol.png": {
            "url": "https://www.bol.com/",
            "text": "Bol",
            "cat": "Stores",
            "Index": 106,
            "Active": True,
            "Modified": 0
        },
        "Dell.png": {
            "url": "https://www.dell.com/",
            "text": "Dell",
            "cat": "Stores",
            "Index": 107,
            "Active": True,
            "Modified": 0
        },
        "Zwoofs.png": {
            "url": "https://www.zwoofs.nl/",
            "text": "Zwoofs",
            "cat": "Stores",
            "Index": 108,
            "Active": True,
            "Modified": 0
        },
        "RockStar.png": {
            "url": "https://socialclub.rockstargames.com/events?gameId=GTAV",
            "text": "RockStar GTA V Events",
            "cat": "Other",
            "Index": 101,
            "Active": True,
            "Modified": 0
        }
    }

    columns = 4


def setup():
    glb.allLinks = dict(sorted(glb.defaultLinks.items(), key=lambda x: x[1]['Index']))

    if JS.cache("page_links") is None or JS.cache("page_links") == "":
        JS.cache("page_links", dumps({}))

    if JS.cache("page_links_colums") is None or JS.cache("page_links_colums") == "":
        JS.cache("page_links_colums", 4)

    HTML.set(f'div', f'page', _id=f'page_links', _align=f'center')

    if not WS.loggedIn:
        return None

    msgDict = WS.dict()

    if "qr" in msgDict:
        if " " in msgDict["qr"]["/Links.json"]:
            msgDict["qr"]["/Links.json"].pop(" ")

        glb.allLinks = {**glb.defaultLinks, **msgDict["qr"]["/Links.json"]}

    glb.allLinks = dict(sorted(glb.allLinks.items(), key=lambda x: x[1]['Index']))


def toggleCat(args: any):
    id = args.target.id

    if id == "":
        id = args.target.parentElement.id

    catStates = loads(JS.cache("page_links"))
    catStates[id.split("_")[2]] = not catStates[id.split("_")[2]]

    CSS.setStyle(f'page_links_{id.split("_")[2]}_header', f'borderBottom', f'2px solid #111')

    CSS.setStyle(f'page_links_{id.split("_")[2]}', f'position', f'unset')
    CSS.setStyle(f'page_links_{id.split("_")[2]}', f'marginTop', f'0px')
    CSS.setStyle(f'page_links_{id.split("_")[2]}', f'opacity', f'1')

    if not catStates[id.split("_")[2]]:
        CSS.setStyle(f'page_links_{id.split("_")[2]}_header', f'borderBottom', f'4px solid #111')

        CSS.setStyle(f'page_links_{id.split("_")[2]}', f'position', f'absolute')
        CSS.setStyle(f'page_links_{id.split("_")[2]}', f'marginTop', f'-9999px')
        CSS.setStyle(f'page_links_{id.split("_")[2]}', f'opacity', f'0')

    JS.cache("page_links", dumps(catStates))


def main():
    def newCat(cat: dict, visable: bool):
        if visable:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerBig %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 2px solid #111; user-select: none;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 1;')
        else:
            HTML.add(f'h1', f'page_links', _id=f'page_links_{cat}_header', _nest=f'{cat}', _align=f'center', _style=f'headerBig %% pageLinks_Base %% border-top: 4px solid #111; border-bottom: 4px solid #111; user-select: none;')
            HTML.add(f'div', f'page_links', _id=f'page_links_{cat}', _align=f'center', _style=f'pageLinks_Base %% border-bottom: 4px solid #111; opacity: 0; margin-top: -9999px; position: absolute;')

    setup()

    catStates = loads(JS.cache("page_links"))
    catRowCount = {}
    catColCount = {}

    for link in glb.allLinks:
        currentCat = glb.allLinks[link]["cat"]

        if not currentCat in catRowCount:
            if not currentCat in catStates:
                catStates[currentCat] = True

            newCat(currentCat, catStates[currentCat])
            catRowCount[currentCat] = 0
            catColCount[currentCat] = 0

        if catColCount[currentCat] % int(JS.cache("page_links_colums")) == 0:
            catRowCount[currentCat] += 1
            HTML.add(f'div', f'page_links_{currentCat}', _id=f'page_links_{currentCat}_row{catRowCount[currentCat]}', _align=f'center', _style=f'flex')

        catColCount[currentCat] += 1

        img = HTML.getLink(glb.allLinks[link]["url"], _nest=f'<img id="Image_{glb.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.allLinks[link]["text"]}" style="width: 30%; margin: 15px auto -10px auto; user-select:none;">')
        txt = HTML.add(f'p', _nest=HTML.getLink(glb.allLinks[link]["url"], _nest=glb.allLinks[link]["text"]))
        HTML.add(f'div', f'page_links_{currentCat}_row{catRowCount[currentCat]}', _nest=f'{img}{txt}', _style=f'width: {100 / int(JS.cache("page_links_colums"))}%; margin: 0px auto;')

    for cat in catRowCount:
        JS.addEvent(f'page_links_{cat}_header', toggleCat, "click")

    JS.cache("page_links", dumps(catStates))

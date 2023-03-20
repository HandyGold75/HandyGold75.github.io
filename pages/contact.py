import mod.HTML as HTML
import mod.ws as ws
import mod.JS as JS


class glb:
    allContacts = {}

    defaultContacts = {
        "Discord.png": {
            "url": "https://discordapp.com/users/296000826588004352",
            "text": "HandyGold75#1539",
            "Index": 101,
            "Active": True,
            "Modified": 0
        },
        "Steam.png": {
            "url": "https://steamcommunity.com/id/HandyGold75",
            "text": "HandyGold75",
            "Index": 102,
            "Active": True,
            "Modified": 0
        },
        "YouTube.png": {
            "url": "https://youtube.com/@HandyGold75",
            "text": "HandyGold75",
            "Index": 103,
            "Active": True,
            "Modified": 0
        },
        "Twitch.png": {
            "url": "https://www.twitch.tv/handygold75",
            "text": "HandyGold75",
            "Index": 104,
            "Active": True,
            "Modified": 0
        },
        "Snapchat.png": {
            "url": "https://www.snapchat.com/add/handygold75",
            "text": "HandyGold75",
            "Index": 105,
            "Active": True,
            "Modified": 0
        },
        "Spotify.png": {
            "url": "https://open.spotify.com/user/11153222914",
            "text": "HandyGold75",
            "Index": 106,
            "Active": True,
            "Modified": 0
        },
        "Exchange.png": {
            "url": "mailto:IZO@HandyGold75.com",
            "text": "IZO@HandyGold75.com",
            "Index": 107,
            "Active": True,
            "Modified": 0
        }
    }


def setup():
    glb.allContacts = dict(sorted(glb.defaultContacts.items(), key=lambda x: x[1]['Index']))

    HTML.set(f'div', f'page', _id="page_contact")

    if not JS.glb.loggedIn:
        return None

    msgDict = ws.msgDict()

    if "qr" in msgDict:
        if " " in msgDict["qr"]["/Contact.json"]:
            msgDict["qr"]["/Contact.json"].pop(" ")

        glb.allContacts = {**glb.defaultContacts, **msgDict["qr"]["/Contact.json"]}

    glb.allContacts = dict(sorted(glb.allContacts.items(), key=lambda x: x[1]['Index']))


def main():
    setup()

    txt = HTML.add(f'h1', _nest=f'Contact details', _style=f'headerVeryBig %% width: 50%; min-width: 250px;')
    HTML.add(f'div', f'page_contact', _nest=txt, _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

    for contact in glb.allContacts:
        img = HTML.getLink(glb.allContacts[contact]["url"], _nest=f'<img src="docs/assets/Contact/{contact}" alt="{contact}" style="width: 100%;">', _style=f'width: 10%; min-width: 22px; margin: 10px; padding: 6px 0px 0px 0px; user-select:none;')
        txt = HTML.add(f'p', _nest=HTML.getLink(glb.allContacts[contact]["url"], _nest=glb.allContacts[contact]["text"]), _style=f'width: 90%; max-width: 150px; text-align: left; margin: auto 10px;')
        HTML.add(f'div', f'page_contact', _nest=f'{img}{txt}', _align=f'center', _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

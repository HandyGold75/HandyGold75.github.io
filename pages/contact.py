from WebKit import HTML, WS
from json import load
from os import path as osPath


class glb:
    allContacts = {}

    with open(f'{osPath.split(__file__)[0]}/config.json', "r", encoding="UTF-8") as fileR:
        defaultContacts = load(fileR)["defaultContacts"]


def setup():
    glb.allContacts = dict(sorted(glb.defaultContacts.items(), key=lambda x: x[1]['Index']))

    HTML.set(f'div', f'page', _id="page_contact")

    if not WS.glb.loggedIn:
        return None

    msgDict = WS.dict()

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

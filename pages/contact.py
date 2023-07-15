from WebKit import HTML
from WebKit.WebSocket import WS
from json import load
from os import path as osPath


class glb:
    allContacts = {}

    with open(f'{osPath.split(__file__)[0]}/config.json', "r", encoding="UTF-8") as fileR:
        defaultContacts = load(fileR)["defaultContacts"]


def setup():
    glb.allContacts = dict(sorted(glb.defaultContacts.items(), key=lambda x: x[1]['Index']))

    HTML.setElement(f'div', f'page', id="page_contact")

    if not WS.loggedIn:
        return None

    msgDict = WS.dict()

    if "qr" in msgDict:
        if " " in msgDict["qr"]["/Contact.json"]:
            msgDict["qr"]["/Contact.json"].pop(" ")

        glb.allContacts = {**glb.defaultContacts, **msgDict["qr"]["/Contact.json"]}

    glb.allContacts = dict(sorted(glb.allContacts.items(), key=lambda x: x[1]['Index']))


def main():
    setup()

    txt = HTML.genElement(f'h1', nest=f'Contact details', style=f'headerVeryBig %% width: 50%; min-width: 250px;')
    HTML.addElement(f'div', f'page_contact', nest=txt, style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

    for contact in glb.allContacts:
        img = HTML.linkWrap(glb.allContacts[contact]["url"], nest=f'<img src="docs/assets/Contact/{contact}" alt="{contact}" style="width: 100%;">', style=f'width: 10%; min-width: 22px; margin: 10px; padding: 6px 0px 0px 0px; user-select:none;')
        txt = HTML.genElement(f'p', nest=HTML.linkWrap(glb.allContacts[contact]["url"], nest=glb.allContacts[contact]["text"]), style=f'width: 90%; max-width: 150px; text-align: left; margin: auto 10px;')
        HTML.addElement(f'div', f'page_contact', nest=f'{img}{txt}', align=f'center', style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

import mod.HTML as HTML
from json import load


class glb:
    allContacts = {}


def setup():
    file_R = open(f'pages/contact.json', "r", encoding="UTF-8")
    glb.allContacts = load(file_R)
    file_R.close()

    HTML.set(f'div', f'page', _id="page_contact")


def main():
    setup()

    txt = HTML.add(f'h1', _nest=f'Contact details', _style=f'headerBig %% width: 50%; min-width: 250px;')
    HTML.add(f'div', f'page_contact', _nest=txt, _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

    for contact in glb.allContacts:
        img = HTML.getLink(glb.allContacts[contact]["url"], _nest=f'<img src="docs/assets/Contact/{contact}" alt="{glb.allContacts[contact]["text"]}" style="width: 25%; min-width: 22px; margin: 10px;">')
        txt = HTML.add(f'p', _nest=HTML.getLink(glb.allContacts[contact]["url"], _nest=glb.allContacts[contact]["text"]), _style=f'width: 75%; max-width: 150px; text-align: left; margin: auto 0px; text-decoration-line: underline; user-select:none;')
        HTML.add(f'div', f'page_contact', _nest=f'{img}{txt}', _align=f'center', _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

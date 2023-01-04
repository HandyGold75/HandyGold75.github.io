import mod.func as func
from json import load
from js import console


class glb:
    allContacts = {}


def setup():
    file_R = open(f'pages/contact.json', "r", encoding="UTF-8")
    glb.allContacts = load(file_R)
    file_R.close()

    func.setHTML(f'div', f'page', _id="page_contact")


def main():
    setup()

    txt = func.addHTML(f'h1', _nest=f'Contact details', _style=f'headerBig %% width: 50%; min-width: 250px;')
    func.addHTML(f'div', f'page_contact', _nest=txt, _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

    for contact in glb.allContacts:
        img = func.makeLink(glb.allContacts[contact]["url"], _nest=f'<img src="docs/assets/Contact/{contact}" alt="{glb.allContacts[contact]["text"]}" style="width: 25%; min-width: 22px; margin: 10px;">')
        txt = func.addHTML(f'p', _nest=func.makeLink(glb.allContacts[contact]["url"], _nest=glb.allContacts[contact]["text"]), _style=f'width: 75%; max-width: 150px; text-align: left; margin: auto 0px; text-decoration-line: underline; user-select:none;')
        func.addHTML(f'div', f'page_contact', _nest=f'{img}{txt}', _align=f'center', _style=f'flex %% width: 50%; margin: 4px auto 0px auto; justify-content: center; border-bottom: 2px dashed #111;')

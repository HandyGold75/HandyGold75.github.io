from json import load
from js import document, window, console


class glb:
    allContacts = {}


def setup():
    file_R = open(f'pages/contact.json', "r", encoding="UTF-8")
    glb.allContacts = load(file_R)
    file_R.close()

    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_contact"></div>'


def main():
    setup()

    el = document.getElementById(f'page_contact')
    txt = f'<h1 style="width: 50%; min-width: 250px; text-align: center; margin: 10px auto; color: #55F;"><b>Contact details</b></h1>'
    el.innerHTML += f'<div style="width: 50%; margin: 4px auto 0px auto; display: flex; justify-content: center; border-bottom: 2px dashed #111;">{txt}</div>'

    for contact in glb.allContacts:
        img = f'<a href="{glb.allContacts[contact]["url"]}" target="_blank"><img src="docs/assets/Contact/{contact}" alt="{glb.allContacts[contact]["text"]}" style="width: 25%; min-width: 22px; margin: 10px;"></a>'
        txt = f'<p style="width: 75%; max-width: 150px; text-align: left; margin: auto 0px;"><u><a href="{glb.allContacts[contact]["url"]}" target="_blank" style="color: #44F;">{glb.allContacts[contact]["text"]}</a></u></p>'
        el.innerHTML += f'<div align="center" style="width: 50%; margin: 4px auto 0px auto; display: flex; justify-content: center; border-bottom: 2px dashed #111;">{img}{txt}</div>'

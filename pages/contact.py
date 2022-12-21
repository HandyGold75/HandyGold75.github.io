from js import document, window, console


class glb:
    allContacts = {
        "discord.ico": {
            "url": "https://discordapp.com/users/296000826588004352",
            "text": "HandyGold75#1539"
        },
        "steam.ico": {
            "url": "https://steamcommunity.com/id/HandyGold75",
            "text": "HandyGold75"
        },
        "youtube.ico": {
            "url": "https://youtube.com/@HandyGold75",
            "text": "HandyGold75"
        },
        "twitch.ico": {
            "url": "https://www.twitch.tv/handygold75",
            "text": "HandyGold75"
        },
        "snapchat.ico": {
            "url": "https://www.snapchat.com/add/handygold75",
            "text": "HandyGold75"
        },
        "spotify.ico": {
            "url": "https://open.spotify.com/user/11153222914",
            "text": "HandyGold75"
        },
        "exchange.ico": {
            "url": "mailto:IanZoontjens@gmail.com",
            "text": "IanZoontjens@gmail.com"
        }
    }


def main():
    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_contact" align="left"></div>'

    el = document.getElementById(f'page_contact')
    el.innerHTML += f'<div class=page_contact_list><h1 style="width: 50%; min-width: 250px; text-align: center; margin: 10px auto;"><b>Contact details</b></h1></div>'

    for contact in glb.allContacts:
        img = f'<a href="{glb.allContacts[contact]["url"]}" target="_blank"><img src="docs/assets/Contact/{contact}" alt="{glb.allContacts[contact]["text"]}" style="width: 25%; margin: 10px;"></a>'
        txt = f'<p style="width: 75%; max-width: 150px; text-align: left; margin: auto 0px;"><u><a href="{glb.allContacts[contact]["url"]}" target="_blank">{glb.allContacts[contact]["text"]}</a></u></p>'
        el.innerHTML += f'<div class=page_contact_list align="center">{img}{txt}</div>'

    els = document.getElementsByClassName(f'page_contact_list')

    for i in range(0, els.length):
        console.log(str(els.item(i).style))
        els.item(i).style = f'width: 50%; margin: 4px auto 0px auto; display: flex; justify-content: center; border-bottom: 2px dashed #111;'

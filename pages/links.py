from js import document, window, console


class glb:
    allLinks = {
        "G-Mail.png": {
            "url": "https://mail.google.com/",
            "text": "Google Mail"
        },
        "G-Drive.png": {
            "url": "https://drive.google.com/",
            "text": "Google Drive"
        },
        "G-Photos.png": {
            "url": "https://photos.google.com/",
            "text": "Google Photos"
        },
        "G-Calendar.png": {
            "url": "https://calendar.google.com/",
            "text": "Google Calendar"
        },
        "YouTube.png": {
            "url": "https://www.youtube.com/",
            "text": "YouTube"
        },
        "YouTubeMusic.png": {
            "url": "https://music.youtube.com/",
            "text": "YouTube Music"
        },
        "Spotify.png": {
            "url": "https://open.spotify.com/",
            "text": "Spotify"
        },
        "GitHub.png": {
            "url": "https://github.com/",
            "text": "GitHub"
        },
        "Linode.png": {
            "url": "https://cloud.linode.com/",
            "text": "Linode Cloud"
        },
        "UniFi.png": {
            "url": "https://unifi.ui.com/",
            "text": "UniFi Portal"
        },
        "FreeNom.png": {
            "url": "https://my.freenom.com/",
            "text": "FreeNom"
        },
        "Sophos.png": {
            "url": "https://my.sophos.com/",
            "text": "Sophos Home"
        },
        "Nord.png": {
            "url": "https://my.nordaccount.com/",
            "text": "Nord Account"
        },
        "OneTimeSecret.png": {
            "url": "https://onetimesecret.com/",
            "text": "One Time Secret"
        },
        "RockStar.png": {
            "url": "https://socialclub.rockstargames.com/events?gameId=GTAV",
            "text": "RockStar GTA V Events"
        },
        "NS.png": {
            "url": "https://www.ns.nl/",
            "text": "NS"
        },
        "SokPop.png": {
            "url": "https://sokpop.co/patreon",
            "text": "SokPop"
        },
        "LinusTechTips.png": {
            "url": "https://www.lttstore.com/",
            "text": "Linus Tech Tips"
        },
        "Megekko.png": {
            "url": "https://www.megekko.nl/",
            "text": "Megekko"
        },
        "Bol.png": {
            "url": "https://www.bol.com/",
            "text": "Bol"
        },
        "Zwoofs.png": {
            "url": "https://www.zwoofs.nl/",
            "text": "Zwoofs"
        }
    }

    columns = 4


def main():
    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_links" align="left" style="justify-content: center;"></div>'

    for i, link in enumerate(glb.allLinks):
        if i % glb.columns == 0:
            el = document.getElementById(f'page_links')
            el.innerHTML += f'<div id=page_links_row{int(i / glb.columns)} align="center" style="display: flex;"></div>'
            el = document.getElementById(f'page_links_row{int(i / glb.columns)}')

        img = f'<a href="{glb.allLinks[link]["url"]}" target="_blank"><img id="Image_{glb.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{glb.allLinks[link]["text"]}" style="width: 30%; margin: 15px auto -10px auto;"></a>'
        txt = f'<p><u><a href="{glb.allLinks[link]["url"]}" target="_blank">{glb.allLinks[link]["text"]}</a></u></p>'
        el.innerHTML += f'<div style="width: {100 / glb.columns}%;">{img}{txt}</div>'

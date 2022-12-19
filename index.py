from modules.WS import ws
from modules.SubPortal import SP, func
from rsa import encrypt
from js import document, window, console


class home:
    def main():
        element = document.getElementById(f'page')
        element.innerHTML = f'<p>Page content for home.</p>'


class links:
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
        }
    }

    columns = 4

    def main():
        element = document.getElementById(f'page')
        element.innerHTML = f'<div id="page_links" align="left" style="justify-content: center;"></div>'

        for i, link in enumerate(links.allLinks):
            if i % links.columns == 0:
                element = document.getElementById(f'page_links')
                element.innerHTML += f'<div id=page_links_row{int(i / links.columns)} align="center" style="display: flex;"></div>'
                element = document.getElementById(f'page_links_row{int(i / links.columns)}')

            img = f'<a href="{links.allLinks[link]["url"]}" target="_blank"><img id="Image_{links.allLinks[link]["text"]}" src="docs/assets/Links/{link}" alt="{links.allLinks[link]["text"]}" style="width: 30%; margin-top: 15px;"></a>'
            txt = f'<p><u><a href="{links.allLinks[link]["url"]}" target="_blank">{links.allLinks[link]["text"]}</a></u></p>'
            element.innerHTML += f'<div style="width: {100 / links.columns}%;">{img}{txt}</div>'

            img = document.getElementById(f'Image_{links.allLinks[link]["text"]}')

            if img.clientHeight == 0:
                img.style.marginBottom = f'{-3.25 * (8 - links.columns)}px'
                continue

            img.style.marginBottom = f'{80 - img.clientHeight - (links.columns * 10)}px'


class portal:
    allPages = {"Admin": SP.page, "Asset Manager": SP.page, "License Manager": SP.page}
    scriptFunctions = {"Admin": func.invoke_AP, "Asset Manager": func.invoke_AM, "License Manager": func.invoke_LM}

    def page(args=None, page=None):
        element = document.getElementById(f'page_portal_body')
        element.innerHTML = f''

        if page in portal.allPages:
            window.localStorage.setItem("page_portal", page)

        elif args.target.id.split("_")[-1] in portal.allPages:
            window.localStorage.setItem("page_portal", args.target.id.split("_")[-1])

        else:
            return None

        element.innerHTML = f'<div id="SubPage" align="left"></div>'
        document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}'

        element = document.getElementById(f'nav_title')
        element.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}</h1>'

        portal.allPages[window.localStorage.getItem("page_portal")]()

    def main():
        ws.start()

        element = document.getElementById(f'page')
        element.innerHTML = f'<div id="page_portal" align="left"></div>'

        element = document.getElementById("page_portal")
        element.innerHTML += f'<div id="page_portal_buttons" align="left"></div>'
        element.innerHTML += f'<div id="page_portal_body" align="left"></div>'

        element = document.getElementById(f'page_portal_buttons')

        for page in portal.allPages:
            element.innerHTML += f'<button id="page_portal_{page}" type="button" disabled>{page}</button>'

        def login(args):
            if args.key != "Enter":
                return None

            if checkLogin() is True:
                return None

            element = document.getElementById("page_portal_body_login_usr")
            usr = element.value

            element = document.getElementById("page_portal_body_login_psw")
            psw = element.value

            crypt = str(encrypt(usr.encode() + psw.encode(), func.pk))

            try:
                ws.send(crypt)
            except ConnectionError:
                func.connectionError()

        def checkLogin(args=None):
            if window.localStorage.getItem("page_index") != "Portal":
                return None

            try:
                msg = ws.msg()
            except ConnectionError:
                func.connectionError()
                return None

            if msg == f'<LOGIN_TOKEN_FAIL>':
                window.localStorage.setItem("token", "")
                setup.loggedIn = False

                element = document.getElementById(f'page_portal_body_login_usr')
                element.disabled = False

                element = document.getElementById(f'page_portal_body_login_psw')
                element.disabled = False

                return None

            elif msg == f'<LOGIN_TOKEN_SUCCESS>':
                setup.loggedIn = True

            elif msg.startswith(f'<LOGIN_SUCCESS> '):
                setup.loggedIn = True
                window.localStorage.setItem("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

            elif msg == " ":
                setup.loggedIn = True

            if setup.loggedIn:
                element = document.getElementById(f'page')
                element.outerHTML = element.outerHTML

                setup.page(page=window.localStorage.getItem("page_index"))

                return True

            if window.localStorage.getItem("token") != "":
                element = document.getElementById(f'page_portal_body_login_usr')
                element.disabled = True

                element = document.getElementById(f'page_portal_body_login_psw')
                element.disabled = True

                try:
                    ws.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')
                except ConnectionError:
                    func.connectionError()

        def logout(args=None):
            try:
                ws.send(f'logout')
            except ConnectionError:
                func.connectionError()

            window.localStorage.setItem("token", "")
            setup.loggedIn = False

            window.location.reload()

        if not setup.loggedIn:
            element = document.getElementById("page_portal_body")
            element.innerHTML += f'<h1>Login</h1>'
            element.innerHTML += f'<form id="page_portal_body_login" onsubmit="return false"></form>'
            element.innerHTML += f'<div id="page_portal_body_buttons" align="center"></div>'

            element = document.getElementById("page_portal_body_login")
            element.innerHTML += f'<div id="page_portal_body_login_txt" align="center"></div>'
            element.innerHTML += f'<div id="page_portal_body_login_inp" align="center"></div>'

            element = document.getElementById("page_portal_body_login_txt")
            element.innerHTML += f'<p>Username</p>'
            element.innerHTML += f'<p>Password</p>'

            element = document.getElementById("page_portal_body_login_inp")
            element.innerHTML += f'<input id="page_portal_body_login_usr"></input>'
            element.innerHTML += f'<input id="page_portal_body_login_psw" type="password"></input>'

            func.addEvent(f'page', checkLogin, f'mouseover')
            func.addEvent(f'page_portal_body_login_usr', login, f'keyup')
            func.addEvent(f'page_portal_body_login_psw', login, f'keyup')

            return None

        for page in portal.allPages:
            element = document.getElementById(f'page_portal_body')
            element.innerHTML = f'<div id="page_portal_body_logout" align="center"></div>'

            element = document.getElementById(f'page_portal_body_logout')
            element.innerHTML += f'<button id="page_portal_body_logout_submit" type="button">Logout</button>'

            func.addEvent(f'page_portal_{page}', portal.page)
            func.addEvent(f'page_portal_{page}', portal.scriptFunctions[page], f'mousedown')
            func.addEvent(f'page_portal_body_logout_submit', logout)

            element = document.getElementById(f'page_portal_{page}')
            element.disabled = False


class contact:
    def main():
        element = document.getElementById(f'page')
        element.innerHTML = f'<div id="page_contact" align="left"></div>'

        element = document.getElementById(f'page_contact')
        element.innerHTML += f'<div class=page_contact_list><h1 style="width: 50%; min-width: 250px; text-align: center; margin: 10px auto;"><b>Contact details</b></h1></div>'

        contactData = {
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

        for contact in contactData:
            img = f'<a href="{contactData[contact]["url"]}" target="_blank"><img src="docs/assets/Contact/{contact}" alt="{contactData[contact]["text"]}" style="width: 25%; margin: 10px;"></a>'
            txt = f'<p style="width: 75%; max-width: 150px; text-align: left; margin: auto 0px;"><u><a href="{contactData[contact]["url"]}" target="_blank">{contactData[contact]["text"]}</a></u></p>'
            element.innerHTML += f'<div class=page_contact_list align="center">{img}{txt}</div>'

        elements = document.getElementsByClassName(f'page_contact_list')

        for i in range(0, elements.length):
            console.log(str(elements.item(i).style))
            elements.item(i).style = f'width: 50%; margin: 4px auto 0px auto; display: flex; justify-content: center; border-bottom: 2px dashed #111;'


class setup:
    loggedIn = False

    for item in ["token", "page_index", "page_portal"]:
        if window.localStorage.getItem(item) is None:
            window.localStorage.setItem(item, "")

    def general():
        document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

        element = document.getElementById(f'body')
        element.innerHTML = f'<div id="main"></div>'

        element = document.getElementById(f'main')
        element.innerHTML = f'<div id="nav"></div><div id="page"></div><div id="footer"></div>'

    def navigation():
        element = document.getElementById(f'nav')
        element.innerHTML += f'<img src="docs/assets/;D.png" id="nav_logo" align="left"><h1 id="nav_title" align="center">HandyGold75 - {window.localStorage.getItem("page_index")}</h1><div id="nav_buttons" align="center"></div>'

        element = document.getElementById(f'nav_buttons')

        for page in setup.allPages:
            element.innerHTML += f'<button id="page_{page}" type="button">{page}</button>'

        for page in setup.allPages:
            func.addEvent(f'page_{page}', setup.page)

    def page(args=None, page=None):
        element = document.getElementById(f'page')
        element.innerHTML = f''

        if page in setup.allPages:
            window.localStorage.setItem("page_index", page)

        elif args.target.id.split(f'_')[-1] in setup.allPages:
            window.localStorage.setItem("page_index", args.target.id.split(f'_')[-1])

        else:
            return None

        window.localStorage.setItem("page_portal", "")
        document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")}'

        element = document.getElementById(f'nav_title')
        element.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")}</h1>'

        setup.allPages[window.localStorage.getItem("page_index")]()

    def footer():
        def toTop(*args):
            document.getElementById(f'body').scrollIntoView()

        element = document.getElementById(f'footer')
        element.innerHTML = (f'<div id="footer_note"><p><b>HandyGold75 - 2022</b></p></div><div id="footer_buttons" align="right"><button id="footer_toTop" type="button">Back to top</button></div></div>')

        func.addEvent(f'footer_toTop', toTop)

    def main():
        setup.general()
        setup.navigation()
        setup.page(page=window.localStorage.getItem("page_index"))
        setup.footer()

    allPages = {"Home": home.main, "Links": links.main, "Portal": portal.main, "Contact": contact.main}


if __name__ == "__main__":
    setup.main()

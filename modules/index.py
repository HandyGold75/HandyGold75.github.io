from modules.WS import ws
from modules.SubPage import SP, func
from rsa import encrypt
from js import document, window, console


class setup:
    loggedIn = False

    if window.localStorage.getItem("token") is None:
        window.localStorage.setItem("token", "")

    def general():
        document.title = f'HandyGold75 - {pages.currentPage}'

    def navigation():
        element = document.getElementById(f'nav')
        element.innerHTML += f'<img src="docs/assets/;D.png" id="nav_logo" align="left"><h1 id="nav_title" align="center">HandyGold75 - {pages.currentPage}</h1><div id="nav_buttons" align="center"></div>'

        element = document.getElementById(f'nav_buttons')

        for page in pages.allPages:
            element.innerHTML += f'<button id="page_{page}" type="button">{page}</button>'

        for page in pages.allPages:
            func.addEvent(f'page_{page}', pages.main)

    def footer():
        element = document.getElementById(f'footer')
        element.innerHTML = (f'<div id="footer_note"><p><b>HandyGold75 - 2022</b></p></div><div id="footer_buttons" align="right"><button id="footer_toTop" type="button">Back to top</button></div></div>')

        func.addEvent(f'footer_toTop', footer_portal.toTop)

    def main():
        setup.general()
        setup.navigation()
        pages.main(page=pages.currentPage)
        setup.footer()


class pages:
    currentPage = "Home"

    def home():
        element = document.getElementById(f'page')
        element.innerHTML = f'<p>Page content for home.</p>'

    def portal():
        ws.start()

        element = document.getElementById(f'page')
        element.innerHTML = f'<div id="page_portal" align="left"></div>'

        element = document.getElementById("page_portal")
        element.innerHTML += f'<div id="page_portal_buttons" align="left"></div>'
        element.innerHTML += f'<div id="page_portal_body" align="left"></div>'

        element = document.getElementById(f'page_portal_buttons')
        for page in subPage.allPages:
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
            if pages.currentPage != "Portal":
                return None

            try:
                msg = ws.msg()
            except ConnectionError:
                func.connectionError()
                return None

            if msg == f'<LOGIN_TOKEN_FAIL>':
                window.localStorage.setItem("token", "")
                setup.loggedIn = False
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

                pages.main(page=pages.currentPage)

                return True

            if window.localStorage.getItem("token") != "":
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

        for page in subPage.allPages:
            element = document.getElementById(f'page_portal_body')
            element.innerHTML = f'<div id="page_portal_body_logout" align="center"></div>'

            element = document.getElementById(f'page_portal_body_logout')
            element.innerHTML += f'<button id="page_portal_body_logout_submit" type="button">Logout</button>'

            func.addEvent(f'page_portal_{page}', subPage.main)
            func.addEvent(f'page_portal_{page}', pages.scriptFunctions[page], f'mousedown')
            func.addEvent(f'page_portal_body_logout_submit', logout)

            element = document.getElementById(f'page_portal_{page}')
            element.disabled = False

    def contact():
        element = document.getElementById(f'page')
        element.innerHTML += f'<div id="page_contact" align="left">'

        element = document.getElementById(f'page_contact')

        element.innerHTML += f'<div class=page_contact_list><h1><b>Contact details</b></h1></div>'

        contactData = {
            "exchange.ico": {
                "url": "mailto:IanZoontjens@gmail.com",
                "text": "IanZoontjens@gmail.com"
            },
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
            }
        }

        for i in contactData:
            element.innerHTML += f'<div class=page_contact_list align="center"><img src="docs/assets/Icons/{i}"><p><u><a href="{contactData[i]["url"]}">{contactData[i]["text"]}</a></u></p></div>'

    def main(args=None, page=None):
        element = document.getElementById(f'page')
        element.innerHTML = f''

        if page in pages.allPages:
            pages.currentPage = page

        elif args.target.id.split(f'_')[-1] in pages.allPages:
            pages.currentPage = args.target.id.split(f'_')[-1]

        else:
            return None

        document.title = f'HandyGold75 - {pages.currentPage}'

        element = document.getElementById(f'nav_title')
        element.innerHTML = f'<h1>HandyGold75 - {pages.currentPage}</h1>'

        pages.allPages[pages.currentPage]()

    allPages = {"Home": home, "Portal": portal, "Contact": contact}
    scriptFunctions = {"Admin": func.invoke_AP, "Asset Manager": func.invoke_AM, "License Manager": func.invoke_LM}


class subPage:
    currentPage = ""

    def main(args=None, page=None):
        element = document.getElementById(f'page_portal_body')
        element.innerHTML = f''

        if page in subPage.allPages:
            subPage.currentPage = page

        elif args.target.id.split("_")[-1] in subPage.allPages:
            subPage.currentPage = args.target.id.split("_")[-1]

        else:
            return None

        element.innerHTML = f'<div id="SubPage" align="left"></div>'

        document.title = f'HandyGold75 - {pages.currentPage} - {subPage.currentPage}'

        element = document.getElementById(f'nav_title')
        element.innerHTML = f'<h1>HandyGold75 - {pages.currentPage} - {subPage.currentPage}</h1>'

        subPage.allPages[subPage.currentPage]()

    allPages = {"Admin": SP.page, "Asset Manager": SP.page, "License Manager": SP.page}


class footer_portal:
    def toTop(*args):
        document.getElementById(f'body').scrollIntoView()


if __name__ == "__main__":
    setup.main()

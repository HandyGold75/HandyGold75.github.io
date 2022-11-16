from wsRelay import ws
from Main_AssetManager import AM
from rsa import encrypt, PublicKey
from js import document, window, console
from pyodide.ffi import create_proxy
from os import walk


class func:
    def addEvent(id: str, func, action="click"):
        proxy = create_proxy(func)
        document.getElementById(id).addEventListener(action, proxy)

    def connectionError():
        element = document.getElementById(f'page_scripts_body')
        element.innerHTML = f'<div id="page_scripts_body_error" align="center"></div>'

        element = document.getElementById(f'page_scripts_body_error')
        element.innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! You are probably logged out!<br>Please refresh the page to try again.</p><br>'


class setup:
    loggedIn = False
    pk = PublicKey(
        17975725580318426255082147295765624015303015361719602497231012933790462235693879580362187130307063578819348335338567705110647296830122706922462277858985753916807418663775359155059872610188320580932610131649669750813854841233828756158531041784174256821099975573954534872920341091204735563674609735155365230886328225569764099100220190749309854601263231477479542538657656228075477248164911150242612255058022595583271630531937574957740889057640197605063861387428744601476627747146952083278992989884033643188605058493867723623443206205193049387986735721023723231370158070058492831123317729469188277654546977114897225138444403440484404763488252900359062156606277556273881462454700682132900566293665122593793415917496306396245694769766289157377434428292617546842809345418069309429637482719212135032501150835116958632132203299437985348946833084644910715245987521602696627857328192665936755312620767597809000086619959376727150300660078176663731141210223403780234209251726760747452546317356315404004871864255840070441131656153163327938733747321658554956837916867148392977768261809450501332458691119391299657873525192653810706009363153494395380856616333139608534198022835408820709017274233496194895658713718965362482943679407034749283305672669328250828229765188719765598395616090554409644372199205005788822144569725849378518257318799359385281740742304089043012203207090757315833795382410385714872414605971371066034681422629572254445672849310499485979905134814561918728629098272915355126315453439738702075534702666290929177330864697626107597200532737216328442694999218938113176867865482874172297137142445161550097040446308420534920219666339316839673749833944188357418385020268794629695550903965269473702504547059078067498031149096658925058636652798068077433395661533192684961900825996213912591011509835703499018540858216533684827588691036564984023994359992388733781114505117772831573454751130891256075050103442171938154332660431264950585164243096093925476801938794141572630854512014984334825819438750599965004024341493159922341794445006274654995566118300460214077412075511161181698540977050816711684965694813515198715185678618288095811937806305637976252287014606730927818130439428520119356203573068177397436647258848659927556173455871707333064805630504242580519613705444817600006146353152014424758858473533029673605478152571643653561181152156398594145488582743474039155367716449975165309811984584398398690891924952884510454449930797215394455097922506895883409901302916494995512076986478728196359060058428252757519467838794722732611686045347810271767912080044182207678353913483129629823113438113820791587878184283905176268454906351041779158933382590216398059177568853055270942077059156649685981827207451739862232562515028977633596944364071556509266121310722218226028783650241233584332498505271414144626505460338325024130616840681895382408708213628489128094251273023012874086250181912500877109239104433256351412004835767020264459805538504082187665406998198032223427723556839093765764713436949937704964091432419465151166261180178053480295497695748125437451332250448661556736139515685003382928341989,
        65537)

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

        func.addEvent(f'footer_toTop', footer_scripts.toTop)

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

    def scripts():
        ws.start()

        element = document.getElementById(f'page')
        element.innerHTML = f'<div id="page_scripts" align="left"></div>'

        element = document.getElementById("page_scripts")
        element.innerHTML += f'<div id="page_scripts_buttons" align="left"></div>'
        element.innerHTML += f'<div id="page_scripts_body" align="left"></div>'

        element = document.getElementById(f'page_scripts_buttons')
        for page in pages_scripts.allPages:
            element.innerHTML += f'<button id="page_scripts_{page}" type="button" disabled>{page}</button>'

        def login(args):
            if args.key != "Enter":
                return None

            if checkLogin() is True:
                return None

            element = document.getElementById("page_scripts_body_login_usr")
            usr = element.value

            element = document.getElementById("page_scripts_body_login_psw")
            psw = element.value

            crypt = str(encrypt(usr.encode() + psw.encode(), setup.pk))

            try:
                ws.send(crypt)
            except ConnectionError:
                func.connectionError()

        def checkLogin(args=None): #ALSO FIRES WHEN MOVING TO HOME OR CONTACT
            if pages.currentPage != "Scripts":
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
            element = document.getElementById("page_scripts_body")
            element.innerHTML += f'<h1>Login</h1>'
            element.innerHTML += f'<form id="page_scripts_body_login" onsubmit="return false"></form>'
            element.innerHTML += f'<div id="page_scripts_body_buttons" align="center"></div>'

            element = document.getElementById("page_scripts_body_login")
            element.innerHTML += f'<div id="page_scripts_body_login_txt" align="center"></div>'
            element.innerHTML += f'<div id="page_scripts_body_login_inp" align="center"></div>'

            element = document.getElementById("page_scripts_body_login_txt")
            element.innerHTML += f'<p>Username</p>'
            element.innerHTML += f'<p>Password</p>'

            element = document.getElementById("page_scripts_body_login_inp")
            element.innerHTML += f'<input id="page_scripts_body_login_usr"></input>'
            element.innerHTML += f'<input id="page_scripts_body_login_psw" type="password"></input>'

            func.addEvent(f'page', checkLogin, f'mouseover')
            func.addEvent(f'page_scripts_body_login_usr', login, f'keyup')
            func.addEvent(f'page_scripts_body_login_psw', login, f'keyup')

            return None

        for page in pages_scripts.allPages:
            element = document.getElementById(f'page_scripts_body')
            element.innerHTML = f'<div id="page_scripts_body_logout" align="center"></div>'

            element = document.getElementById(f'page_scripts_body_logout')
            element.innerHTML += f'<button id="page_scripts_body_logout_submit" type="button">Logout</button>'

            func.addEvent(f'page_scripts_{page}', pages_scripts.main)
            func.addEvent(f'page_scripts_{page}', pages.scriptFunctions[page], f'mousedown')
            func.addEvent(f'page_scripts_body_logout_submit', logout)

            element = document.getElementById(f'page_scripts_{page}')
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

    allPages = {"Home": home, "Scripts": scripts, "Contact": contact}
    scriptFunctions = {"Asset Manager": AM.getData}


class pages_scripts:
    currentPage = ""

    def main(args=None, page=None):
        element = document.getElementById(f'page_scripts_body')
        element.innerHTML = f''

        if page in pages_scripts.allPages:
            pages_scripts.currentPage = page

        elif args.target.id.split("_")[-1] in pages_scripts.allPages:
            pages_scripts.currentPage = args.target.id.split("_")[-1]

        else:
            return None

        element.innerHTML = f'<div id="{pages_scripts.currentPage}" align="left"></div>'

        document.title = f'HandyGold75 - {pages.currentPage} - {pages_scripts.currentPage}'

        element = document.getElementById(f'nav_title')
        element.innerHTML = f'<h1>HandyGold75 - {pages.currentPage} - {pages_scripts.currentPage}</h1>'

        pages_scripts.allPages[pages_scripts.currentPage]()

    allPages = {"Asset Manager": AM.page}


class footer_scripts:
    def toTop(*args):
        document.getElementById(f'body').scrollIntoView()


if __name__ == "__main__":
    setup.main()

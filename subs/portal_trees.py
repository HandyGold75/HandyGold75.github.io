import mod.func as func
import mod.ws as ws
from rsa import encrypt, PublicKey
from datetime import datetime, timedelta
from js import document, window, console


class invoke:
    def MO(args=None):
        glb.mainPage = "Monitor"
        glb.currentSub = ""

        glb.lastUpdate = 0
        glb.knownTree = {"Current": {"sId": int, "cl": dict, "wsAuth": dict, "logStack": dict}, "All": {"cl": dict, "wsAuth": dict, "logStack": dict}}

        glb.dates = ["Expires", "Modified", "time"]

        glb.svcoms = {"main": "monitor", "read": "read"}

        getData()


class glb:
    mainPage = ""
    currentSub = ""

    lastUpdate = 0
    knownTree = {}

    dates = []

    svcoms = {}

    pk = PublicKey(
        17975725580318426255082147295765624015303015361719602497231012933790462235693879580362187130307063578819348335338567705110647296830122706922462277858985753916807418663775359155059872610188320580932610131649669750813854841233828756158531041784174256821099975573954534872920341091204735563674609735155365230886328225569764099100220190749309854601263231477479542538657656228075477248164911150242612255058022595583271630531937574957740889057640197605063861387428744601476627747146952083278992989884033643188605058493867723623443206205193049387986735721023723231370158070058492831123317729469188277654546977114897225138444403440484404763488252900359062156606277556273881462454700682132900566293665122593793415917496306396245694769766289157377434428292617546842809345418069309429637482719212135032501150835116958632132203299437985348946833084644910715245987521602696627857328192665936755312620767597809000086619959376727150300660078176663731141210223403780234209251726760747452546317356315404004871864255840070441131656153163327938733747321658554956837916867148392977768261809450501332458691119391299657873525192653810706009363153494395380856616333139608534198022835408820709017274233496194895658713718965362482943679407034749283305672669328250828229765188719765598395616090554409644372199205005788822144569725849378518257318799359385281740742304089043012203207090757315833795382410385714872414605971371066034681422629572254445672849310499485979905134814561918728629098272915355126315453439738702075534702666290929177330864697626107597200532737216328442694999218938113176867865482874172297137142445161550097040446308420534920219666339316839673749833944188357418385020268794629695550903965269473702504547059078067498031149096658925058636652798068077433395661533192684961900825996213912591011509835703499018540858216533684827588691036564984023994359992388733781114505117772831573454751130891256075050103442171938154332660431264950585164243096093925476801938794141572630854512014984334825819438750599965004024341493159922341794445006274654995566118300460214077412075511161181698540977050816711684965694813515198715185678618288095811937806305637976252287014606730927818130439428520119356203573068177397436647258848659927556173455871707333064805630504242580519613705444817600006146353152014424758858473533029673605478152571643653561181152156398594145488582743474039155367716449975165309811984584398398690891924952884510454449930797215394455097922506895883409901302916494995512076986478728196359060058428252757519467838794722732611686045347810271767912080044182207678353913483129629823113438113820791587878184283905176268454906351041779158933382590216398059177568853055270942077059156649685981827207451739862232562515028977633596944364071556509266121310722218226028783650241233584332498505271414144626505460338325024130616840681895382408708213628489128094251273023012874086250181912500877109239104433256351412004835767020264459805538504082187665406998198032223427723556839093765764713436949937704964091432419465151166261180178053480295497695748125437451332250448661556736139515685003382928341989,
        65537)


def getData(args=None):
    if (datetime.now() - timedelta(seconds=1)).timestamp() > glb.lastUpdate:
        try:
            ws.send(f'{glb.svcoms["main"]} {glb.svcoms["read"]}')
        except ConnectionError:
            func.connectionError()

        glb.lastUpdate = datetime.now().timestamp()


def refresh():
    console.log("REFRESH")


def pageSub(args):
    def setup(args):
        try:
            data = ws.msgDict()[glb.svcoms["main"]]
        except ConnectionError:
            func.connectionError()
            return None

        if f'{args.target.id.split("_")[-1]}' in glb.knownTree:
            glb.currentSub = args.target.id.split("_")[-1]

        if not glb.currentSub in data:
            return None

        data = data[glb.currentSub]

        if data == {}:
            data[" "] = {}
            mainValue = list(glb.knownTree[glb.currentSub])[-1]
            data[" "] = {}

            for value in glb.knownTree[glb.currentSub][mainValue]:
                data[" "][value] = glb.knownTree[glb.currentSub][mainValue][value]()

        el = document.getElementById(f'SubPage_nav_options_refresh')
        el.disabled = False

        return data

    def addRow(rowC):
        el = document.getElementById(f'SubPage_page')
        el.innerHTML += f'<div id="SubPage_page_row{rowC}" align="left"></div>'

        el = document.getElementById(f'SubPage_page_row{rowC}')
        el.style.display = "flex"

        return el, rowC + 1

    def addTree(data):
        def recursive(data, rowC, colC, layer, prtSpc={"1": "|1", "2": "|2", "3": "|3", "4": "|4", "5": "|5", "6": "|6"}):
            if layer + 2 > colC:
                colC = layer + 2

            styleP = f'margin: -1px 0px; padding: 0px; text-align: left; font-size: 75%; white-space: nowrap; background: #1F1F1F;'

            prtChar = "├──────────────"
            prtSpc[f'{layer}'] = f'|{layer}'

            for i, record in enumerate(data):
                if len(data) - 1 == i:
                    prtChar = "└──────────────"

                    if record == list(data)[-1]:
                        prtSpc[f'{layer}'] = ""

                    console.log(f'record: {layer}')
                    console.log(f'record: {record}')
                    console.log(f'lastKey: {list(data)[-1]}')

                spacer = ""

                if layer > 1:
                    for i1 in range(1, layer):
                        spacer += f'<p class="SubPage_page_rows_p2" style="{styleP}">{prtSpc[str(i1)]}</p>'

                if layer > 0:
                    spacer += f'<p class="SubPage_page_rows_p2" style="{styleP}">{prtChar}</p>'

                if type(data[record]) is dict:

                    el, rowC = addRow(rowC)

                    el.innerHTML += f'{spacer}<p class="SubPage_page_rows_p1" style="{styleP.replace("left", "center")}">{record}</p>'

                    rowC, colC = recursive(data[record], rowC, colC, layer + 1, prtSpc)

                else:
                    el, rowC = addRow(rowC)

                    if layer > 0:
                        el.innerHTML += f'{spacer}<p class="SubPage_page_rows_p1" style="{styleP}">{record}:</p><p class="SubPage_page_rows_p1" style="{styleP}">{data[record]}</p>'
                        continue

                    el.innerHTML += f'{spacer}<p class="SubPage_page_rows_p1" style="{styleP.replace("left", "center")}">{record}:</p><p class="SubPage_page_rows_p1" style="{styleP}">{data[record]}</p>'

            return rowC, colC

        rowC, colC = recursive(data, 0, 0, 0)

        els = document.getElementsByClassName(f'SubPage_page_rows_p1')

        for i in range(0, els.length):
            els.item(i).style.width = f'{100 / colC}%'

        els = document.getElementsByClassName(f'SubPage_page_rows_p2')

        for i in range(0, els.length):
            els.item(i).style.width = f'{50/ colC}%'
            els.item(i).style.padding = f'0px 0px 0px {50 / colC}%'

        # els = document.getElementsByClassName(f'SubPage_page_bLeft')

        # for i in range(0, els.length):
        #     els.item(i).style.borderLeft = f'2px solid #44F'

        # els = document.getElementsByClassName(f'SubPage_page_bBottom')

        # for i in range(0, els.length):
        #     els.item(i).style.borderLeft = f'2px solid #44F'

    el = document.getElementById(f'SubPage_page')
    el.innerHTML = f''

    data = setup(args)

    if data is None:
        return None

    addTree(data)


def main(args=None, sub=None):
    el = document.getElementById(f'SubPage')
    el.innerHTML = f'<div id="SubPage_nav" align="center" style="width: 95%; padding: 6px 0px; margin: 0px auto 10px auto; border-bottom: 4px dotted #111; display: flex;"></div>'
    el.innerHTML += f'<div id="SubPage_page" align="center" style="margin: 10px 10px 10px 0px;"></div>'

    el = document.getElementById(f'SubPage_nav')
    el.innerHTML += f'<div id="SubPage_nav_main" align="left" style="width: 60%"></div>'
    el.innerHTML += f'<div id="SubPage_nav_options" align="right" style="width: 40%"></div>'

    el = document.getElementById(f'SubPage_nav_main')

    try:
        data = ws.msgDict()[glb.svcoms["main"]]
    except ConnectionError:
        func.connectionError()
        return None

    foundFile = False

    for tree in data:
        if tree in glb.knownTree:
            el.innerHTML += f'<button id="SubPage_nav_main_{tree}" type="button" style="border: 2px solid #44F; font-size: 75%;">{tree}</button>'
            foundFile = True

    if not foundFile:
        el = document.getElementById(f'SubPage_nav')
        el.innerHTML = f'<div id="SubPage_nav_main" align="center" style="width: 100%"></div>'

        el = document.getElementById(f'SubPage_nav_main')
        el.innerHTML += f'<h2 style="margin: 10px auto; text-align: center;">Unauthorized!</h2>'

        el = document.getElementById(f'page_portal_{glb.mainPage}')
        el.disabled = True

        return None

    el = document.getElementById(f'SubPage_nav_options')
    el.innerHTML += f'<button id="SubPage_nav_options_refresh" type="button" align=right style="border: 2px solid #44F; font-size: 75%;" disabled>Refresh</button>'

    for tree in data:
        if tree in glb.knownTree:
            func.addEvent(f'SubPage_nav_main_{tree}', pageSub)
            func.addEvent(f'SubPage_nav_main_{tree}', getData, f'mousedown')

    func.addEvent(f'SubPage_nav_options_refresh', refresh)

    if sub is not None:
        glb.currentSub = sub
        pageSub(args)

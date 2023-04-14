import mod.CSS as CSS
import mod.HTML as HTML
from js import document, window, eval, setTimeout, setInterval, console
from pyodide.ffi import create_proxy, create_once_callable # type: ignore
from rsa import PublicKey


class glb:
    popupTypes = {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}
    links_py_columns = 4

    pk = PublicKey(
        17975725580318426255082147295765624015303015361719602497231012933790462235693879580362187130307063578819348335338567705110647296830122706922462277858985753916807418663775359155059872610188320580932610131649669750813854841233828756158531041784174256821099975573954534872920341091204735563674609735155365230886328225569764099100220190749309854601263231477479542538657656228075477248164911150242612255058022595583271630531937574957740889057640197605063861387428744601476627747146952083278992989884033643188605058493867723623443206205193049387986735721023723231370158070058492831123317729469188277654546977114897225138444403440484404763488252900359062156606277556273881462454700682132900566293665122593793415917496306396245694769766289157377434428292617546842809345418069309429637482719212135032501150835116958632132203299437985348946833084644910715245987521602696627857328192665936755312620767597809000086619959376727150300660078176663731141210223403780234209251726760747452546317356315404004871864255840070441131656153163327938733747321658554956837916867148392977768261809450501332458691119391299657873525192653810706009363153494395380856616333139608534198022835408820709017274233496194895658713718965362482943679407034749283305672669328250828229765188719765598395616090554409644372199205005788822144569725849378518257318799359385281740742304089043012203207090757315833795382410385714872414605971371066034681422629572254445672849310499485979905134814561918728629098272915355126315453439738702075534702666290929177330864697626107597200532737216328442694999218938113176867865482874172297137142445161550097040446308420534920219666339316839673749833944188357418385020268794629695550903965269473702504547059078067498031149096658925058636652798068077433395661533192684961900825996213912591011509835703499018540858216533684827588691036564984023994359992388733781114505117772831573454751130891256075050103442171938154332660431264950585164243096093925476801938794141572630854512014984334825819438750599965004024341493159922341794445006274654995566118300460214077412075511161181698540977050816711684965694813515198715185678618288095811937806305637976252287014606730927818130439428520119356203573068177397436647258848659927556173455871707333064805630504242580519613705444817600006146353152014424758858473533029673605478152571643653561181152156398594145488582743474039155367716449975165309811984584398398690891924952884510454449930797215394455097922506895883409901302916494995512076986478728196359060058428252757519467838794722732611686045347810271767912080044182207678353913483129629823113438113820791587878184283905176268454906351041779158933382590216398059177568853055270942077059156649685981827207451739862232562515028977633596944364071556509266121310722218226028783650241233584332498505271414144626505460338325024130616840681895382408708213628489128094251273023012874086250181912500877109239104433256351412004835767020264459805538504082187665406998198032223427723556839093765764713436949937704964091432419465151166261180178053480295497695748125437451332250448661556736139515685003382928341989,
        65537)

    loggedIn = False


def log(msg: str = f''):
    console.log(msg)


def clearEvents(id):
    el = document.getElementById(id)
    el.outerHTML = el.outerHTML


def addEvent(id: str, func, action: str = "click", isClass: bool = False):
    if isClass:
        id.addEventListener(action, create_proxy(func))
        return None

    document.getElementById(id).addEventListener(action, create_proxy(func))


def cache(key: str, value: any = None):
    if not value is None:
        window.localStorage.setItem(key, value)

    return window.localStorage.getItem(key)


def clearCache():
    window.localStorage.clear()
    window.location.reload()


def f5():
    window.location.reload()


def popup(type: str, text: str):
    if type in glb.popupTypes:
        return glb.popupTypes[type](text)


def setTitle(title: str):
    document.title = title


def getWindow():
    return window


def getVP():
    return window.innerHeight, window.innerWidth


def onResize(args=None):
    def update(size: int):
        sizeMap = {"0": ("0px", "50%", "85px"), "1": ("0px 20px", "75%", "85px"), "max": ("0px 20px", "100%", "100px")}

        if size >= 2:
            size = "max"

        if not str(size) in sizeMap:
            return None

        CSS.setStyle(f'body', f'padding', sizeMap[str(size)][0])
        CSS.setStyle(f'body', f'fontSize', sizeMap[str(size)][1])
        CSS.setStyle(f'nav_logo', f'max-width', sizeMap[str(size)][2])

    def update_links(size: int):
        sizeMap = {"0": 3, "1": 4, "2": 5, "max": 6}

        if size >= 3:
            size = "max"

        if not str(size) in sizeMap:
            return None

        glb.links_py_columns = sizeMap[str(size)]
        from index import pageIndex
        pageIndex("noResize", page=window.localStorage.getItem(f'page_index'))

    def update_sonos(size: int):
        sizeMap = {"0": ("0%", "100%", "40px", "35px", "none"), "1": ("50%", "50%", "20px", "45px", ""), "max": ("75%", "25%", "0px", "55px", "")}

        if size >= 2:
            size = "max"

        if not str(size) in sizeMap:
            return None

        el = document.getElementById(f'SubPage_page_art')
        if not el is None:
            el.style.width = sizeMap[str(size)][0]
            el.style.display = sizeMap[str(size)][4]

        el = document.getElementById(f'SubPage_page_que')
        if not el is None:
            el.style.width = sizeMap[str(size)][1]
            el.style.marginBottom = sizeMap[str(size)][2]

        el = document.getElementById(f'SubPage_page_queAdd')
        if not el is None:
            el.style.minHeight = sizeMap[str(size)][3]

    page = window.localStorage.getItem(f'page_index')
    if page == "Portal":
        page = window.localStorage.getItem(f'page_portal')

    fmap = {"Links": update_links, "Sonos": update_sonos}

    size = 99
    if window.innerWidth < 450:
        size = 0
    elif window.innerWidth < 700:
        size = 1
    elif window.innerWidth < 950:
        size = 2

    update(size)
    if page in fmap:
        fmap[page](size)


def afterDelay(func, delay: int):
    setTimeout(create_once_callable(func), delay)


def aSync(func):
    setTimeout(create_once_callable(func), 0)


def atInterval(func, delay: int):
    setInterval(create_proxy(func), delay)


def jsEval(com: str):
    return eval(f'{com}')


def graph(name: str, rowHeight: str, rows: int, rowStep: int, cols: int, colStep: int = None, origin: tuple = (), rowPrefix: str = "", rowAfterfix: str = "", colNames: tuple = ()):
    htmlRows = ""
    for i1 in range(0, rows):
        borderStyle = ""
        if i1 > 0:
            borderStyle = f' border-top: 2px dashed #111;'

        txt = HTML.add(f'h1', _nest=f'{rowPrefix}{(rows - i1) * rowStep}{rowAfterfix}', _style=f'headerSmall %% height: 25%; margin: 0px auto auto auto;')
        if i1 == rows - 1:
            txt += HTML.add(f'h1', _style=f'headerSmall %% height: 40%; margin: auto auto auto auto;')
            txt += HTML.add(f'h1', _nest=f'{rowPrefix}{(rows - i1 - 1) * rowStep}{rowAfterfix}', _style=f'headerSmall %% height: 25%; margin: auto auto auto 5px;')

        htmlCols = HTML.add(f'div', _nest=txt, _id=f'{name}_row_{rows - i1 - 1}_col_header', _style=f'background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 2px solid #111;{borderStyle}')
        for i2 in range(0, cols):
            if i2 == cols - 1:
                htmlCols += HTML.add(f'div', _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {100 / cols}%; height: {rowHeight};{borderStyle}')
            else:
                htmlCols += HTML.add(f'div', _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {100 / cols}%; height: {rowHeight}; border-right: 1px dashed #111;{borderStyle}')

        htmlRows += HTML.add(f'div', _nest=htmlCols, _id=f'{name}_row_{rows - i1 - 1}', _style=f'flex %% width: 100%; height: {rowHeight};')

    txt = ""
    if len(origin) == 1:
        txt += HTML.add(f'h1', _nest=f'{origin[0]}', _style=f'headerSmall %% margin: auto;')
    elif len(origin) > 1:
        txt += HTML.add(f'h1', _nest=f'{origin[0]}', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: left;')
        txt += HTML.add(f'h1', _nest=f'/', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: center;')
        txt += HTML.add(f'h1', _nest=f'{origin[1]}', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: right;')

    htmlCols = HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_header', _style=f'background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 2px solid #111; border-top: 2px solid #111;')
    for i2 in range(0, cols):
        try:
            txt = HTML.add(f'h1', _nest=f'{colNames[i2]}', _style=f'headerSmall %% margin: auto;')
        except IndexError:
            txt = HTML.add(f'h1', _nest=f'', _style=f'headerSmall %% margin: auto;')

        if i2 == cols - 1:
            htmlCols += HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-top: 2px solid #111;')
        else:
            htmlCols += HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 1px dashed #111; border-top: 2px solid #111;')

    htmlRows += HTML.add(f'div', _nest=htmlCols, _id=f'{name}_row_header', _style=f'flex %% width: 100%; height: {rowHeight};')

    return HTML.add(f'div', _nest=htmlRows, _id=f'{name}', _style=f'margin: 10px; padding-bottom: 2px; border: 2px solid #111;')


def graphDraw(name: str, cords: tuple, lineRes: int = 100, disalowRecursive: bool = False):
    def getLineSteps(oldCords, curCords, resolution):
        diff1, diff2 = (curCords[0] - oldCords[0], curCords[1] - oldCords[1])

        if diff1 < 0:
            diff1 = -diff1
        if diff2 < 0:
            diff2 = -diff2

        biggestDiff = 0
        smallestDiff = 1
        altDiff = curCords[1] - oldCords[1]
        if diff2 > diff1:
            biggestDiff = 1
            smallestDiff = 0
            altDiff = curCords[0] - oldCords[0]

        increments = 1
        if curCords[biggestDiff] > oldCords[biggestDiff]:
            increments = -1

        steps = []
        totalSteps = len(range(int(curCords[biggestDiff] * resolution), int(oldCords[biggestDiff] * resolution), increments))
        for i, step in enumerate(range(int(curCords[biggestDiff] * resolution), int(oldCords[biggestDiff] * resolution), increments)):
            if biggestDiff == 0:
                steps.append((step / resolution, round(curCords[smallestDiff] - ((altDiff / totalSteps) * i), 2)))
            else:
                steps.append((round(curCords[smallestDiff] - ((altDiff / totalSteps) * i), 2), step / resolution))

        return steps

    for i, cord in enumerate(cords):
        colNum, colFloat = str(float(cord[0])).split(".")
        rowNum, rowFloat = str(float(cord[1])).split(".")

        try:
            HTML.add(
                f'div',
                f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                _style=f'width: 10px; height: 10px; margin: -5px; background: #55F; border-radius: 10px; position: relative; top: {95 - int(rowFloat[:2] + "0" * (2 - len(rowFloat[:2])))}%; left: {-5 + int(colFloat[:2] + "0" * (2 - len(colFloat[:2])))}%')
        except AttributeError:
            raise AttributeError(f'Invalid ID/ Cords: {name}_row_{rowNum[:2]}_col_{colNum[:2]} {cord}')

        if i <= 0 or disalowRecursive:
            continue

        oldCords = list(cords[i - 1])
        curCords = list(cords[i])

        steps = getLineSteps(oldCords, curCords, lineRes)

        graphDraw(name, steps, lineRes=lineRes, disalowRecursive=True)
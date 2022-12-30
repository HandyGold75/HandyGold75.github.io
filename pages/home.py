from js import document, window, console


class glb:
    pass


def setup():
    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_home" align="left"></div>'


def main():
    setup()

    el = document.getElementById(f'page_home')
    el.innerHTML = f'<p>Page content for home.</p>'
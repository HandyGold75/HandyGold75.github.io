import mod.func as func
from js import console


class glb:
    pass


def setup():
    func.setHTML(f'div', f'page', _id=f'page_home', _align=f'left')


def main():
    setup()

    func.setHTML(f'p', f'page_home', _nest=f'Page content for home.')

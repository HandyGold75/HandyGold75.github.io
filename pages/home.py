import mod.HTML as HTML


class glb:
    pass


def setup():
    HTML.set(f'div', f'page', _id=f'page_home', _align=f'left')


def main():
    setup()

    HTML.set(f'p', f'page_home', _nest=f'Page content for home.')

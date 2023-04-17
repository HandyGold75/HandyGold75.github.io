from WebKit import HTML


class glb:
    pass


def main():
    HTML.set(f'div', f'page', _id=f'page_home', _align=f'left')

    HTML.set(f'p', f'page_home', _nest=f'Page content for home.')

from WebKit import HTML


class glb:
    pass


def main():
    HTML.setElement(f'div', f'page', id=f'page_home', align=f'left')
    HTML.setElement(f'p', f'page_home', nest=f'Page content for home.')

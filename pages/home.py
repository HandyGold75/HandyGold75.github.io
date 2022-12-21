from js import document, window, console


def main():
    el = document.getElementById(f'page')
    el.innerHTML = f'<p>Page content for home.</p>'
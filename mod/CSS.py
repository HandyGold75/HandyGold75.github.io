from js import document


def get(id: str, key: str):
    return getattr(document.getElementById(id), key)


def set(id: str, key: str, value: str):
    try:
        getattr(document.getElementById(id), key)
    except AttributeError:
        return None

    setattr(document.getElementById(id), key, value)


def getStyle(id: str, key: str):
    return getattr(document.getElementById(id).style, key)


def setStyle(id: str, key: str, value: str):
    try:
        getattr(document.getElementById(id).style, key)
    except AttributeError:
        return None

    setattr(document.getElementById(id).style, key, value)

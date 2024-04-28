from sys import __stdin__, platform, stdin
from time import sleep, time

if platform == "win32":
    from ctypes import byref, windll, wintypes
    from msvcrt import getwch, kbhit
else:
    from select import select
    from termios import TCSADRAIN, tcgetattr, tcsetattr
    from tty import setcbreak


def timedInput(
    prompt: str = "",
    prefill: str = "",
    timeout: int = 5,
    resetOnInput: bool = True,
    maxLength: int = 0,
    allowCharacters: str = r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t",
    endCharacters: str = "\x1b\n\r",
):
    return __timedInput(prompt, prefill, timeout, resetOnInput, maxLength, allowCharacters, endCharacters)


def __timedInput(
    prompt: str = "",
    prefill: str = "",
    timeout: int = 5,
    resetOnInput: bool = True,
    maxLength: int = 0,
    allowCharacters: str = r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t",
    endCharacters: str = "\x1b\n\r",
):
    def checkStdin():
        if platform == "win32":
            return kbhit()
        else:
            return select([stdin], [], [], 0) == ([stdin], [], [])

    def readStdin():
        if platform == "win32":
            return getwch()
        else:
            return stdin.read(1)

    if not __stdin__.isatty():
        raise RuntimeError(
            "timedInput() requires an interactive shell, cannot continue.")
    else:
        __savedConsoleSettings = __getStdoutSettings()
        __enableStdoutAnsiEscape()

        userInput = prefill
        timeStart = time()
        timedOut = False

        print("  ", end="\r", flush=True)
        if len(prompt + prefill) > 0:
            print(prompt + prefill, end="", flush=True)

        while True:
            if len(prompt + prefill) > 0:
                print("\r" + prompt + prefill + userInput, end="", flush=True)

            if timeout > -1 and (time() - timeStart) >= timeout:
                timedOut = True
                if userInput != "":
                    print("")
                break

            if checkStdin():
                inputCharacter = readStdin()
                if inputCharacter in endCharacters:
                    break
                if inputCharacter != "\b" and inputCharacter != "\x7f":
                    if len(allowCharacters) and not inputCharacter in allowCharacters:
                        inputCharacter = ""
                    if maxLength > 0 and len(userInput) >= maxLength:
                        inputCharacter = ""
                    userInput = userInput + inputCharacter
                    print(inputCharacter, end="", flush=True)
                else:
                    if len(userInput):
                        userInput = userInput[0: len(userInput) - 1]
                        print("\x1b[1D\x1b[0K", end="", flush=True)
                if resetOnInput and timeout > -1:
                    timeStart = time()

            sleep(0.01)

        __setStdoutSettings(__savedConsoleSettings)
        return userInput, timedOut


def __getStdoutSettings():
    if platform == "win32":
        __savedConsoleSettings = wintypes.DWORD()
        kernel32 = windll.kernel32
        kernel32.GetConsoleMode(
            kernel32.GetStdHandle(-11), byref(__savedConsoleSettings))
    else:
        __savedConsoleSettings = tcgetattr(stdin)
    return __savedConsoleSettings


def __setStdoutSettings(__savedConsoleSettings):
    if platform == "win32":
        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(
            kernel32.GetStdHandle(-11), __savedConsoleSettings)
    else:
        tcsetattr(stdin, TCSADRAIN, __savedConsoleSettings)


def __enableStdoutAnsiEscape():
    if platform == "win32":
        kernel32 = windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else:
        setcbreak(stdin.fileno(), TCSADRAIN)

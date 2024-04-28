from datetime import datetime
from http.server import SimpleHTTPRequestHandler
from json import dump, load
from os import chdir, listdir, makedirs, path as osPath
from signal import SIGTERM, signal
from socketserver import TCPServer
from ssl import PROTOCOL_TLS, SSLContext
from sys import exit
from traceback import format_exc

from ..mod import logger


class fileServer:
    def __init__(self):
        self.workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/public")
        self.sslCertPaths = (f"/etc/letsencrypt/live/doc.handygold75.com", f'{osPath.split(__file__)[0].replace("/lib/sub", "")}/server/ssl/doc')

        self.httpd = None

        self.requiredFiles = {}
        self.configStyleFiles = ["/config.json"]
        self.sharedServerFiles = ["/config.json"]

        self.log = logger(("fileServer",), "fileServer", "FileServer").log

        if not osPath.exists(self.workFolder):
            makedirs(self.workFolder)

        self.loadFiles()
        signal(SIGTERM, self.quit)

    def loadFiles(self):
        from Server import server as rootServer

        for file in tuple(self.sharedServerFiles):
            shortFile = f'/{file.split("/")[-1]}'
            if not shortFile in self.sharedServerFiles:
                self.sharedServerFiles.append(shortFile)

            if not type(rootServer.requiredFiles[file]) is dict:
                self.requiredFiles[shortFile] = type(rootServer.requiredFiles[file])
                continue

            if file in self.configStyleFiles:
                self.requiredFiles[shortFile] = {}
                for item in rootServer.requiredFiles[file]:
                    self.requiredFiles[shortFile][item] = type(rootServer.requiredFiles[file][item])
                continue

            self.requiredFiles[shortFile] = {}
            for item in rootServer.requiredFiles[file][tuple(rootServer.requiredFiles[file])[-1]]:
                self.requiredFiles[shortFile][item] = type(rootServer.requiredFiles[file][tuple(rootServer.requiredFiles[file])[-1]][item])
            continue

        for file in self.requiredFiles:
            if file in self.sharedServerFiles:
                continue

            if len(file.split("/")) > 2:
                if not osPath.exists(f'{self.workFolder}{"/".join(file.split("/")[:-1])}'):
                    makedirs(f'{self.workFolder}{"/".join(file.split("/")[:-1])}')

            if not osPath.exists(f"{self.workFolder}{file}"):
                with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                    if type(self.requiredFiles[file]) is dict:
                        dump({}, fileW)
                        continue
                    fileW.write("")

    def quit(self, *args):
        self.httpd.server_close()
        exit()

    def verify(self, file: str, obj: dict):
        if not type(self.requiredFiles[file]) is dict:
            if not type(obj) is self.requiredFiles[file]:
                raise SyntaxError(f"Type mismatch for {str(obj)} {str(type(obj))} != {str(self.requiredFiles[file])}")
            return None

        for mainObj in obj:
            for check in self.requiredFiles[file]:
                if not check in obj[mainObj]:
                    raise SyntaxError(f"Missing record {check} ({str(mainObj)})")

                if not self.requiredFiles[file][check] is type(obj[mainObj][check]):
                    raise SyntaxError(f"Type mismatch record for {check} {str(self.requiredFiles[file][check])} != {str(type(obj[mainObj][check]))}")

            for check in obj[mainObj]:
                if not check in self.requiredFiles[file]:
                    raise SyntaxError(f"Additional record {check} ({str(mainObj)})")

    def findFile(self, file):
        if not file in self.requiredFiles:
            raise NameError(f"File {file} not found!")

        serverFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/server")

        if file.split("/")[-1] in listdir(serverFolder):
            return f'{serverFolder}/{file.split("/")[-1]}'
        elif file.split("/")[-1] in listdir(self.workFolder):
            return f'{self.workFolder}/{file.split("/")[-1]}'

        raise NameError(f"File {file} not found!")

    def write(self, file: str, obj: dict):
        if file in self.configStyleFiles:
            self.verify(file, obj)
            with open(self.findFile(file), "w", encoding="UTF-8") as fileW:
                dump(obj, fileW, indent=2)

            return obj

        objSort = {}
        for subObj in obj:
            objSort[subObj] = {}
            for tag in obj[subObj]:
                objSort[subObj][tag] = {}
                for key in self.requiredFiles[file]:
                    if key in obj[subObj][tag]:
                        objSort[subObj][tag][key] = obj[subObj][tag][key]

        try:
            objSort = dict(sorted(objSort.items(), key=lambda x: int(x[0])))
        except ValueError:
            objSort = dict(sorted(objSort.items()))

        for subObjSort in objSort:
            self.verify(file, objSort[subObjSort])
        with open(self.findFile(file), "w", encoding="UTF-8") as fileW:
            dump(objSort, fileW, indent=2)

        return objSort

    def errorHandler(self, request, client_address):
        msg = f"Exception occurred during processing of request from {client_address}"
        self.log(criticality="error", msg=msg)

        err = format_exc().split("\n")[-2]
        for allowedError in ["ConnectionError", "ConnectionResetError"]:
            if allowedError in err:
                return None

        self.log(criticality="error", msg=format_exc())
        raise Exception(msg)

    def start(self):
        with open(self.findFile("/config.json"), "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)
            ip = fileData["IP"]
            port = fileData["PORT"] + 1

        chdir(self.workFolder)

        handler = SimpleHTTPRequestHandler
        handler.log_message = lambda *args: None
        self.httpd = TCPServer((ip, port), handler)
        self.httpd.handle_error = self.errorHandler

        sslCert = False
        for path in self.sslCertPaths:
            if osPath.exists(f"{path}/fullchain.pem") and osPath.exists(f"{path}/privkey.pem"):
                sslCert = SSLContext(PROTOCOL_TLS)
                sslCert.load_cert_chain(certfile=f"{path}/fullchain.pem", keyfile=f"{path}/privkey.pem")
                self.httpd.socket = sslCert.wrap_socket(self.httpd.socket, server_side=True)
                self.log(criticality="info", msg=f"Started HTTPS service on {ip}:{port}")
                break
        else:
            self.log(criticality="warning", msg=f'Missing doc certificates! Valid locations: \n    {"\n    ".join(self.sslCertPaths)}')
            self.log(criticality="info", msg=f"Started HTTP service on {ip}:{port}")

        self.httpd.serve_forever()

    def main(self):
        self.start()
        self.quit()


if __name__ == "__main__":
    fileServer().main()

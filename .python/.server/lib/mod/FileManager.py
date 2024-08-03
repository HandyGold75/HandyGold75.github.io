from ast import literal_eval
from datetime import datetime
from hashlib import sha256
from json import dump, dumps, load, loads
from os import listdir, makedirs, path as osPath, remove
from shutil import move, rmtree

from rsa import PublicKey, decrypt, encrypt


class fileManager:
    def __init__(
        self,
        workFolder: str,
        sheets: dict = {},
        configs: list | tuple = (),
        modifiedKey: str = "Modified",
        discoveryFolders: list | tuple = (),
        configEncryptKeys: list | tuple = (),
        decryptPvk: object = None,
        return_var: list = [None],
    ):
        self.workFolder = workFolder

        self.sheets = sheets
        self.configs = configs

        self.modifiedKey = modifiedKey
        self.discoveryFolders = discoveryFolders
        self.configEncryptKeys = configEncryptKeys
        self.decryptPvk = decryptPvk

        self.dataSplitter = "%%"

        with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/mod", "") + "/server/ssl/pub.pem", "r", encoding="UTF-8") as fileR:
            self.svPub = PublicKey.load_pkcs1(fileR.read())

        if not osPath.exists(self.workFolder):
            makedirs(self.workFolder)

        for sheet in self.sheets:
            if not osPath.exists(f"{self.workFolder}/{sheet}"):
                makedirs(f"{self.workFolder}/{sheet}")

        self.commands = {
            "template": [None, self.com_template],
            "read": [None, self.com_read],
            "mod": [None, self.com_mod],
            "modcfg": [None, self.com_modcfg],
            "add": [None, self.com_add],
            "del": [None, self.com_dell],
            "swap": [None, self.com_swap],
            "count": [None, self.com_count],
        }

        if self.sheets == {}:
            for toPop in ("mod", "add", "del", "swap", "count"):
                self.commands.pop(toPop)
        if self.configs == ():
            for toPop in ("modcfg",):
                self.commands.pop(toPop)

        if not return_var is None:
            return_var[0] = self

    def _findFile(self, file):
        if file in self.configs:
            file = f"{file}.json"
        else:
            raise NameError(f"File {file} not found!")

        if file in listdir(self.workFolder):
            return f'{self.workFolder}/{file.split("/")[-1]}'

        for folder in self.discoveryFolders:
            if file in listdir(folder):
                return f'{folder}/{file.split("/")[-1]}'

        raise NameError(f"File {file} not found!")

    def _verifyAllowed(self, file: str, allowSheets: bool = False, allowConfig: bool = False):
        if not file in [*(self.sheets if allowSheets else []), *(self.configs if allowConfig else [])]:
            raise SyntaxError(f"File is not allowed, use one of {(*self.sheets, *self.configs)}")

        if file in self.sheets:
            if not osPath.exists(f"{self.workFolder}/{file}") or not osPath.isdir(f"{self.workFolder}/{file}"):
                folders = []
                for folder in listdir(self.workFolder):
                    if osPath.isdir(f"{self.workFolder}/{folder}"):
                        folders.append(folder)

                raise SyntaxError(f"Sheet does not exist, use one of {tuple(folders)}")

        elif file in self.configs:
            file = self._findFile(file)
            if not osPath.exists(file) or not osPath.isfile(file) or not file.endswith(".json"):
                raise SyntaxError(
                    f"Config does not exist, use one of {self.configs}")

    def _verfiyIndex(self, sheet: tuple | list | str, index: str | int, allowStr: bool = True, allowUnder: bool = False, allowOver: bool = False):
        if type(sheet) in [tuple, list]:
            sheetCount = len(sheet)
        else:
            sheetCount = self._count(sheet)

        if type(index) is int:
            if (not allowUnder and index < 0) or (not allowOver and index > sheetCount - 1):
                raise SyntaxError(f'Index is formated incorrectly, use "{"-" if allowUnder else ""}0:{sheetCount - 1}{"+" if allowOver else ""}"')

        elif type(index) is str and allowStr:
            if index.count(":") != 1:
                raise SyntaxError(f'Index is formated incorrectly, use "{"-" if allowUnder else ""}0:{sheetCount - 1}{"+" if allowOver else ""}"')

            index1 = int(index.split(":")[0])
            index2 = int(index.split(":")[-1])
            if index1 > index2 or (not allowUnder and index1 < 0) or (not allowOver and index2 > sheetCount - 1):
                raise SyntaxError(f'Index is formated incorrectly, use "{"-" if allowUnder else ""}0:{sheetCount - 1}{"+" if allowOver else ""}"')

        else:
            raise SyntaxError(f'Index is formated incorrectly, use "{"-" if allowUnder else ""}0:{sheetCount - 1}{"+" if allowOver else ""}"')

    def _verifyData(self, healtyData: tuple | list | dict, data: tuple | list):
        if len(healtyData) > len(data):
            raise SyntaxError(f"Missing one or more record(s)!")
        elif len(healtyData) < len(data):
            raise SyntaxError(f"One or more additional record(s) found!")

        if type(healtyData) is dict:
            for key in healtyData:
                if key == self.modifiedKey:
                    data[key] = datetime.now().timestamp()

                if not key in data:
                    raise KeyError(f"Missing key {key}!")
                if not type(data[key]) is type(healtyData[key] and not (type(healtyData[key]) is bytes and type(data[key]) is str)):
                    raise TypeError(f"Type mismatch for key {key} ({type(data[key])} != {type(healtyData[key])})!")

                if type(healtyData[key]) is dict:
                    data[key] = self._verifyData(healtyData[key], data[key])

            return data

        data = list(data)
        for i, check in enumerate(healtyData):
            skey, stype = check
            if skey == self.modifiedKey:
                data[i] = datetime.now().timestamp()

            if not type(data[i]) is stype and not (stype is bytes and type(data[i]) is str):
                raise TypeError(f"Type mismatch for key {skey} ({type(data[i])} != {stype})!")

        return data

    def _sanatizeData(self, data: dict | list):
        if isinstance(data, dict):
            return {k: "REDACTED" if k in ("Password", "TapoPassword") else self._sanatizeData(v) for k, v in data.items()}
        if isinstance(data, list):
            tmp = []
            for v in data:
                try:
                    if isinstance(literal_eval(v), bytes):
                        tmp.append("REDACTED")
                        continue
                except (ValueError, SyntaxError):
                    pass

                tmp.append(self._sanatizeData(v))

            return tmp

        return data

    def _jsonFriendlyfy(self, data: dict | list | tuple):
        if isinstance(data, dict):
            return {k: (str() if v is bytes else v()) if isinstance(v, type) else self._jsonFriendlyfy(v) for k, v in data.items()}

        if isinstance(data, (list, tuple)):
            wasTuple = isinstance(data, tuple)
            data = list(data)

            for index, item in enumerate(data):
                if isinstance(item, (list, tuple)):
                    data[index] = self._jsonFriendlyfy(item)
                elif isinstance(item, type):
                    data[index] = str() if item is bytes else item()

            return tuple(data) if wasTuple else data

        return data

    def _read(self, sheet: str, index: int | str | None = None):
        self._verifyAllowed(sheet, allowSheets=True)

        sheetData = {}
        folders = listdir(f"{self.workFolder}/{sheet}")
        if not index is None:
            self._verfiyIndex(sheet, index)

            if type(index) is int:
                folders = (str(index),)
            elif type(index) is str:
                folders = []
                for i in range(int(index.split(":")[0]), int(index.split(":")[-1]) + 1):
                    folders.append(str(i))

        for folder in folders:
            if not osPath.isdir(f"{self.workFolder}/{sheet}/{folder}"):
                continue

            file = listdir(f"{self.workFolder}/{sheet}/{folder}")
            if len(file) > 1:
                raise FileExistsError(f"Record with index {folder} contains multible records!")
            elif len(file) == 0:
                raise FileNotFoundError(f"Record with index {folder} contains no records!")
            file = file[0]

            if not osPath.isfile(f"{self.workFolder}/{sheet}/{folder}/{file}"):
                continue

            with open(f"{self.workFolder}/{sheet}/{folder}/{file}", "r", encoding="UTF-8") as fileR:
                fileData = fileR.read().split(self.dataSplitter)

            sheetData[folder] = []
            for i, value in enumerate(fileData):
                if self.sheets[sheet][i][-1] is bool:
                    value = literal_eval(value)
                if self.sheets[sheet][i][-1] is bytes:
                    value = str(value)
                elif self.sheets[sheet][i][-1] is list:
                    value = loads(value)
                else:
                    value = self.sheets[sheet][i][-1](value)
                sheetData[folder].append(value)

        return dict(sorted(sheetData.items(), key=lambda item: int(item[0])))

    def _readcfg(self, config: str):
        self._verifyAllowed(config, allowConfig=True)

        with open(self._findFile(config), "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)

        return fileData

    def _write(self, sheet: str, index: int, data: tuple | list, preventOverwrite: bool = False, allowOverIndex: bool = True):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index, allowStr=False,
                          allowOver=allowOverIndex)
        data = self._verifyData(self.sheets[sheet], data)

        if not osPath.exists(f"{self.workFolder}/{sheet}/{index}"):
            makedirs(f"{self.workFolder}/{sheet}/{index}")
        elif preventOverwrite:
            raise FileExistsError(f"Sheet already has an record at index {index}!")

        file = listdir(f"{self.workFolder}/{sheet}/{index}")
        if len(file) > 1:
            raise FileExistsError(f"Record with index {index} contains multible records!")
        elif len(file) == 1:
            remove(f"{self.workFolder}/{sheet}/{index}/{file[0]}")

        dataTmp = []
        for i, item in enumerate(data):
            if self.sheets[sheet][i][-1] is list:
                item = dumps(item)
            elif self.sheets[sheet][i][-1] is bytes:
                item = str(self._recrypt(item))
            dataTmp.append(str(item))

        with open(f'{self.workFolder}/{sheet}/{index}/{sha256(self.dataSplitter.join(dataTmp).encode("utf-8")).hexdigest()}', "w", encoding="UTF-8") as fileW:
            fileW.write(self.dataSplitter.join(dataTmp))

    def _writecfg(self, config: str, data: dict):
        self._verifyAllowed(config, allowConfig=True)

        fileData = self._readcfg(config)
        data = {**fileData, **data}
        data = self._verifyData(fileData, data)

        for key in self.configEncryptKeys:
            if key in data:
                data[key] = str(self._recrypt(key))

        with open(self._findFile(config), "w", encoding="UTF-8") as fileW:
            dump(data, fileW)

    def _modify(self, sheet: str, index: int, key: str, value: str):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index, allowStr=False)

        data = self._read(sheet, index)[str(index)]

        for i, check in enumerate(self.sheets[sheet]):
            skey, stype = check
            if key == skey:
                if stype is bool:
                    data[i] = literal_eval(value)
                    break
                data[i] = stype(value)
                break
        else:
            raise KeyError(f"Key {key} is not valid!")

        self._write(sheet, index, data)

    def _modifycfg(self, config: str, key: str, value: str):
        self._verifyAllowed(config, allowConfig=True)

        fileData = self._readcfg(config)

        if not key in fileData:
            raise KeyError(f"Key {key} is not valid!")

        if type(fileData[key]) is bool:
            fileData[key] = literal_eval(value)
        else:
            fileData[key] = type(fileData[key])(value)

        self._writecfg(config, fileData)

    def _dell(self, sheet: str, index: int | str):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index)

        if type(index) is int:
            rmtree(f"{self.workFolder}/{sheet}/{index}")

            for i in range(index, self._count(sheet)):
                self._move(sheet, i + 1, i)

        elif type(index) is str:
            index1 = int(index.split(":")[0])
            index2 = int(index.split(":")[-1])
            for i in range(index2, index1 - 1, -1):
                rmtree(f"{self.workFolder}/{sheet}/{i}")

            offset = index2 - index1
            for i in range(index2, self._count(sheet) + offset):
                self._move(sheet, i + 1, i - offset)

    def _add(self, sheet: str, index: int, count: int, data: tuple | list = None):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index, allowUnder=True, allowOver=True)

        currentCount = self._count(sheet)
        if index < 0:
            for i in range(currentCount, currentCount + count):
                self._write(sheet, i, data, preventOverwrite=True)

            return None

        if index > currentCount:
            index = currentCount

        for i in range(currentCount - 1, index - 1, -1):
            self._move(sheet, i, i + count)
        for i in range(index, index + count):
            self._write(sheet, i, data, preventOverwrite=True)

    def _move(self, sheet: str, index1: int, index2: int):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index1, allowStr=False, allowOver=True)
        self._verfiyIndex(sheet, index2, allowStr=False, allowOver=True)

        if osPath.exists(f"{self.workFolder}/{sheet}/{index2}"):
            raise FileExistsError(f"Sheet already has an record at index {index2}!")

        file1 = listdir(f"{self.workFolder}/{sheet}/{index1}")
        if len(file1) > 1:
            raise FileExistsError(f"Record with index {index1} contains multible records!")
        elif len(file1) == 0:
            raise FileNotFoundError(f"Record with index {index1} contains no records!")
        file1 = file1[0]

        makedirs(f"{self.workFolder}/{sheet}/{index2}")
        move(f"{self.workFolder}/{sheet}/{index1}/{file1}",
             f"{self.workFolder}/{sheet}/{index2}/{file1}")
        rmtree(f"{self.workFolder}/{sheet}/{index1}")

    def _swap(self, sheet: str, index1: int, index2: int):
        self._verifyAllowed(sheet, allowSheets=True)
        self._verfiyIndex(sheet, index1)
        self._verfiyIndex(sheet, index2)

        file1 = listdir(f"{self.workFolder}/{sheet}/{index1}")
        if len(file1) > 1:
            raise FileExistsError(f"Record with index {index1} contains multible records!")
        elif len(file1) == 0:
            raise FileNotFoundError(f"Record with index {index1} contains no records!")
        file1 = file1[0]

        file2 = listdir(f"{self.workFolder}/{sheet}/{index2}")
        if len(file2) > 1:
            raise FileExistsError(f"Record with index {index2} contains multible records!")
        elif len(file2) == 0:
            raise FileNotFoundError(f"Record with index {index2} contains no records!")
        file2 = file2[0]

        move(f"{self.workFolder}/{sheet}/{index1}/{file1}",
             f"{self.workFolder}/{sheet}/{index2}/{file1}")
        move(f"{self.workFolder}/{sheet}/{index2}/{file2}",
             f"{self.workFolder}/{sheet}/{index1}/{file2}")

    def _count(self, sheet: str):
        self._verifyAllowed(sheet, allowSheets=True)
        return len(listdir(f"{self.workFolder}/{sheet}"))

    def _recrypt(self, data: str):
        try:
            return encrypt(decrypt(literal_eval(str(data)), self.decryptPvk).decode().encode(), self.svPub)
        except Exception:
            return ""

    def _tryInt(self, obj: int | float | str):
        try:
            obj = int(obj)
        except (TypeError, ValueError):
            pass

        return obj

    def template(self):
        return {"template": {"sheets": self.sheets, "configs": self.configs}}

    async def com_template(self, clT):
        return self._sanatizeData(self._jsonFriendlyfy(self.template()))

    def read(self, sheet: str, index: int | None = None):
        if sheet in self.configs:
            if not index is None:
                raise TypeError("unsupported positional argument for configs: 'index'")
            return {sheet: self._sanatizeData(self._readcfg(sheet))}

        return {sheet: self._read(sheet, self._tryInt(index))}

    async def com_read(self, clT, sheet: str, index: int | None = None):
        return self._sanatizeData(self.read(sheet, index))

    def mod(self, sheet: str, index: int, key: str | None, data: tuple | list | str):
        if sheet in self.configs:
            raise ValueError("configs should use modcfg to make modifications")

        if key is None or key == "*":
            if type(data) is str:
                data = loads(data)
            self._write(sheet, int(index), tuple(data), allowOverIndex=False)
        else:
            self._modify(sheet, int(index), key, str(data))

        return {sheet: self._read(sheet)}

    async def com_mod(self, clT, sheet: str, index: int, key: str | None, data: tuple | list | str):
        return self._sanatizeData(self.mod(sheet, index, key, data))

    def modcfg(self, config: str, key: str | None, data: dict | str):
        if config in self.sheets:
            raise ValueError("sheets should use mod to make modifications")

        if key is None or key == "*":
            if type(data) is str:
                data = loads(data)
            self._writecfg(config, dict(data))
        else:
            self._modifycfg(config, key, str(data))

        return {config: self._readcfg(config)}

    async def com_modcfg(self, clT, config: str, key: str | None, data: dict | str):
        return self._sanatizeData(self.modcfg(config, key, data))

    def add(self, sheet: str, index: int | None = None, count: int | None = None, data: tuple | list | str = None):
        count = 1 if count is None else count
        index = -1 if index is None else index
        if data is None:
            data = []
            for check in self.sheets[sheet]:
                data.append(check[-1]())
        elif type(data) is str:
            data = loads(data)

        self._add(sheet, self._tryInt(index), int(count), tuple(data))

        return {sheet: self._read(sheet)}

    async def com_add(self, clT, sheet: str, index: int | None = None, count: int | None = None, data: tuple | list | str = None):
        return self._sanatizeData(self.add(sheet, index, count, data))

    def dell(self, sheet: str, index: int | str):
        self._dell(sheet, self._tryInt(index))
        return {sheet: self._read(sheet)}

    async def com_dell(self, clT, sheet: str, index: int | str):
        return self._sanatizeData(self.dell(sheet, index))

    def swap(self, sheet: str, index1: int, index2: int):
        self._swap(sheet, int(index1), int(index2))
        return {sheet: self._read(sheet)}

    async def com_swap(self, clT, sheet: str, index1: int, index2: int):
        return self._sanatizeData(self.swap(sheet, index1, index2))

    def count(self, sheet: str, short: bool = False):
        if short:
            return self._count(sheet)
        return f"Count {sheet}: {self._count(sheet)}"

    async def com_count(self, clT, sheet: str, short: bool = False):
        return self._sanatizeData(self.count(sheet, short))

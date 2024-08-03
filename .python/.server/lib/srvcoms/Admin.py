from os import listdir, makedirs, path as osPath, remove
from shutil import rmtree

from ..mod import fileManager, logger


class admin:
    requiredFiles = {}

    def __init__(self, userData, return_var=None):
        self.workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "/server")

        self.fileManager = fileManager(
            workFolder=self.workFolder,
            sheets={
                "tokens": (("User", str), ("Token", str), ("Password", bytes), ("Auth", int), ("Roles", list), ("Expires", float), ("Modified", float), ("Active", bool), ("TapoUser", str), ("TapoPassword", bytes), ("Notes", str)),
            },
            configs=("config",),
            modifiedKey="Modified",
            configEncryptKeys=("Password", "TapoPassword"),
            decryptPvk=userData["pvk"],
        )
        self.logger = logger(("server", "clientHandler", "fileServer", "tapoMonitor"))

        if not osPath.exists(self.workFolder):
            makedirs(self.workFolder)

        for command in self.fileManager.commands:
            self.fileManager.commands[command][0] = "Admin"

        self.logger.commands["readlog"] = self.logger.commands["read"]
        self.logger.commands.pop("template")
        self.logger.commands.pop("read")

        self.commands = {
            **self.fileManager.commands,
            **self.logger.commands,
            **{
                "template": ["Admin", self.com_template],
                "clean": ["Admin", self.clean],
            },
        }

        if not return_var is None:
            return_var[0] = self

    async def com_template(self, clT):
        return {"template": {**(await self.fileManager.com_template(clT))["template"], "logs": {**(await self.logger.com_template(clT))["template"]}}}

    async def clean(self, clT):
        rootFolder = self.workFolder.replace("/server", "")

        purgeFolders = []
        purgeSubFolders = ["/public/Sonos"]
        purgeFiles = ["/public/Sonos"]
        cleanFolders = ["/user"]

        actionsDone = []
        for folder in purgeFolders:
            if not osPath.exists(f"{rootFolder}{folder}"):
                continue
            rmtree(f"{rootFolder}{folder}")
            actionsDone.append(f"~{folder}")

        for folder in purgeSubFolders:
            if not osPath.exists(f"{rootFolder}{folder}"):
                continue

            for file in listdir(f"{rootFolder}{folder}"):
                if osPath.isdir(f"{rootFolder}{folder}/{file}"):
                    rmtree(f"{rootFolder}{folder}/{file}")
                    pass

            actionsDone.append(f"~{folder}/*/*")

        for folder in purgeFiles:
            if not osPath.exists(f"{rootFolder}{folder}"):
                continue

            for file in listdir(f"{rootFolder}{folder}"):
                if osPath.isfile(f"{rootFolder}{folder}/{file}"):
                    remove(f"{rootFolder}{folder}/{file}")
                    pass

            actionsDone.append(f"~{folder}/*.*")

        userDataHeader = [pair[0] for pair in self.fileManager.template()["template"]["sheets"]["tokens"]]
        allUserData = self.fileManager.read("tokens")["tokens"]
        tokens = tuple(allUserData[dataIndex][userDataHeader.index("Token")] for dataIndex in allUserData)

        for folder in cleanFolders:
            for subFolder in listdir(f"{rootFolder}{folder}"):
                if not osPath.exists(f"{rootFolder}{folder}/{subFolder}") or not osPath.isdir(f"{rootFolder}{folder}/{subFolder}"):
                    continue
                if subFolder in tokens or len(subFolder) < 128:
                    continue
                rmtree(f"{rootFolder}{folder}/{subFolder}")
                actionsDone.append(f"~{folder}/{subFolder}")

        return {"Cleaned": actionsDone}

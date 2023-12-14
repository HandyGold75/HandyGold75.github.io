async function loadPackage(package) {
    window.micropip.install(package);
    logToDebug(`<p>Loaded package: ${package}</p>`)
};

async function loadFolder(folder) {
    if (folder !== "") {
        await window.pyodide.runPythonAsync(`
        from os import makedirs
        makedirs("${folder}", exist_ok=True)
        `)
    };
    logToDebug(`<p>Loaded folder: ./${folder}</p>`)
};

async function loadFile(file) {
    await window.pyodide.runPythonAsync(`
    from pyodide.http import pyfetch
    with open("${file}", "wb") as f:
        f.write(await (await pyfetch("./${file}")).bytes())
    `);
    logToDebug(`<p>Loaded file: ./${file}</p>`)
};

function logToDebug(msg) {
    document.getElementById("debug").innerHTML += msg
}


async function main() {
    let body = document.getElementById("body")
    body.innerHTML = `
    <img src="./docs/assets/Load.svg" style="position: absolute; left: 50%; top: 50px; transform: translate(-50%, 0px); width: 150px;"></svg>
    <div id="debug" style="width: 100%; margin-top: 250px; text-align: center;"></div>
    `

    window.pyodide = await loadPyodide();
    logToDebug(`<p>Loaded Pyodide</p>`)

    await window.pyodide.loadPackage("micropip");
    window.micropip = window.pyodide.pyimport("micropip");
    logToDebug(`<p>Loaded Micropip</p>`)

    const config = await (await fetch("./docs/python/pyconfig.json")).json();
    let promises = new Array();
    logToDebug(`<p>Loaded PyConfig</p>`)

    for (const package of config["packages"]) {
        promises.push(loadPackage(package))
    };

    Object.entries(config["files"]).forEach(([path, files]) => {
        promises.push(
            loadFolder(path).then(async () => {
                if (path !== "") {
                    path += "/"
                };
                for (const file of files) {
                    await loadFile(path + file)
                };
            })
        )
    });

    Promise.all(promises).then((responses) => {
        window.pyodide.runPython(`
        with open("main.py", "r") as f:
            exec(f.read())
        `)
    })
};

main();
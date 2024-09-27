import "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js";

async function loadFolder(folder) {
  if (folder !== "") {
    await window.pyodide.runPythonAsync(`
        from os import makedirs
        makedirs("${folder}", exist_ok=True)
        `);
  }
  document.getElementById("debug").innerHTML +=
    `<p>Loaded folder: ./${folder}</p>`;
}

async function main() {
  document.getElementsByTagName("body")[0].innerHTML = `
    <img src="./docs/assets/Load.svg" style="position: absolute; left: 50%; top: 50px; transform: translate(-50%, 0px); width: 150px;"></svg>
    <div id="debug" style="width: 100%; margin-top: 250px; text-align: center;"></div>
    `;

  window.pyodide = await loadPyodide();
  document.getElementById("debug").innerHTML += `<p>Loaded Pyodide</p>`;

  await window.pyodide.loadPackage("micropip", { messageCallback: () => {} });
  window.micropip = window.pyodide.pyimport("micropip");
  document.getElementById("debug").innerHTML += `<p>Loaded Micropip</p>`;

  const config = await (await fetch("./docs/python/pyconfig.json")).json();
  let promises = new Array();
  document.getElementById("debug").innerHTML += `<p>Loaded PyConfig</p>`;

  for (const pkg of config["packages"]) {
    window.micropip.install(pkg);
    document.getElementById("debug").innerHTML +=
      `<p>Loaded package: ${pkg}</p>`;
  }

  Object.entries(config["files"]).forEach(([path, files]) => {
    promises.push(
      loadFolder(path).then(async () => {
        if (path !== "") {
          path += "/";
        }
        for (const file of files) {
          await window.pyodide.runPythonAsync(`
                    from pyodide.http import pyfetch
                    with open("${path + file}", "wb") as f:
                        f.write(await (await pyfetch("./${path + file}")).bytes())
                    `);
          document.getElementById("debug").innerHTML +=
            `<p>Loaded file: ./${path + file}</p>`;
        }
      }),
    );
  });

  Promise.all(promises).then((responses) => {
    window.pyodide.runPython(`
        with open("main.py", "r") as f:
            exec(f.read())
        `);
  });
}

main();


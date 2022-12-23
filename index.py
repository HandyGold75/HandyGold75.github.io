<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
    <script defer src="https://pyscript.net/latest/pyscript.js"></script>
    <title>HandyGold75</title>
    <link href="docs/assets/;D.ico" rel="icon" type="image/x-icon">
    <link href="style.css" type="text/css" rel="stylesheet">
</head>

<body id="body">
    <py-config>
        packages = ["rsa"]

        [[fetch]]
        files = [
        "index.py",
        "mod/func.py", "mod/ws.py",
        "pages/home.py", "pages/links.py", "pages/portal.py", "pages/contact.py",
        "subs/portal_sheets.py"
        ]
    </py-config>
    <script src="mod/wsClient.js"></script>
    <py-script src="index.py"></py-script>
</body>

</html>
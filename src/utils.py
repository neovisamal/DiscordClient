import os
import sys
import json

from datetime import datetime
from dateutil import tz


embedColors = {
"Red": 0xff0000,
"Orange": 0xff6600,
"Yellow": 0xfff700,
"Green": 0x00ff1e,
"Blue": 0x002aff,
"Purple": 0x8000ff,
"Pink": 0xfb00ff
}


def checkIfNone(value, default):
    if value:
        return value
    else:
        return default


def loadConfig(path):
    with open(f"{path}/config.json") as file:
        return json.loads(file.read())


def saveData(path, config):
    with open(f"{path}/config.json", "w+") as file:
        file.write(json.dumps(config))


def openInBrowser(url):
    browsers = {
        "win32": "start",
        "darwin": "open"
        }

    os.system(f"{browsers[sys.platform]} \"\" {url}")


def UTCtoPST(utc_time):
    utc = tz.gettz('UTC')
    new_zone = tz.gettz("America/Los_Angeles")

    utc_time = utc_time.replace(tzinfo=utc)

    local_time = (utc_time.astimezone(new_zone)).strftime('%H:%M:%S %m/%d/%Y')

    return local_time


async def getMessage(message):
    async for m in message.channel.history(limit=25):
        if message.id == m.id:
            return m


def raiseDialogue(message):
    command = 'PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('
    command += f"'{message}')"
    command += '"'
    os.system(command)


def log(message):
    with open("log.txt", "w") as file:
        file.write(f"{datetime.utcnow()}, {message}")

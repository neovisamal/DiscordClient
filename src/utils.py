import os
from datetime import datetime

def raiseDialogue(message):
    command = 'PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('
    command += f"'{message}')"
    command += '"'
    os.system(command)


def log(message):
    with open("log.txt", "w") as file:
        file.write(f"{datetime.utcnow()}, {message}")

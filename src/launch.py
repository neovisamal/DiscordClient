import os
import utils


def launch():
    local = os.getenv('LOCALAPPDATA')

    path = local + '\Discord'
    for dir in os.listdir(path):
        if dir.startswith("app-"):
            path += f"/{dir}/Discord.exe"
            break
    else:
        utils.raiseDialogue("Discord is not installed")


    os.system(f"START {path}")

if __name__ == "__main__":
    launch()

import os

def launch():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    path = roaming + '\\Discord'
    print(path)

    os.system(f"START {path}")

if __name__ == "__main__":
    launch()

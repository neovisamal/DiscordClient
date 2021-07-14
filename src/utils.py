import discord
from discord.ext import commands

from datetime import datetime
from dateutil import tz

import json
import os


class Config:
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save_data()


    def __init__(self, **kwargs):
        self.TOKEN = kwargs.get("TOKEN", None)
        self.cogs = kwargs.get("cogs", [])
        self.ignored_words = kwargs.get("ignored_words", [])
        self.prefix = kwargs.get("prefix", ".")
        self.log_channel = kwargs.get("log_channel", 0)
        self.ignored_users = kwargs.get("ignored_users", [])
        self.logged_guilds = kwargs.get("logged_guilds", [])


    @classmethod
    def from_file(cls, *, path="config.json"):
        with open(path) as file:
            config = json.loads(file.read())
        return cls(**config)


    def save_data(self, *, path="config.json"):
        with open(path, "w+") as file:
            file.write(json.dumps(self.__dict__))


    @staticmethod
    def config_exists(*, path="config.json"):
        try:
            open(path)
            return True
        except FileNotFoundError:
            return False


class Color(discord.Color):
    @classmethod
    def red(cls):
        return cls(0xff0000)


class Converters:
    RoleConverter = commands.RoleConverter()
    MemberConverter = commands.MemberConverter()


def checkIfNone(value, default):
    if value:
        return value
    else:
        return default


def UTCtoPST(utc_time):
    utc = tz.gettz('UTC')
    new_zone = tz.gettz("America/Los_Angeles")

    utc_time = utc_time.replace(tzinfo=utc)

    local_time = (utc_time.astimezone(new_zone)).strftime('%H:%M:%S %m/%d/%Y')

    return local_time


def raiseDialogue(message):
    command = 'PowerShell -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('
    command += f"'{message}')"
    command += '"'
    os.system(command)

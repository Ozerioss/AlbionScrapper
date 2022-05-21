import configparser
from pathlib import Path


def read_config():
    config = configparser.ConfigParser()
    config.read(Path("resources/conf/config.local.ini"))
    return config

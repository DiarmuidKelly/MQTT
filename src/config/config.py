import configparser
import pathlib

def parse(config_path='./config.ini', config_section='DEFAULT'):
    config = configparser.ConfigParser()
    config_file = pathlib.Path(config_path)
    config.read(config_file)
    config = config[config_section]
    return config
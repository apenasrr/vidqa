from configparser import ConfigParser
from pathlib import Path


def get_data(path_file_config: Path) -> dict:
    """get default configuration data from file config.ini

    Args:
        path_file_config (Path): path configuration file

    Returns:
        dict: config data
    """

    config_file = ConfigParser()
    config_file.read(path_file_config)
    default_config = dict(config_file["default"])
    return default_config


def set_data(path_file_config: Path, variable: str, value: str) -> None:
    """Changes variable in the configuration file

    Args:
        path_file_config (Path): path configuration file
        variable (str): variable to be changed
        value (str): value to set
    """

    config_file = ConfigParser()
    config_file.read(path_file_config)
    config_file.set("default", variable, value)
    with open(path_file_config, "w") as file:
        config_file.write(file)

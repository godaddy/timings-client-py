"""Utility to allow user to load the config settings"""
import yaml

DEFAULT = 'default'

_CONFIG_MAP = {}


def load_config(filespec, name):
    """
    Loads the configuration from the file path specified and caches this for
    later use by future callers.
    To set the default, pass in DEFAULT as the name
    :param filespec: The file path to the target configuration file.
    :param name: The name to associate with this config. Set to DEFAULT for
    default.
    :return: The Conf associated with the configuration.
    """
    conf = Conf(filespec)
    _CONFIG_MAP[name] = conf
    return conf


def get_config(name=None):
    """
    Returns a cached version of the config based on name. When None, returns
    the default.
    :param name: The name to cache this under. None assumes DEFAULT
    :return: The config object associated with the provided name.
    :raises: KeyError when the config was not previously loaded.
    """
    if name is None:
        return _CONFIG_MAP[DEFAULT]
    return _CONFIG_MAP[name]


class Conf():
    def __init__(self, filespec):
        self._filespec = filespec
        self._config = self._read_conf(filespec)

    def _read_conf(self, filespec):
        with open(filespec, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return config

    def get_filespec(self):
        return self._filespec

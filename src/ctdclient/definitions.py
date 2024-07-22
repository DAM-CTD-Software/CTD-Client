import importlib.metadata
from pathlib import Path

from ctdclient.utils import get_config_path


ROOT_PATH = Path(__file__).absolute().parents[2]
CONFIG_PATH = get_config_path()
VERSION = importlib.metadata.version("ctdclient")
THEMES_PATH = ROOT_PATH.joinpath("templates/ctktheme.json")

# update specifics
INSTALL_DIR = ROOT_PATH.joinpath("updates")
TUFUP_METADATA = INSTALL_DIR.joinpath("metadata")
TUFUP_TARGET = INSTALL_DIR.joinpath("target")
METADATA_URL = "http://localhost:8000/metadata/"
TARGET_URL = "http://localhost:8000/target/"

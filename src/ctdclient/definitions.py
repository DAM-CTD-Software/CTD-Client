import sys
import importlib.metadata
from pathlib import Path
from ctdclient.configurationhandler import ConfigurationFile

from ctdclient.utils import get_config_path

if getattr(sys, 'frozen', False):
    ROOT_PATH = Path(sys.executable).parent
    RESSOURCES_PATH = Path(sys._MEIPASS)
else:
    RESSOURCES_PATH = ROOT_PATH = Path(__file__).absolute().parents[2]
CONFIG_PATH = get_config_path(ROOT_PATH, RESSOURCES_PATH)
config = ConfigurationFile(CONFIG_PATH)
VERSION = importlib.metadata.version("ctdclient")
THEMES_PATH = RESSOURCES_PATH.joinpath("ctktheme.json")
ICON_PATH = RESSOURCES_PATH.joinpath("icon.ico")
PROCESSING_TEMPLATE_PATH = RESSOURCES_PATH.joinpath(
    "templates", "processing_template.toml")

# update specifics
INSTALL_DIR = RESSOURCES_PATH.joinpath("updates")
TUFUP_METADATA = INSTALL_DIR.joinpath("metadata")
TUFUP_TARGET = INSTALL_DIR.joinpath("targets")
# ensure, that directory exists
if not TUFUP_TARGET.exists():
    TUFUP_TARGET.mkdir(parents=True)
METADATA_URL = f"{config.server}metadata/"
TARGET_URL = f"{config.server}targets/"

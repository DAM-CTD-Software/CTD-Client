import sys
from pathlib import Path

from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.configurationhandler import InvalidConfigFile
from ctdclient.utils import get_config_path
from ctdclient.utils import individual_dship_api_call
from ctdclient.eventmanager import EventManager
from ctdclient.version import __version__

if getattr(sys, "frozen", False):
    ROOT_PATH = Path(sys.executable).parent
    RESSOURCES_PATH = Path(sys._MEIPASS)
else:
    RESSOURCES_PATH = ROOT_PATH = Path(__file__).absolute().parents[2]
CONFIG_PATH = get_config_path(ROOT_PATH, RESSOURCES_PATH)
try:
    config = ConfigurationFile(CONFIG_PATH)
    WRONG_CONFIG = False
except InvalidConfigFile:
    CONFIG_PATH.replace(f"misconfigured_{CONFIG_PATH.name}")
    CONFIG_PATH = get_config_path(ROOT_PATH, RESSOURCES_PATH)
    config = ConfigurationFile(CONFIG_PATH)
    WRONG_CONFIG = True
VERSION = __version__
THEMES_PATH = RESSOURCES_PATH.joinpath("ctktheme.json")
ICON_PATH = RESSOURCES_PATH.joinpath("icon.ico")
TEMPLATE_PATH = RESSOURCES_PATH.joinpath("templates")
PROCESSING_TEMPLATE_PATH = TEMPLATE_PATH.joinpath("processing_template.toml")

# update specifics
INSTALL_DIR = RESSOURCES_PATH.joinpath("updates")
TUFUP_METADATA = INSTALL_DIR.joinpath("metadata")
TUFUP_TARGET = INSTALL_DIR.joinpath("targets")
# ensure, that directory exists
if not TUFUP_TARGET.exists():
    TUFUP_TARGET.mkdir(parents=True)
if not config.server[-1] == "/":
    config.server = f"{config.server}/"
METADATA_URL = f"{config.server}metadata/"
TARGET_URL = f"{config.server}targets/"

# retrieve very basic dship information
url = f"{config.dship_ip}{config.dship_url_part}"
cruise_name = individual_dship_api_call(
    f"{url}/{config.dship_api_target_names['Cruise']}"
)
cruise_name = cruise_name if cruise_name else "unknown"
# TODO: add cruise head parameter
# cruise_head = individual_dship_api_call(
#     f'{url}/ADD_PARAMETER_HERE')
# cruise_head = cruise_head if cruise_head else "unknown"
cruise_head = "unknown"

global last_ctd_station
last_ctd_station = ""

event_manager = EventManager()

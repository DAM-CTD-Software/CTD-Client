import sys
from pathlib import Path

from platformdirs import user_config_dir

from ctdclient.configurationhandler import ConfigurationFile, InvalidConfigFile
from ctdclient.eventmanager import EventManager
from ctdclient.utils import (
    create_new_config_file,
    get_config_path,
    individual_dship_api_call,
)
from ctdclient.version import __version__

if getattr(sys, "frozen", False):
    ROOT_PATH = Path(sys.executable).parent
    RESOURCES_PATH = Path(sys._MEIPASS)
else:
    ROOT_PATH = Path(__file__).absolute().parents[2]
    RESOURCES_PATH = ROOT_PATH.joinpath("resources")
VERSION = __version__
THEMES_PATH = RESOURCES_PATH.joinpath("ctktheme.json")
ICON_PATH = RESOURCES_PATH.joinpath("icon.ico")
TEMPLATE_PATH = RESOURCES_PATH.joinpath("templates")
PROCESSING_TEMPLATE_PATH = TEMPLATE_PATH.joinpath("processing_template.toml")
CONFIG_PATH = Path(user_config_dir("ctdclient"))
CONFIG_FILE_PATH = get_config_path(CONFIG_PATH, TEMPLATE_PATH)
try:
    config = ConfigurationFile(CONFIG_FILE_PATH)
    WRONG_CONFIG = False
except InvalidConfigFile:
    create_new_config_file(
        CONFIG_FILE_PATH, TEMPLATE_PATH.joinpath("ctdclient.toml")
    )
    config = ConfigurationFile(CONFIG_FILE_PATH)
    WRONG_CONFIG = True

# retrieve very basic dship information
url = f"{config.dship_ip}{config.dship_url_part}"
cruise_name = individual_dship_api_call(
    f"{url}/{config.dship_api_target_names['Cruise']}"
)
cruise_name = cruise_name if cruise_name else "unknown"
cruise_head = "unknown"

global last_ctd_station
last_ctd_station = ""

event_manager = EventManager()

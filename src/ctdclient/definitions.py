import sys
import importlib.metadata
from pathlib import Path
import argparse

from ctdclient.utils import get_config_path


# parser = argparse.ArgumentParser()
# parser.add_argument(
#     '--dship_present',
#     '-s',
#     # type=bool,
#     default=True,
#     action="store_false",
#     help="Whether on a ship with dship running. DEFAULT=True"
#     )
# parser.add_argument(
#     '--dev',
#     '-d',
#     # type=bool,
#     default=False,
#     action="store_true",
#     help="Whether in a development environment with respective paths. DEFAULT=False"
#     )
# parser.add_argument(
#     '--update_server',
#     '-u',
#     type=str,
#     default="http://localhost:8000/",
#     help="The adress of the server from which to fetch updates."
# ) 
# args = parser.parse_args()
# 
# DSHIP = args.dship_present
# DEV = args.dev
# SERVER = args.update_server
DSHIP = False
DEV = False
SERVER = "http://localhost:8000/"
UPDATING = True

ROOT_PATH = Path(__file__).absolute().parents[2]
if getattr(sys, 'frozen', False):
    RESSOURCES_PATH = Path(sys._MEIPASS)
    FROZEN = True
else:
    RESSOURCES_PATH = ROOT_PATH
    FROZEN = False
CONFIG_PATH = get_config_path(ROOT_PATH, RESSOURCES_PATH)
VERSION = importlib.metadata.version("ctdclient")
THEMES_PATH = RESSOURCES_PATH.joinpath("ctktheme.json")
ICON_PATH = RESSOURCES_PATH.joinpath("icon.ico")
PROCESSING_TEMPLATE_PATH = RESSOURCES_PATH.joinpath("templates", "processing_template.toml")

# update specifics
INSTALL_DIR = RESSOURCES_PATH.joinpath("updates")
TUFUP_METADATA = INSTALL_DIR.joinpath("metadata")
TUFUP_TARGET = INSTALL_DIR.joinpath("target")
METADATA_URL = f"{SERVER}metadata/"
TARGET_URL = f"{SERVER}targets/"

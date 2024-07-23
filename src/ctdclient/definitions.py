import importlib.metadata
from pathlib import Path
import argparse

from ctdclient.utils import get_config_path


parser = argparse.ArgumentParser()
parser.add_argument(
    '--dship_present',
    '-s',
    # type=bool,
    default=True,
    action="store_false",
    help="Whether on a ship with dship running. DEFAULT=True"
)
parser.add_argument(
    '--dev',
    '-d',
    # type=bool,
    default=False,
    action="store_true",
    help="Whether in a development environment with respective paths. DEFAULT=False"
)
parser.add_argument(
    '--update_server',
    '-u',
    type=str,
    default="http://localhost:8000/",
    help="The adress of the server from which to fetch updates."
)
args = parser.parse_args()

DSHIP = args.dship_present
DEV = args.dev
SERVER = args.update_server

ROOT_PATH = Path(__file__).absolute().parents[2]
CONFIG_PATH = get_config_path()
VERSION = importlib.metadata.version("ctdclient")
THEMES_PATH = ROOT_PATH.joinpath("ctktheme.json")

# update specifics
INSTALL_DIR = ROOT_PATH.joinpath("updates")
TUFUP_METADATA = INSTALL_DIR.joinpath("metadata")
TUFUP_TARGET = INSTALL_DIR.joinpath("target")
METADATA_URL = f"{SERVER}metadata/"
TARGET_URL = f"{SERVER}target/"

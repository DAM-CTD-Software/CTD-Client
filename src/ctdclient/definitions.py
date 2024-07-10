from pathlib import Path

from ctdclient.utils import get_config_path


ROOT_PATH = Path(__file__).absolute().parents[2]
CONFIG_PATH = get_config_path()
THEMES_PATH = ROOT_PATH.joinpath("src/ctdclient/view/ctktheme.json")

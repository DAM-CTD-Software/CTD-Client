import platform
import sys
from pathlib import Path

from code_tools.logging import configure_logging
from code_tools.logging import get_logger

configure_logging("ctdclient.log")
logger = get_logger(__name__)


def get_config_path(dir_range: range = range(1, 4)) -> Path:
    if platform.system() == "Linux":
        config_name = "linux_config.toml"
    elif platform.system() == "Windows":
        config_name = "ctdclient.toml"
    else:
        logger.error("Unknown operating system. Aborting.")
        sys.exit(2)
    for dir_level in dir_range:
        dir = Path(__file__).absolute().parents[dir_level]
        file_path = dir.joinpath(config_name)
        if file_path.exists():
            return file_path
    logger.error("No configuration file found. Aborting.")
    sys.exit(1)

import shutil
from pathlib import Path

import pytest
import tomlkit
from conftest import config_template
from tomlkit.toml_file import TOMLFile

from ctdclient.configurationhandler import ConfigurationFile, InvalidConfigFile
from ctdclient.utils import _merge_dicts, create_new_config_file


def test_dict_difference_generation():
    one = {"a": 1, "b": 2, "c": 3}
    two = {"d": 4, "e": 5, "f": 6}
    _merge_dicts(one, two)
    assert len(one) == 6
    assert one["d"] == 4


def test_config_file_difference():
    # create dummy config that will be deleted after the test
    dummy_config = Path("test_ctdclient.toml")
    shutil.copyfile(config_template, dummy_config)
    new = TOMLFile(dummy_config).read()
    new.pop("email")
    new["base"].pop("processing_exes")
    with open(dummy_config, "w") as file:
        file.write(tomlkit.dumps(new).replace("\r", ""))
    updated = create_new_config_file(dummy_config, config_template)
    assert "email" in list(updated.keys())
    try:
        ConfigurationFile(dummy_config)
    except InvalidConfigFile:
        pytest.fail(f"Generated invalid configuration file:\n{updated}")
    else:
        dummy_config.unlink()

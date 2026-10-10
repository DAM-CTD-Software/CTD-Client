from pathlib import Path

import numpy as np
import pytest
import tomlkit
from conftest import output_name, raw_data_dir, target_file
from ctdam.parser import CnvFile

from ctdclient.definitions import CONFIG_PATH
from ctdclient.model.processing import ProcessingList, ProcessingProcedure


def test_processing_canceled_run(processing: ProcessingProcedure):
    processing.run(Path("ctdclient.toml"))
    processing.cancel()
    processing.process.join(timeout=5)
    assert processing.killed
    assert not processing.process.is_alive()


def test_processing_list_creation():
    proc_list = ProcessingList()
    proc_list.read_processing_files()
    assert len(proc_list) == len([file for file in CONFIG_PATH.glob("*proc*")])


def test_processing_passes_toml_settings(tmp_path: Path, mocker):
    settings = {
        "downcast_only": True,
        "remove_flags": True,
        "output_type": "cnv",
        "output_dir": str(tmp_path),
        "output_columns": ["Pressure", "Temperature"],
        "modules": {"alignctd": {"oxygen": 0.5}},
    }
    config_file = tmp_path / "processing.toml"
    config_file.write_text(tomlkit.dumps(settings))
    processing = ProcessingProcedure(config_file)
    ctdam_process = mocker.patch("ctdclient.model.processing.process")

    result = processing.apply_procedure(target_file)

    ctdam_process.assert_called_once_with(
        input=target_file,
        other_settings=settings,
        use_multiprocessing=False,
    )
    assert result is ctdam_process.return_value


@pytest.mark.parametrize(
    "input_file", [target_file, raw_data_dir / "EMB356_11-1.hex"]
)
def test_internal_processing(
    processing: ProcessingProcedure, input_file: Path, tmp_path: Path
):
    processing.configuration = {
        "modules": {"alignctd": {"oxygen": 0}},
        "output_type": "internal",
        "output_dir": str(tmp_path),
    }
    processing.run(input_file)
    processing.process.join(timeout=30)
    assert processing.process.exitcode == 0


def test_cnv_processing_successful(simple_processing: ProcessingProcedure):
    simple_processing.run(target_file)
    simple_processing.process.join(timeout=30)
    assert simple_processing.process.exitcode == 0
    output = Path(simple_processing.configuration["output_dir"]) / output_name
    exported = CnvFile(output).data
    original = CnvFile(target_file).data
    assert len(exported["prDM"]) > 0
    for column in ("t090C", "t190C"):
        np.testing.assert_allclose(
            exported[column], original[column], atol=0.0001
        )


@pytest.mark.xfail(
    strict=True,
    reason="CTDAM 2.14 needs upstream CNV export fixes for binned data",
)
def test_full_processing(processing: ProcessingProcedure, tmp_path: Path):
    processing.configuration = {
        "modules": {"alignctd": {}, "binavg": {}},
        "output_type": "cnv",
        "output_name": "binned.cnv",
        "output_dir": str(tmp_path),
    }
    input_file = raw_data_dir / "EMB356_11-1.hex"
    processing.run(input_file)
    processing.process.join(timeout=30)
    assert processing.process.exitcode == 0
    data = CnvFile(tmp_path / "binned.cnv").data
    assert len(data["prDM"]) > 0
    assert "t090C" in data
    assert "t190C" in data
    assert np.allclose(np.diff(data["prDM"]), 1)

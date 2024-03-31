import seabird_processing as sp
from pathlib import Path
import subprocess
from code_tools.logging import configure_logging, get_logger

from seabird_processing.configs import (
    AirPressureConfig,
    AlignCTDConfig,
    BinAvgConfig,
    BottleSumConfig,
    CellTMConfig,
    DatCnvConfig,
    DeriveConfig,
    DeriveTEOS10Config,
    FilterConfig,
    LoopEditConfig,
    SeaPlotConfig,
    SectionConfig,
    W_FilterConfig,
    WildEditConfig,
)

# maps processing step name to Class name inside of seabird_processing
config_classes = {
    "AirPressure": AirPressureConfig,
    "AlignCTD": AlignCTDConfig,
    "BinAvg": BinAvgConfig,
    "BottleSum": BottleSumConfig,
    "CellTM": CellTMConfig,
    "DatCnv": DatCnvConfig,
    "Derive": DeriveConfig,
    "DeriveTEOS10": DeriveTEOS10Config,
    "Filter": FilterConfig,
    "LoopEdit": LoopEditConfig,
    "SeaPlot": SeaPlotConfig,
    "Section": SectionConfig,
    "W_Filter": W_FilterConfig,
    "WildEdit": WildEditConfig,
}

configure_logging(f"{__name__}.log")
logger = get_logger(__name__)


class BatchProcessing:
    """
    Handles the collection of parameters and preparation needed to use the
    seabird_processing module of Hakai Institute.
    The individual processing steps are collected inside of a dictionary that
    holds the names and psas of the respective module. To this information,
    the Class heavily relies on paths that are set inside of the configuration
    file. The current setup needs an additional dictionary that maps the names
    of the procssing step to their respective class equivalents inside of the
    seabird_processing module, which is not able to handle these names itself.
    """

    def __init__(
        self,
        config,
        processing_steps: dict,
    ):
        self.raw_hex = config["user"]["paths"]["hex"]
        self.xmlcon = config["user"]["paths"]["xmlcon"]
        self.psa_folder = config["user"]["processing"]["psas"]
        self.outdir_path = config["user"]["paths"]["export_location"]
        self.processing_steps = processing_steps
        self.final_steps = {}

    def get_processing_configs(self):
        """Maps processing names inside the processing_steps dictionary to
        classes of the seabird_processing module. Constructs a new dictionary
        that fits those classes to the psas."""
        for step, psa in self.processing_steps.items():
            for step_name, proc_config in config_classes.items():
                if step.lower() == step_name.lower():
                    self.final_steps[proc_config] = psa
        assert len(self.processing_steps) == len(self.final_steps)

    def clean_psa_paths(self):
        """Makes sure that all the paths inside the dictionaries are absolute,
        by using the psa folder inside the config file as prefix."""
        for step, psa_string in self.processing_steps.items():
            psa = Path(psa_string)
            if psa.is_absolute():
                self.processing_steps[step] = psa
            else:
                self.processing_steps[step] = Path(self.psa_folder).joinpath(
                    psa
                )

    def create_config_objects(self) -> list:
        """Produces the config objects needed by the seabird_processing batch
        module. Brings all the needed information together and instantiates
        the processing objects. These are kept inside of a list which can
        directly be fed into the Batch class of seabird_processing."""
        self.clean_psa_paths()
        self.get_processing_configs()
        config_objects = []
        for step, psa in self.final_steps.items():
            processing_object = step(
                xmlcon=self.xmlcon, psa=psa, output_dir=self.outdir_path
            )
            config_objects.append(processing_object)
        return config_objects

    def run(self):
        """The main method of this Class, calls all the other methods and runs
        the processing steps as batch process, using Seabirds own batch
        processing routine."""
        config_objects = self.create_config_objects()
        batch_process = sp.Batch(config_objects)
        batch_process.run(str(self.raw_hex))


class WindowsBatch:
    """Simple class to only run the old windows batch we actually want to
    replace"""

    def __init__(
            self,
            batch: Path | str,
            hex_file: Path | str
        ):
        try:
            self.batch = Path(batch)
            self.hex_file = str(hex_file)[:-4]
        except TypeError as error:
            logger.error(f"Wrong input type: {error}")
        else:
            self.run(self.hex_file)

    def run(self, hex_file):
        try:
            ps = subprocess.Popen([self.batch, hex_file]) #, cwd=self.batch.parent)
            if ps.stdout:
                logger.debug(ps.stdout)
        except subprocess.CalledProcessError as error:
            if error.stderr:
                logger.error(error.stderr)
            raise error

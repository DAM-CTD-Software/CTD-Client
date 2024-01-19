import seabird_processing as sp
from pathlib import Path
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
    WildEditConfig
)

config_classes = {
    'AirPressure': AirPressureConfig,
    'AlignCTD': AlignCTDConfig,
    'BinAvg': BinAvgConfig,
    'BottleSum': BottleSumConfig,
    'CellTM': CellTMConfig,
    'DatCnv': DatCnvConfig,
    'Derive': DeriveConfig,
    'DeriveTEOS10': DeriveTEOS10Config,
    'Filter': FilterConfig,
    'LoopEdit': LoopEditConfig,
    'SeaPlot': SeaPlotConfig,
    'Section': SectionConfig,
    'W_Filter': W_FilterConfig,
    'WildEdit': WildEditConfig,
}


class BatchProcessing:

    def __init__(
            self,
            config,
            processing_steps: dict,
    ):
        self.raw_hex = config['user']['paths']['hex']
        self.xmlcon = config['user']['paths']['xmlcon']
        self.psa_folder = config['user']['processing']['psas']
        self.outdir_path = config['user']['paths']['export_location']
        self.processing_steps = processing_steps
        self.final_steps = {}

    def get_processing_configs(self):
        for step, psa in self.processing_steps.items():
            for step_name, proc_config in config_classes.items():
                if step.lower() == step_name.lower():
                    self.final_steps[proc_config] = psa
        assert len(self.processing_steps) == len(self.final_steps)

    def clean_psa_paths(self):
        for step, psa_string in self.processing_steps.items():
            psa = Path(psa_string)
            if psa.is_absolute():
                self.processing_steps[step] = psa
            else:
                self.processing_steps[step] = Path(
                    self.psa_folder).joinpath(psa)

    def create_config_objects(self):
        self.clean_psa_paths()
        self.get_processing_configs()
        config_objects = []
        for step, psa in self.final_steps.items():
            processing_object = step(
                xmlcon=self.xmlcon,
                psa=psa,
                output_dir=self.outdir_path)
            config_objects.append(processing_object)
        return config_objects

    def run(self):
        config_objects = self.create_config_objects()
        batch_process = sp.Batch(config_objects)
        batch_process.run(str(self.raw_hex))

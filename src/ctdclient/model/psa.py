import json
import xml.etree.ElementTree as ET
from collections import UserDict
from pathlib import Path

import xmltodict
from code_tools.logging import get_logger

logger = get_logger(__name__)


class XMLFile(UserDict):
    """Parent class for XML and psa representation that loads XML as a
    python-internal tree and as a dict.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, path_to_file):
        self.path_to_file = Path(path_to_file)
        self.file_name = self.path_to_file.stem
        self.file_dir = self.path_to_file.parents[0]
        self.input = ""
        with open(self.path_to_file, "r") as file:
            for line in file:
                self.input += line
        self.xml_tree = ET.fromstring(self.input)
        self.data = xmltodict.parse(self.input)

    def to_xml(self, file_name=None, file_path=None):
        file_path = self.file_dir if file_path is None else file_path
        file_name = self.file_name if file_name is None else file_name
        with open(
            Path(file_path).joinpath(file_name + self.path_to_file.suffix), "w"
        ) as file:
            file.write(xmltodict.unparse(self.data, pretty=True))
        logger.info(
            f"Wrote {self.path_to_file} to {
                file_name}{self.path_to_file.suffix}"
        )

    def to_json(self, file_name=None, file_path=None):
        """Writes the dictionary representation of the XML input to a json
        file.

        Parameters
        ----------
        file_name : str :
            the original files name (Default value = self.file_name)
        file_path : pathlib.Path :
            the directory of the file (Default value = self.file_dir)

        Returns
        -------

        """
        file_path = self.file_dir if file_path is None else file_path
        file_name = self.file_name if file_name is None else file_name
        with open(Path(file_path).joinpath(file_name + ".json"), "w") as file:
            json.dump(self.data, file, indent=4)
        logger.info(f"Wrote {self.path_to_file} to {file_name}.json.")


class XMLCONFile(XMLFile):

    def __init__(self, path_to_file):
        super().__init__(path_to_file)


class PsaFile(XMLFile):

    def __init__(self, path_to_file):
        super().__init__(path_to_file)


class SeasavePsa(PsaFile):

    def __init__(self, path_to_file):
        super().__init__(path_to_file)
        self.settings_part = self.data["SeasaveProgramSetup"]["Settings"]

    def set_metadata_header(self, metadata_list, header_prompt: bool = False):
        headerform = self.settings_part["HeaderForm"]
        header_dict = {}
        if header_prompt:
            header_choice = "2"
        else:
            header_choice = "1"
        header_dict["@HeaderChoice"] = header_choice
        prompt = []
        for index, value in enumerate(metadata_list):
            prompt_element = {}
            prompt_element["@index"] = str(index)
            prompt_element["@value"] = self.map_umlauts_for_seasave(value)
            prompt.append(prompt_element)
        header_dict["Prompt"] = prompt
        headerform = header_dict
        self.data["SeasaveProgramSetup"]["Settings"]["HeaderForm"] = headerform

    def map_umlauts_for_seasave(self, header_line: str) -> str:
        return (
            header_line
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
            .replace("Ä", "Ae")
            .replace("Ö", "Oe")
            .replace("Ü", "Ue")
        )

    def set_bottle_fire_info(self, bottle_info={}, number_of_bottles=13):
        watersampler = self.settings_part["WaterSamplerConfiguration"]
        for row in watersampler["AutoFireData"]["DataTable"]["Row"]:
            bottle_number = int(row["@BottleNumber"])
            if bottle_number <= number_of_bottles:
                try:
                    row["@FireAt"] = str(float(bottle_info[bottle_number]))
                except (KeyError, ValueError):
                    row["@FireAt"] = "0.0"
                except TypeError:
                    row["@FireAt"] = str(bottle_info[bottle_number])
        if len(bottle_info) == 0:
            watersampler["AutoFireData"]["@MaxPressureOrDepth"] = "0.000000"
        else:
            watersampler["AutoFireData"]["@MaxPressureOrDepth"] = "1000.000000"
        watersampler["@NumberOfWaterBottles"] = str(number_of_bottles)
        watersampler["@EnableRemoteFiring"] = "0"
        watersampler["AutoFireData"]["@AllowManualFiring"] = "1"
        self.data["SeasaveProgramSetup"]["Settings"][
            "WaterSamplerConfiguration"
        ] = watersampler

    def set_xmlcon_file_path(self, xmlcon_path):
        self.settings_part["ConfigurationFilePath"]["@value"] = xmlcon_path

    def set_hex_file_path(self, hex_path):
        self.settings_part["DataFilePath"]["@value"] = hex_path

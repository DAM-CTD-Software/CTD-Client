from code_tools.logging import get_logger
from ctdclient.configurationhandler import ConfigurationFile

logger = get_logger(__name__)


class MetadataHeader:

    @classmethod
    def build_metadata_header(
        cls,
        configuration: ConfigurationFile,
        dship_values: dict,
        platform: str,
        cast: str,
        operator: str,
        pos_alias: str = "",
        autostart: bool = False,
    ):
        """
        Generates the metadata header in the needed format and saves the last
        operator.

        Parameters
        ----------
        operator :


        Returns
        -------

        """
        configuration.operators["last"] = operator
        configuration.last_cast = int(cast)
        configuration.write(platform)
        if platform == "Scanfish":
            platform = "sfCTD"
        header_list = []
        for name, value in dship_values.items():
            header_list.append(cls.create_metadata_header_line(name, value))
        header_list.insert(
            2, cls.create_metadata_header_line("Platform", platform)
        )
        header_list.insert(
            3, cls.create_metadata_header_line("Cast", f"{int(cast):04d}")
        )
        header_list.insert(
            4, cls.create_metadata_header_line("Operator", operator)
        )
        header_list.insert(
            10,
            cls.create_metadata_header_line(
                "WsStartID", f"{int(cast)*25 + 1}"
            ),
        )
        if pos_alias:
            header_list[-1] = cls.create_metadata_header_line(
                "Pos_Alias", pos_alias
            )
        configuration.psa.set_metadata_header(header_list, autostart)
        header_print = "\n".join(header_list)
        logger.info(f"Wrote the following metadata header:\n{header_print}")
        return header_print

    @classmethod
    def create_metadata_header_line(cls, name, value):
        return f"{name} = {value}"

    @classmethod
    def format_dship_response(cls, name, value):
        if name == "Station":
            try:
                _, action_log_info = value.split("_")
                station, event = action_log_info.split("-")
                formatted_value = f"{int(station):03d}-{int(event):02d}"
            except AttributeError:
                formatted_value = "000-00"
        elif name == "GPS_Lat":
            try:
                first_part, second_part = value.split()
                formatted_value = f"{first_part} {float(second_part):2.3f} N"
            except ValueError:
                formatted_value = f"{float(value):2.3f} N"
        elif name == "GPS_Lon":
            try:
                first_part, second_part = value.split()
                if float(second_part) < 10:
                    gap = "  "
                else:
                    gap = " "
                formatted_value = (
                    f"{first_part}{gap}{float(second_part):2.3f} E"
                )
            except ValueError:
                formatted_value = f"{float(value):2.3f} E"
        elif name == "Echo_Depth":
            formatted_value = f"{float(value): .1f} m"
        elif name == "Air_Pressure":
            formatted_value = f"{float(value): .1f} hPa"
        else:
            formatted_value = value
        return formatted_value

    @classmethod
    def build_file_name(
        cls,
        dship_values: dict,
        cast_number: int,
        platform: str,
    ):
        try:
            cruise = dship_values["Cruise"]
            # handle special case when a cruise consists of two separate legs
            # and indicates that by a /
            try:
                if "/" in cruise:
                    cruise = cruise.replace("/", "_")
            except TypeError:
                pass
        except KeyError:
            cruise = ""
        station = dship_values["Station"]
        platform_name_mapper = {
            "CTD": "CTD",
            "vCTD": "CTD",
            "Scanfish": "SF",
            "pCTD": "pCTD",
        }
        return f"{cruise}_{station}_{platform_name_mapper[platform]}_{cast_number:04d}.hex"

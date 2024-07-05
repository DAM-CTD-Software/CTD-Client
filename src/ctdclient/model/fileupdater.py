from pathlib import Path


class UpdateFiles:

    def __init__(
        self,
        file_path: str | Path,
        file_dir: str | Path,
        station_event_info: str,
        auto_run=True,
    ):
        self.file_path = Path(file_path)
        self.file_name = self.file_path.stem
        self.file_dir = Path(file_dir)
        if self.check_file_name() and auto_run:
            self.file_list = self.find_all_files()
            self.new_name = self.create_new_file_name(
                self.file_name, station_event_info
            )
            self.replace_metadata_header_info(station_event_info)
            self.rename_files(self.file_list, self.new_name)

    def check_file_name(self) -> bool:
        if self.file_name.split("-")[0].endswith("000"):
            return True
        else:
            return False

    def find_all_files(self) -> list[Path]:
        out_list = []
        for file in self.file_dir.iterdir():
            if file.stem == self.file_name:
                out_list.append(self.file_dir.joinpath(file))
        return out_list

    def rename_files(self, file_list: list[Path], new_name: str):
        for file in file_list:
            file.rename(f"{self.file_dir}/{new_name}{file.suffix}")

    def create_new_file_name(self, old_name: str, station_data: str) -> str:
        individual_name_parts = old_name.split("_")
        try:
            cruise_id, station_event_info = station_data.split("_")
        except ValueError:
            cruise_id, _, station_event_info = station_data.split("_")
        station, event = station_event_info.split("-")
        for index, part in enumerate(individual_name_parts):
            if index == 0:
                part = cruise_id.replace("/", "_")
            if part == "000-00":
                individual_name_parts[index] = (
                    f"{
                    int(station):03d}-{int(event):02d}"
                )
        return "_".join(individual_name_parts)

    def replace_metadata_header_info(self, station_event_info):
        with open(self.file_dir.joinpath(self.file_path), "r") as file:
            contents = file.readlines()

        for index, line in enumerate(contents):
            if line.startswith("** Station"):
                line = f"** Station = {station_event_info.replace("/", "_")}\n"
                contents[index] = line
                break

        with open(self.file_dir.joinpath(self.file_path), "w") as file:
            contents = "".join(contents)
            file.write(contents)

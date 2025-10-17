import logging
from pathlib import Path

from ctdclient.definitions import config
from ctdclient.definitions import CONFIG_PATH
from ctdclient.definitions import event_manager
from processing.visualize import basic_bokeh_plot
from processing.visualize import cruise_plots

logger = logging.getLogger(__name__)


class Plotting:
    def __init__(self) -> None:
        if bool(config.plotting["auto_plot"]):
            event_manager.subscribe(
                "processing_successful", self.run_auto_plotting
            )

    def check_html_dir(self):
        html_dir = Path(config.plotting["plot_dir"]).absolute()
        if not html_dir.exists():
            html_dir.mkdir(parents=True)

    def plot_file(self, file: Path | str = "", show_plot: bool = True):
        self.check_html_dir()
        try:
            basic_bokeh_plot(
                cnv=file,
                print_plot=True,
                output_name=Path(file).with_suffix(".html").name,
                output_directory=config.plotting["plot_dir"],
                metadata=True,
                show_plot=show_plot,
                config_path=CONFIG_PATH.joinpath("vis_config.toml"),
            )
        except Exception as error:
            logger.error(f"Could not plot {file}: {error}")

    def plot_cruise(
        self,
        dir: str = "",
        no_new_plots: bool = False,
    ):
        self.check_html_dir()
        dir = dir if dir else str(config.output_directory)
        logger.debug(f"Plotting configuration: {config.plotting}")
        config.write()
        try:
            cruise_plots(
                directory=dir,
                output_directory=config.plotting["plot_dir"],
                output_name="main.html",
                embed_contents=config.plotting["embed_contents"],
                html_title=config.plotting["html_title"],
                overwrite=config.plotting["overwrite"],
                no_new_plots=no_new_plots,
                size_limit=int(config.plotting["size_limit"]),
                filter=config.plotting["filter"],
                show_html=config.plotting["show_html"],
            )
        except Exception as error:
            logger.error(f"Could not create cruise plot: {error}")

    def run_auto_plotting(self, target: Path):
        if not target.exists():
            return
        self.plot_file(target, show_plot=False)
        self.plot_cruise(no_new_plots=True)

    def toggle_auto_plot(self, new_value: bool | None = None):
        config.plotting["auto_plot"] = (
            new_value
            if isinstance(new_value, bool)
            else not config.plotting["auto_plot"]
        )
        if config.plotting["auto_plot"]:
            event_manager.subscribe(
                "processing_successful", self.run_auto_plotting
            )
        else:
            event_manager.unsubscribe(
                "processing_successful", self.run_auto_plotting
            )

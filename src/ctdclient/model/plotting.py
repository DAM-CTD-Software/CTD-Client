import logging
import shutil
from pathlib import Path

from ctdam.vis import basic_bokeh_plot, cruise_plots

from ctdclient.definitions import (
    CONFIG_PATH,
    TEMPLATE_PATH,
    config,
    event_manager,
)
from ctdclient.utils import call_editor

logger = logging.getLogger(__name__)


class Plotting:
    """Organizes plotting logic."""

    def __init__(self) -> None:
        if bool(config.plotting["auto_plot"]):
            event_manager.subscribe(
                "processing_successful", self.run_auto_plotting
            )
        self.config_name = "vis_config.toml"
        self.config_path = CONFIG_PATH.joinpath(self.config_name)
        self._check_config()
        logger.debug(self.config_path)

    def _check_config(self):
        """Handles initialization of new config if none found."""
        if not self.config_path.exists():
            shutil.copy(
                TEMPLATE_PATH.joinpath(self.config_name), self.config_path
            )

    def check_html_dir(self):
        """Handles initialization of new html directory if none found."""
        html_dir = Path(config.plotting["plot_dir"]).absolute()
        if not html_dir.exists():
            html_dir.mkdir(parents=True)

    def plot_file(self, file: Path | str = "", show_plot: bool = True):
        """
        Runs plotting logic from ctdam python package on single file.

        Parameters
        ----------
        file: Path | str
            The target file to plot
        show_plot: bool
            Whether to open the plot in webbrowser automatically
        """
        self.check_html_dir()
        try:
            basic_bokeh_plot(
                cnv=file,
                print_plot=True,
                output_name=Path(file).with_suffix(".html").name,
                output_directory=config.plotting["plot_dir"],
                metadata=True,
                show_plot=show_plot,
                config_path=self.config_path,
            )
        except Exception as error:
            logger.error(f"Could not plot {file}: {error}")

    def plot_cruise(
        self,
        dir: str = "",
        no_new_plots: bool = False,
    ):
        """
        Runs plotting logic from ctdam python package on whole cruise.

        Parameters
        ----------
        dir: str
            The directory of target files to plot
        no_new_plots: bool
            Whether to overwrite existing plots or not
        """
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
                config_path=self.config_path,
            )
        except Exception as error:
            logger.error(f"Could not create cruise plot: {error}")

    def run_auto_plotting(self, target: Path):
        """
        Performs single plotting and update of cruise plot html.

        Parameters
        ----------
        target: Path
            The target file to plot
        """
        if not target.exists():
            return
        self.plot_file(target, show_plot=False)
        self.plot_cruise(no_new_plots=True)

    def toggle_auto_plot(self, new_value: bool | None = None):
        """
        Toggle whether to automatically plot new files or not.

        Parameters
        ----------
        new_value: bool | None
            The new plot option
        """
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

    def open_config(self):
        """Open plot configuration in a file editor."""
        logger.debug(
            f"Opening plotting config file: {self.config_path.absolute()}"
        )
        call_editor(self.config_path)

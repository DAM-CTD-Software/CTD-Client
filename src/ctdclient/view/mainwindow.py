from typing import Type

import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.definitions import INSTALL_DIR
from ctdclient.definitions import METADATA_URL
from ctdclient.definitions import TARGET_URL
from ctdclient.definitions import TUFUP_METADATA
from ctdclient.definitions import TUFUP_TARGET
from ctdclient.definitions import VERSION
from ctdclient.definitions import UPDATING
from ctdclient.view.tabview import TabView
from CTkMessagebox import CTkMessagebox

from tufup.client import Client


class MainWindow(ctk.CTkFrame):

    def __init__(
        self,
        parent: ctk.CTk,
        config: ConfigurationFile,
        tab_dict: dict[str, Type[ctk.CTkFrame]],
    ):
        super().__init__(parent)

        self.tabs = TabView(
            window=self,
            configuration=config,
            tabs=tab_dict,
            width=600,
            height=700,
            # command=self.update_config_values,
        )
        self.tabs.grid()
        if UPDATING:
            self.tufup_client = Client(
                app_name="CTD-Client",
                app_install_dir=INSTALL_DIR,
                current_version=VERSION,
                metadata_dir=TUFUP_METADATA,
                metadata_base_url=METADATA_URL,
                target_dir=TUFUP_TARGET,
                target_base_url=TARGET_URL,
            )

    def check_for_update(self):
        update = self.tufup_client.check_for_updates()
        if update:
            answer = CTkMessagebox(
                title="Update available",
                message=f"A new version of this software is available: v{
                    update.version} . Do you want to update now? You will be able to use this software as normal during the process. For the changes to take effect, you will need to restart this software though.",
                option_1="Update now",
                option_2="Update later",
                option_3="Show update details",
            )
            if answer.get() == "Update now":
                self.update()
            if answer.get() == "Update later":
                return
            if answer.get() == "Show update details":
                CTkMessagebox(
                    title="Update details",
                    message=update.custom["changes"],
                    option_1="Ok",
                )

    def update(self):
        self.tufup_client.download_and_apply_update(
            skip_confirmation=True,
            progress_hook=self.update_progress,
            purge_dst_dir=False,
            exclude_from_purge=None,
            log_file_name="install.log",
        )

    def update_progress(self, bytes_downloaded: int, bytes_expected: int):
        progress_in_percent = bytes_downloaded / bytes_expected * 100
        # TODO: use ctk progress bar here

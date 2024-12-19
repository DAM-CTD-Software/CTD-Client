import shutil
import sys
import tkinter.font as tkFont
from pathlib import Path
from typing import Type

import customtkinter as ctk
import psutil
from code_tools.logging import configure_logging
from code_tools.logging import get_logger
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.maincontroller import MainController
from ctdclient.definitions import config
from ctdclient.definitions import ICON_PATH
from ctdclient.definitions import METADATA_URL
from ctdclient.definitions import RESSOURCES_PATH
from ctdclient.definitions import ROOT_PATH
from ctdclient.definitions import TARGET_URL
from ctdclient.definitions import THEMES_PATH
from ctdclient.definitions import TUFUP_METADATA
from ctdclient.definitions import TUFUP_TARGET
from ctdclient.definitions import VERSION
from ctdclient.definitions import WRONG_CONFIG
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.mainwindow import MainWindow
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.processing import ProcessingView
from CTkMessagebox import CTkMessagebox
from tufup.client import Client

configure_logging("ctdclient.log")
logger = get_logger(__name__)

global UPDATED
UPDATED = False


def main():
    """The main entry point of the software."""
    if check_if_running():
        sys.exit("CTD-Client is already running.")
    configuration_file = config
    # set ctk options
    root = ctk.CTk()
    root.title(f"DAM CTD Software v{VERSION}")
    # Because CTkToplevel currently is bugged on windows
    # and doesn't check if a user specified icon is set
    # we need to set the icon again after 200ms
    if sys.platform.startswith("win"):
        root.after(200, lambda: root.iconbitmap(ICON_PATH))

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    root.option_add("*Font", default_font)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(str(THEMES_PATH))
    root.geometry("700x780")
    # initialize objects
    main_window = MainWindow(
        parent=root,
        config=configuration_file,
        tab_dict=create_tabs(configuration_file),
    )
    main_controller = MainController(configuration_file, main_window)

    # check for update upon start
    if configuration_file.updating:
        try:
            tufup_client = Client(
                app_name="CTD-Client",
                app_install_dir=ROOT_PATH,
                current_version=VERSION,
                metadata_dir=TUFUP_METADATA,
                metadata_base_url=METADATA_URL,
                target_dir=TUFUP_TARGET,
                target_base_url=TARGET_URL,
            )
            main_window.after(
                5000, check_for_update, tufup_client, main_window
            )
        except FileNotFoundError as error:
            logger.error(f"Could not initiate updating: {error}")

    if WRONG_CONFIG:
        main_window.after(2000, inform_about_bad_config, main_window)

    main_window.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()
    # clean up for shutdown
    main_controller.kill_threads()


def check_if_running() -> bool:
    """Checks, whether CTD-Client is already running"""
    current_process_name = "ctdclient"
    current_process_name += ".exe" if sys.platform.startswith("win") else ""
    for process in psutil.process_iter():
        try:
            # skip the process if its this one (using the process' creation
            # time here, as this software is multithreaded and spans three
            # processes upon starting, so PID would not be enough.)
            if process.create_time() != psutil.Process().create_time():
                if current_process_name == process.name():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


def inform_about_bad_config(main_window):
    answer = CTkMessagebox(
        title="Misconfigured config file",
        message="Your configuration file seems to be misformed. A new one has been generated and is being used for this session. Please make sure that all the necessary settings are correct.",
        icon="warning",
        option_1="Ok",
    )
    if answer.get() == "Ok":
        main_window.tabs.configuration.tabs.set("expert settings")
        main_window.tabs.set("configuration")
        CTkMessagebox(
            title="Caution",
            message="These settings can break the application, proceed with caution and only if you know what you are doing.",
            option_1="Ok",
        )


def check_for_update(tufup_client: Client, main_window: MainWindow):
    try:
        check_update = tufup_client.check_for_updates()
    except RuntimeError as error:
        message = f"Could not fetch software updates: {error}"
        logger.info(message)
        print(message)
    else:
        if check_update:
            answer = CTkMessagebox(
                title="Update available",
                message=f"A new version of this software is available: v{
                    check_update.version} . Do you want to update now? You will be able to use this software as normal during the process. For the changes to take effect, you will need to restart this software though.",
                option_1="Update now",
                option_2="Update later",
                # option_3="show update details",
            )
            if answer.get() == "Update now":
                update(tufup_client)
                logger.info(
                    f"Updated succesfully from version {
                        VERSION} to {check_update.version}"
                )
            if answer.get() == "Update later":
                return
            # TODO: implement update message routine
            # if answer.get() == "Show update details":
            #     try:
            #         message = check_update.custom["changes"]
            #     except AttributeError:
            #         message = "No information given."
            #     CTkMessagebox(
            #         title="Update details",
            #         message="dummy text",
            #         option_1="Ok",
            #     )
            #     answer = CTkMessagebox(
            #         title="Update",
            #         message="Do you want to update?",
            #         option_1="Now",
            #         option_2="Later",
            #     )
            #     if answer.get() == "Now":
            #         update(tufup_client)
    # check daily for new updates
    main_window.after(
        24 * 3600 * 1000, check_for_update, tufup_client, main_window
    )


def update(tufup_client: Client):
    tufup_client.download_and_apply_update(
        skip_confirmation=True,
        install=installation_procedure,
        progress_hook=update_progress,
        log_file_name="install.log",
    )
    CTkMessagebox(
        title="Updated",
        message="The software has successfully been updated. You need to restart the application in order to use the new features.",
        option_1="Ok",
    )


def installation_procedure(src_dir: Path, dst_dir: Path, **kwargs):
    # rename exe in root dir
    new_temp_name = ROOT_PATH.joinpath(".old.exe")
    if new_temp_name.exists():
        new_temp_name.unlink()
    shutil.move(ROOT_PATH.joinpath("ctdclient.exe"), new_temp_name)
    # move extracted new files into root dir
    for file in src_dir.iterdir():
        if file.name in ("ctdclient.exe", "update_fixer.bat"):
            shutil.move(file, dst_dir)
    # delete the tmp update directory and its files
    shutil.rmtree(src_dir)
    # sets flag so that the old exe will be deleted
    global UPDATED
    UPDATED = True


def update_progress(bytes_downloaded: int, bytes_expected: int):
    progress_in_percent = bytes_downloaded / bytes_expected * 100
    # TODO: use ctk progress bar here
    print(progress_in_percent)


def create_tabs(config: ConfigurationFile) -> dict[str, Type[CtkFrame]]:
    # TODO: implement config part to allow tab selection
    tab_dict = {
        "measurement": MeasurementView,
        "processing": ProcessingView,
        "configuration": ConfigurationView,
    }
    return tab_dict


if __name__ == "__main__":
    # necessary for PyInstaller, to avoid spawning endless loops of the Clients
    # process. See https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html
    import multiprocessing

    multiprocessing.freeze_support()

    main()

    if UPDATED:
        import os

        old_path = RESSOURCES_PATH.joinpath("update_clean_up.bat")
        if not old_path.is_absolute():
            old_path = old_path.absolute()
        target_dir = old_path.parents[1]
        # move the batch file out of the tmp dir of the exe into its own tmp space
        shutil.copy(old_path, target_dir)
        os.startfile(
            target_dir.joinpath("update_clean_up.bat"),
            operation="open",
            arguments=str(ROOT_PATH.joinpath(".old.exe")),
        )
        # option to start a batch script for special update needs
        # needs to be deployed with the update
        update_fixing_script = ROOT_PATH.joinpath("update_fixer.bat")
        if update_fixing_script.exists():
            os.startfile(update_fixing_script)

    sys.exit(0)

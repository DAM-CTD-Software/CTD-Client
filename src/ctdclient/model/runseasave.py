import subprocess

from code_tools.logging import get_logger

logger = get_logger(__name__)


class RunSeasave:
    """
    Calls the seasave.exe with the specified command line arguments.
    In preparation for this, the Seasave.psa will be configured with the paths
    to XMLCON and hex file.
    """

    def __init__(self, config, hex_name, psa_output_name=None) -> None:
        self.config = config
        self.path_to_seasave_exe = self.config.path_to_seasave
        self.path_to_psa = self.config.seasave_psa
        self.hex_name = hex_name
        self.set_psa_run_info(psa_output_name)

    def run(self, downcast=True, autostart=True):
        """
        Executes the seasave.exe with given command line arguments.

        Parameters
        ----------
        downcast :
             (Default value = True)
        autostart :
             (Default value = True)

        Returns
        -------

        """
        run_command = [
            self.path_to_seasave_exe
        ] + self.set_seasave_command_line_parameters(downcast, autostart)
        try:
            ps = subprocess.Popen(run_command)
            if ps.stdout:
                logger.debug(ps.stdout)
        except subprocess.CalledProcessError as error:
            if error.stderr:
                logger.error(error.stderr)
            raise error
        except PermissionError as error:
            logger.error(
                f"Insufficient permissions to run the command {
                    run_command}: {error}"
            )
            raise error
        else:
            logger.info(
                f"Ran Seasave : {run_command}\nwith this psa: {
                    self.path_to_psa}\nand this file name: {self.hex_name}"
            )
            return ps

    def set_psa_run_info(self, psa_output_name=None):
        """Sets XMLCON and hex file paths in Seasave.psa."""
        self.config.psa.set_xmlcon_file_path(self.config.xmlcon)
        self.config.psa.set_hex_file_path(self.hex_name)
        self.config.psa.to_xml(file_name=psa_output_name)

    def set_seasave_command_line_parameters(
        self,
        downcast=True,
        autostart=False,
    ) -> list:
        """
        Builds command line argument list for usage in the run method.

        Parameters
        ----------
        downcast :

        autostart :


        Returns
        -------

        """
        parameters = []
        if autostart:
            parameters.append(f"-autostart={self.path_to_psa}")
        else:
            parameters.append(f"-p={self.path_to_psa}")
        if downcast:
            parameters.append("-autofireondowncast")
        return parameters

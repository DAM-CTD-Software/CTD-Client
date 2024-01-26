import subprocess
import logging

logger = logging.getLogger(__name__)


class RunSeasave:
    """ """

    def __init__(self, config) -> None:
        self.path_to_seasave_exe = config['paths']['seasave_exe']
        self.path_to_psa = config['user']['paths']['psa']
        self.config = config
        self.set_psa_run_info()

    def run(self, downcast=True, autostart=True):
        """

        Parameters
        ----------
        downcast :
             (Default value = True)
        autostart :
             (Default value = True)

        Returns
        -------

        """
        run_command = [self.path_to_seasave_exe] + \
            self.set_seasave_command_line_parameters(downcast, autostart)
        try:
            ps = subprocess.Popen(run_command)
            if ps.stdout:
                logger.debug(ps.stdout)
        except subprocess.CalledProcessError as e:
            if e.stderr:
                logger.error(e.stderr)
            raise e

    def set_psa_run_info(self):
        """ """
        self.config.psa.set_xmlcon_file_path(
            self.config['user']['paths']['xmlcon'])
        self.config.psa.set_hex_file_path(self.config['user']['paths']['hex'])
        self.config.psa.to_xml()

    def set_seasave_command_line_parameters(self, downcast, autostart) -> list:
        """

        Parameters
        ----------
        downcast :
            
        autostart :
            

        Returns
        -------

        """
        parameters = []
        if autostart:
            parameters.append(f'-autostart={self.path_to_psa}')
        else:
            parameters.append(f'-p={self.path_to_psa}')
        if downcast:
            parameters.append('-autofireondowncast')
        return parameters

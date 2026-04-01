import logging

logger = logging.getLogger(__name__)


class ModelMixin:
    """
    Adds a error message callback to Model classes.

    Not properly working and therefore not used at the moment.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_callback = []

    def raise_error_message(self, message: str):
        """
        Calls error message to be displayed in a view.

        Parameters
        ----------
        message: str
            The error message

        """
        try:
            self.error_callback(message)
        except Exception as error:
            logger.error(
                f"Error displaying error message: {
                    error
                }. Original error was: {message}"
            )

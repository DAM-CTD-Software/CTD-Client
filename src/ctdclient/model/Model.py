import logging

logger = logging.getLogger(__name__)


class ModelMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_callback = []

    def raise_error_message(self, message: str):
        try:
            self.error_callback(message)
        except Exception as error:
            logger.error(
                f"Error displaying error message: {
                    error
                }. Original error was: {message}"
            )

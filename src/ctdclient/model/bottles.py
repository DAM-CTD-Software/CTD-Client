import logging
from collections import Counter
from collections import UserDict

logger = logging.getLogger(__name__)


class BottleClosingDepths(UserDict):
    """
    Writes the pressure values one wants to close the bottles to the
    Seasave.psa in the required format. The class is instantiated with a
    default bottle layout which is set in the configuration file. To apply
    a closing setup, update_bottle_information() must be called with a dict
    of the following format:

            {BottleID: pressure value as difference from the air pressure,
                [str]: [str],
                    1: 4,
                    2: 6,
                    6: Bo}
    """

    def __init__(self, config) -> None:
        self.config = config
        self.instantiate_bottle_info()

    def instantiate_bottle_info(self):
        """Sets a default bottle layout according to the configuration file."""
        self.number_of_bottles = self.config.number_of_bottles
        self.data = {
            number + 1: "" for number in range(self.number_of_bottles)
        }

    def check_bottle_data(self, bottle_data_table: dict):
        bottle_data_table = {
            k: v.replace(",", ".")
            for k, v in bottle_data_table.items()
            if v != ""
        }
        # check for more than two bottles set to the same depth
        depth_counts = Counter(bottle_data_table.values())
        if [count for count in depth_counts.values() if count > 2]:
            logger.error(
                "Cannot close more than two bottles at the same depth automatically. Make sure to set the bottles to different depths or try to put your target bottles on the same release hook."
            )
            self.data = {1: "ERROR"}
            return

        items = sorted(bottle_data_table.items(), key=lambda x: x[1])
        adjusted_values = []
        for _, value in items:
            try:
                adjusted_values.append(float(value))
            except ValueError:
                continue

        for i in range(1, len(adjusted_values)):
            diff = adjusted_values[i] - adjusted_values[i - 1]
            if diff < self.config.minimum_bottle_diff:
                shift = (self.config.minimum_bottle_diff - diff) / 2
                adjusted_values[i - 1] -= shift
                adjusted_values[i] += shift

        new_data_table = {
            k: f"{v:.1f}" for (k, _), v in zip(items, adjusted_values)
        }
        for n in range(1, self.number_of_bottles + 1):
            if n not in new_data_table:
                new_data_table[n] = ""
        self.data = {k: v for k, v in sorted(new_data_table.items())}

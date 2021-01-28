__all__ = ["PMDComponent"]


class PMDComponent:
    """The PMD controller.

    Parameters
    ----------
    simulation_mode

    Attributes
    ----------
    position
    connected
    """

    def __init__(self, simulation_mode):
        self.position = None
        self.connected = False

    def connect(self):
        """Connect to the device."""
        self.connected = True

    def disconnect(self):
        """Disconnect from the device."""
        self.connected = False

    def configure(self, config):
        """Configure the device."""
        pass

    def get_position(self):
        """Get the position of the device."""
        self.position = 1

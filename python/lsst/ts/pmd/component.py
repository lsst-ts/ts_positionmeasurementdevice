__all__ = ["MitutoyoComponent"]

import math
import pty
import os

import serial

from .mock_server import MockSerial

SIMULATION_SERIAL_PORT = "/dev/ttyUSB0"


class MitutoyoComponent:
    """Mitutoyo controller.

    A class for the Mitutoyo dial gauge.

    Parameters
    ----------
    simulation_mode : `bool`
        Whether the component is in simulation mode.

    Attributes
    ----------
    position : `float`
        The position of the device.
    connected : `bool`
        Whether the device is connected.
    """

    def __init__(self, simulation_mode):
        self.position = [
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
        ]
        self.connected = False
        self.simulation_mode = bool(simulation_mode)
        self.names = ["", "", "", "", "", "", "", ""]

    def connect(self):
        """Connect to the device."""
        if not self.simulation_mode:
            self.commander = serial.Serial(port=SIMULATION_SERIAL_PORT)
        else:
            main, reader = pty.openpty()
            self.commander = MockSerial(os.ttyname(main))

        self.connected = True

    def disconnect(self):
        """Disconnect from the device."""
        self.connected = False

    def configure(self, config):
        """Configure the device.

        Parameters
        ----------
        config : `types.Simplenamespace`
            The configuration object.
        """
        for index, device in enumerate(config["devices"]):
            self.names[index] = device
        self.hub_type = config["hub_type"]
        self.units = config["units"]
        self.location = config["location"]

    def send_msg(self, msg):
        self.commander.write(f"{msg}\r".encode())
        try:
            reply = self.commander.read_until(b"\r")
            return reply
        except TimeoutError:
            reply = b"\r"
            return reply

    def get_slots_position(self):
        position = [
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
        ]
        for i, name in enumerate(self.names):
            if name == "":
                continue
            reply = self.send_msg(str(i + 1))
            if reply != b"\r":
                split_reply = reply.decode().split(":")
                position[i] = float(split_reply[-1])
            else:
                position[i] = math.nan
        return position

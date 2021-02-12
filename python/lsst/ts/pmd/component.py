__all__ = ["MitutoyoComponent"]

import math
import pty
import os

import serial

from .mock_server import MockSerial


class MitutoyoComponent:
    """Mitutoyo controller.

    A placeholder class for the Mitutoyo dial gauge.

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
        self.free_slots = 7
        self.simulation_mode = bool(simulation_mode)
        self.names = ""

    def connect(self):
        """Connect to the device."""
        if not self.simulation_mode:
            self.commander = serial.Serial(port="/dev/ttyUSB0")
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
        for device in config["devices"]:
            self.names += device + ","
            self.free_slots -= 1
        for slot in range(self.free_slots):
            self.names += ","
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

    def get_slots_value(self):
        self.get_slot_1_position()
        self.get_slot_2_position()
        self.get_slot_3_position()
        self.get_slot_4_position()
        self.get_slot_5_position()
        self.get_slot_6_position()
        self.get_slot_7_position()
        self.get_slot_8_position()

    def get_slot_1_position(self):
        """Get the position of the device."""
        reply = self.send_msg("1")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[0] = float(split_reply[-1])
        else:
            self.position[0] = math.nan

    def get_slot_2_position(self):
        reply = self.send_msg("2")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[1] = float(split_reply[-1])
        else:
            self.position[1] = math.nan

    def get_slot_3_position(self):
        reply = self.send_msg("3")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[2] = float(split_reply[-1])
        else:
            self.position[2] = math.nan

    def get_slot_4_position(self):
        reply = self.send_msg("4")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[3] = float(split_reply[-1])
        else:
            self.position[3] = math.nan

    def get_slot_5_position(self):
        reply = self.send_msg("5")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[4] = float(split_reply[-1])
        else:
            self.position[4] = math.nan

    def get_slot_6_position(self):
        reply = self.send_msg("6")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[5] = float(split_reply[-1])
        else:
            self.position[5] = math.nan

    def get_slot_7_position(self):
        reply = self.send_msg("7")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[6] = float(split_reply[-1])
        else:
            self.position[6] = math.nan

    def get_slot_8_position(self):
        reply = self.send_msg("8")
        if reply != b"\r":
            split_reply = reply.decode().split(":")
            self.position[7] = float(split_reply[-1])
        else:
            self.position[7] = math.nan

# This file is part of ts_pmd.
#
# Developed for the Vera Rubin Telescope and Site Project.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        """Send a message to the device.

        Parameters
        ----------
        msg : `str`
            The message to send.

        Raises
        ------
        Exception
            Raised when the device is not connected.

        Returns
        -------
        reply : `bytes`
            The reply from the device.
        """
        if not self.connected:
            raise Exception("Not connected")
        self.commander.write(f"{msg}\r".encode())
        try:
            reply = self.commander.read_until(b"\r")
            return reply
        except TimeoutError:
            reply = b"\r"
            return reply

    def get_slots_position(self):
        """Get all device slot positions.

        Raises
        ------
        Exception
            Raised when the device is not connected.

        Returns
        -------
        position : `list` of `float`
            An array of values from the devices.
        """
        if not self.connected:
            raise Exception("Not connected")
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

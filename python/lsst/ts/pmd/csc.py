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

__all__ = ["PMDCsc"]

import pathlib
import asyncio

from lsst.ts import salobj

from .component import MitutoyoComponent


class PMDCsc(salobj.ConfigurableCsc):
    """The CSC for the Position Measurement Device.

    Parameters
    ----------
    index : `int`
        The index of the CSC.
    simulation_mode : `int`
        Whether the CSC is in simulation mode.
    initial_state : `lsst.ts.salobj.State`
        The initial_state of the CSC.
    config_dir : `pathlib.Path`
        The path of the configuration directory.

    Attributes
    ----------
    telemetry_task : `asyncio.Future`
        The task for running the telemetry loop.
    telemetry_interval : `float`
        The interval that telemetry is published at. (Seconds)
    component : `MitutoyoComponent`
        The component for the PMD.
    """

    valid_simulation_modes = (0, 1)
    """The valid simulation modes for the PMD."""

    def __init__(
        self,
        index,
        simulation_mode=0,
        initial_state=salobj.State.STANDBY,
        config_dir=None,
        settings_to_apply="",
    ):
        schema_path = pathlib.Path(__file__).parents[4].joinpath("schema", "PMD.yaml")

        super().__init__(
            name="PMD",
            index=index,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
            schema_path=schema_path,
            settings_to_apply=settings_to_apply,
        )
        self.telemetry_task = salobj.make_done_future()
        self.telemetry_interval = 1
        self.index = index
        self.component = None

    async def configure(self, config):
        """Configure the CSC.

        Parameters
        ----------
        config : `types.Simplenamespace`
            The configuration object.
        """
        self.log.info(config)
        self.telemetry_interval = config.hub_config[self.index - 1][
            "telemetry_interval"
        ]
        if config.hub_config[self.index - 1]["hub_type"] == "Mitutoyo":
            self.component = MitutoyoComponent(self.simulation_mode)
        self.component.configure(config.hub_config[self.index - 1])
        self.evt_metadata.set_put(
            hubType=self.component.hub_type,
            location=self.component.location,
            names=",".join(self.component.names),
            units=self.component.units,
        )

    async def telemetry(self):
        """Execute the telemetry loop."""
        try:
            while True:
                self.log.debug("Begin sending telemetry")
                position = self.component.get_slots_position()
                self.tel_position.set_put(position=position)
                await asyncio.sleep(self.telemetry_interval)
        except asyncio.CancelledError:
            self.log.info("Telemetry loop cancelled")
        except Exception:
            self.log.exception("Telemetry loop failed")

    async def handle_summary_state(self):
        """Handle the summary states."""
        if self.disabled_or_enabled:
            if not self.component.connected:
                self.component.connect()
            if self.telemetry_task.done():
                self.telemetry_task = asyncio.create_task(self.telemetry())
        else:
            self.telemetry_task.cancel()
            if self.component is not None:
                self.component.disconnect()
                self.component = None

    async def close_tasks(self):
        """Close the CSC for cleanup."""
        await super().close_tasks()
        self.telemetry_task.cancel()
        self.component.disconnect()

    @staticmethod
    def get_config_pkg():
        """Get the configuration package directory."""
        return "ts_config_ocs"

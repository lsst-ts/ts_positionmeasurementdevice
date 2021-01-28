__all__ = ["PMDCsc"]

import pathlib
import asyncio

from lsst.ts import salobj

from .component import PMDComponent


class PMDCsc(salobj.ConfigurableCsc):
    """The CSC for the PMD.

    Parameters
    ----------
    index
    simulation_mode
    initial_state
    config_dir

    Attributes
    ----------
    telemetry_task
    telemetry_interval
    component
    """

    valid_simulation_modes = [0]
    """The valid simulation modes for the PMD."""

    def __init__(
        self,
        index,
        simulation_mode=0,
        initial_state=salobj.State.STANDBY,
        config_dir=None,
    ):
        schema_path = pathlib.Path(__file__).parents[4].joinpath("schema", "PMD.yaml")

        super().__init__(
            name="PMD",
            index=index,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
            schema_path=schema_path,
        )
        self.telemetry_task = salobj.make_done_future()
        self.telemetry_interval = 1
        self.component = None

    async def configure(self, config):
        """Configure the CSC."""
        self.telemetry_interval = config.telemetry_interval

    async def telemetry(self):
        """Execute the telemetry loop."""
        while True:
            self.log.debug("Begin sending telemetry")
            self.component.get_position()
            self.tel_position.set_put(position=self.component.position)
            await asyncio.sleep(self.telemetry_interval)

    async def handle_summary_state(self):
        """Handle the summary states."""
        if self.disabled_or_enabled:
            if self.component is None:
                self.component = PMDComponent(self.simulation_mode)
            if not self.component.connected:
                self.component.connect()
            if self.telemetry_task.done():
                self.telemetry_task = asyncio.create_task(self.telemetry())
        else:
            if self.component is not None:
                self.component.disconnect()
                self.component = None
            self.telemetry_task.cancel()

    async def close_tasks(self):
        """Close the CSC for cleanup."""
        await super().close_tasks()
        self.telemetry_task.cancel()
        self.component.disconnect()

    @staticmethod
    def get_config_pkg():
        """Get the configuration package directory."""
        return "ts_config_ocs"

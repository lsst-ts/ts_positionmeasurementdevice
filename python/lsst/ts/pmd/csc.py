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
        The interval that telemetry is published at.
    component : `MituyoyoComponent`
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
        self.telemetry_interval = config.hub_config[self.index - 1][
            "telemetry_interval"
        ]
        if config.hub_config[self.index - 1]["hub_type"] == "Mitutoyo":
            self.component = MitutoyoComponent(self.simulation_mode)
        self.component.configure(config.hub_config[self.index - 1])
        self.evt_metadata.set_put(
            hubType=self.component.hub_type,
            location=self.component.location,
            names=self.component.names,
            units=self.component.units,
        )

    async def telemetry(self):
        """Execute the telemetry loop."""
        try:
            while True:
                self.log.debug("Begin sending telemetry")
                self.component.get_slots_value()
                self.tel_position.set_put(position=self.component.position)
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

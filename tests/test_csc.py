import asynctest
import unittest

from lsst.ts import salobj, pmd


class PMDCscTestCase(asynctest.TestCase, salobj.BaseCscTestCase):
    def basic_make_csc(
        self, index, initial_state, config_dir=None, simulation_mode=0, **kwargs
    ):
        return pmd.PMDCsc(initial_state=initial_state, index=index)

    async def test_standard_state_transitions(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, index=1):
            await self.check_standard_state_transitions(enabled_commands=[])

    async def test_bin_script(self):
        await self.check_bin_script(
            name="PMD", exe_name="run_pmd.py", index=1,
        )

    async def test_telemetry(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, index=1):
            await self.assert_next_sample(topic=self.remote.tel_position, position=1)


if __name__ == "__main__":
    unittest.main()

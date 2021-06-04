import unittest
from lsst.ts.pmd.config_schema import CONFIG_SCHEMA

import jsonschema

from lsst.ts import salobj


class ValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.schema = CONFIG_SCHEMA
        self.validator = salobj.DefaultingValidator(schema=self.schema)

    def test_all_specified(self):
        data = {
            "hub_config": [
                {
                    "sal_index": 1,
                    "telemetry_interval": 1,
                    "devices": ["Dial Gage"],
                    "units": "um",
                    "location": "Office",
                    "serial_port": "/dev/ttyUSB0",
                    "hub_type": "Mitutoyo",
                }
            ]
        }
        data_copy = data.copy()
        result = self.validator.validate(data)
        self.assertEqual(data, data_copy)
        for field, value in data.items():
            self.assertEqual(result[field], value)

    def test_invalid_configs(self):
        good_data = {
            "hub_config": [
                {
                    "sal_index": 1,
                    "telemetry_interval": 1,
                    "devices": ["Dial Gage"],
                    "units": "um",
                    "location": "Office",
                    "serial_port": "/dev/ttyUSB0",
                    "hub_type": "Mitutoyo",
                }
            ]
        }
        bad_hub_items = {
            "hub_config": [
                {
                    "sal_index": 0,
                    "telemetry_interval": "Sandwich",
                    "devices": 1,
                    "units": "fff",
                    "location": 1,
                    "serial_port": 12,
                    "hub_type": "Sandwich",
                }
            ]
        }
        for name, bad_value in bad_hub_items.items():
            bad_data = good_data.copy()
            bad_data["hub_config"][0][name] = bad_value
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                self.validator.validate(bad_data)


if __name__ == "__main__":
    unittest.main()

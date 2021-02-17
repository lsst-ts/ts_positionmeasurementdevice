import unittest
import pathlib

import jsonschema
import yaml

from lsst.ts import salobj


class ValidationTestCase(unittest.TestCase):
    def setUp(self):
        schemaname = "PMD.yaml"
        pkg_dir = pathlib.Path(__file__).parents[1]
        schemapath = pkg_dir / "schema" / schemaname
        with open(schemapath, "r") as f:
            rawschema = f.read()
        self.schema = yaml.safe_load(rawschema)
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
        data = {
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
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            self.validator.validate(data)


if __name__ == "__main__":
    unittest.main()

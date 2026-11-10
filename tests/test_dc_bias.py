import unittest

from dc_bias import calculate_dc_bias, validate_dc_inputs


class TestDcBiasReference(unittest.TestCase):
    def test_reference_case_active_region(self):
        result = calculate_dc_bias(12, 100000, 22000, 2200, 1000, 100, 0.7)

        self.assertAlmostEqual(result["vth"], 2.16393442623, places=9)
        self.assertAlmostEqual(result["rth"], 18032.7868852459, places=6)
        self.assertAlmostEqual(result["ib"], 1.22985814626e-05, places=12)
        self.assertAlmostEqual(result["ic"], 0.00122985814626, places=12)
        self.assertAlmostEqual(result["ie"], 0.00124215672772, places=12)
        self.assertAlmostEqual(result["vb"], 1.94215672772, places=9)
        self.assertAlmostEqual(result["ve"], 1.24215672772, places=9)
        self.assertAlmostEqual(result["vc"], 9.29431207823, places=9)
        self.assertAlmostEqual(result["vce"], 8.0521553505, places=9)

        self.assertEqual(result["region"], "active")
        self.assertFalse(result.get("warnings"))

    def test_returns_expected_keys(self):
        result = calculate_dc_bias(12, 100000, 22000, 2200, 1000, 100, 0.7)
        for key in ("vth", "rth", "ib", "ic", "ie", "vb", "ve", "vc", "vce", "region", "warnings"):
            self.assertIn(key, result)


class TestDcBiasRegionsAndValidation(unittest.TestCase):
    def test_cutoff_when_vth_not_greater_than_vbe(self):
        # R2 very small -> VTH below VBE
        result = calculate_dc_bias(12, 100000, 1000, 2200, 1000, 100, 0.7)
        self.assertLessEqual(result["vth"], 0.7)
        self.assertEqual(result["region"], "cutoff")
        self.assertTrue(result.get("warnings"))

    def test_saturation_when_vce_low(self):
        # Very large RC drives VCE negative (deep saturation)
        result = calculate_dc_bias(12, 100000, 22000, 100000, 1000, 100, 0.7)
        self.assertLess(result["vce"], 0.2)
        self.assertEqual(result["region"], "saturation")
        self.assertTrue(result.get("warnings"))

    def test_validate_rejects_non_positive_and_missing(self):
        base = {"vcc": "12", "r1": "100000", "r2": "22000", "rc": "2200", "re": "1000", "beta": "100", "vbe": "0.7"}

        bad_cases = [
            ({**base, "r1": "0"}, "r1"),
            ({**base, "rc": "-10"}, "rc"),
            ({**base, "beta": "0"}, "beta"),
            ({**base, "vcc": "0"}, "vcc"),
            ({k: v for k, v in base.items() if k != "re"}, "re"),
            ({**base, "r2": "abc"}, "r2"),
        ]
        for values, expected_field in bad_cases:
            clean, errors = validate_dc_inputs(values)
            self.assertIsNone(clean)
            self.assertTrue(errors)
            fields = [e.get("field") for e in errors]
            self.assertIn(expected_field, fields)


if __name__ == "__main__":
    unittest.main()

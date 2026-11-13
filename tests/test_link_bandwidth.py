# Run from the repository root: python -m unittest discover -s tests
import contextlib
import io
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)

import helpers as hlp
import generate_inputs as igen
import rapidchiplet as rc
import validation as val


def make_inputs(base_chiplet_area, phy_area = 0.85):
	experiment = hlp.read_json(os.path.join(ROOT, "experiments", "example_experiment.json"))
	params = {k : v[0] for (k, v) in experiment.items() if type(v) == list and len(v) > 0}
	params["grid_scale"] = "2x2"
	params["base_chiplet_area"] = base_chiplet_area
	params["phy_area"] = phy_area
	inputs = igen.generate_inputs(params, "test_link_bandwidth", do_write = False)
	inputs["verbose"] = False
	inputs["validate"] = True
	return inputs


class TestPhyBandwidthValidation(unittest.TestCase):

	def setUp(self):
		self.old_cwd = os.getcwd()
		os.chdir(ROOT)

	def tearDown(self):
		os.chdir(self.old_cwd)

	def run_quietly(self, function, *args):
		out = io.StringIO()
		with contextlib.redirect_stdout(out):
			result = function(*args)
		return (result, out.getvalue())

	def test_example_design_is_valid(self):
		inputs = make_inputs(74)
		(bandwidths, _) = self.run_quietly(rc.compute_link_bandwidths, inputs, {})
		self.assertGreater(min(bandwidths.values()), 0)
		(errors, _) = self.run_quietly(val.validate_phy_bandwidths, inputs)
		self.assertEqual(errors, 0)

	def test_tiny_chiplet_is_reported(self):
		# A chiplet of 0.03 mm^2 plus four 0.02 mm^2 PHYs has too few bumps per PHY for the non-data wires, so the
		# computed link bandwidth is negative. This used to pass validation silently.
		inputs = make_inputs(0.03, phy_area = 0.02)
		(bandwidths, output) = self.run_quietly(rc.compute_link_bandwidths, inputs, {})
		self.assertLess(min(bandwidths.values()), 0)
		self.assertIn("VALIDATION ERROR", output)
		(errors, _) = self.run_quietly(val.validate_phy_bandwidths, inputs)
		self.assertGreater(errors, 0)

	def test_no_report_without_validation(self):
		inputs = make_inputs(0.03, phy_area = 0.02)
		inputs["validate"] = False
		(_, output) = self.run_quietly(rc.compute_link_bandwidths, inputs, {})
		self.assertNotIn("VALIDATION ERROR", output)


if __name__ == "__main__":
	unittest.main()

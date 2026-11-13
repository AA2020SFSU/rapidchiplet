# Run from the repository root: python -m unittest discover -s tests
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import run_experiment as rexp


class TestExperimentNames(unittest.TestCase):

	def test_ranged_file_parameter_gives_flat_names(self):
		# Two values for a file-path parameter used to produce names such as
		# "exp-inputs/packagings/a.json", and writing ./results/<name>.json then crashed.
		experiment = {
			"packaging_file" : ["inputs/packagings/a.json", "inputs/packagings/b.json"],
			"grid_scale" : ["4x4"],
		}
		names = sorted(rexp.compute_parameter_combinations(experiment, "exp").keys())
		self.assertEqual(names, ["exp-a", "exp-b"])
		for name in names:
			self.assertNotIn("/", name)

	def test_same_file_name_in_different_directories_stays_unique(self):
		experiment = {"packaging_file" : ["inputs/x/p.json", "inputs/y/p.json"]}
		names = sorted(rexp.compute_parameter_combinations(experiment, "exp").keys())
		self.assertEqual(len(names), 2)
		for name in names:
			self.assertNotIn("/", name)

	def test_non_path_values_keep_old_names(self):
		experiment = {
			"grid_scale" : ["4x4", "8x8"],
			"trace" : [[], ["a", "b"]],
		}
		names = sorted(rexp.compute_parameter_combinations(experiment, "exp").keys())
		self.assertEqual(names, ["exp-4x4-_", "exp-4x4-a_b", "exp-8x8-_", "exp-8x8-a_b"])


if __name__ == "__main__":
	unittest.main()

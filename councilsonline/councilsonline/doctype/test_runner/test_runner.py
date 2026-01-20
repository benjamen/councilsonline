# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import subprocess
import os
from datetime import datetime
import json


class TestRunner(Document):
	def before_save(self):
		"""Calculate success rate before saving"""
		if self.total_tests and self.total_tests > 0:
			self.success_rate = (self.passed_tests / self.total_tests) * 100


@frappe.whitelist()
def run_tests(test_suite, test_type="All", test_file=None):
	"""
	Run tests and create a Test Runner document to track execution

	Args:
		test_suite: Frontend Unit Tests, Frontend E2E Tests, Backend Unit Tests, etc.
		test_type: Unit, Integration, E2E, All
		test_file: Optional specific test file to run

	Returns:
		dict: Test Runner document name and initial status
	"""
	# Create Test Runner document
	test_runner = frappe.get_doc({
		"doctype": "Test Runner",
		"test_suite": test_suite,
		"test_type": test_type,
		"test_file": test_file,
		"status": "Pending",
		"started_at": datetime.now()
	})
	test_runner.insert()
	frappe.db.commit()

	# Run tests in background
	frappe.enqueue(
		method="councilsonline.councilsonline.doctype.test_runner.test_runner.execute_tests",
		test_runner_name=test_runner.name,
		queue="long",
		timeout=600
	)

	return {
		"name": test_runner.name,
		"status": "Running"
	}


def execute_tests(test_runner_name):
	"""
	Execute the actual tests and update the Test Runner document

	Args:
		test_runner_name: Name of the Test Runner document
	"""
	test_runner = frappe.get_doc("Test Runner", test_runner_name)
	test_runner.status = "Running"
	test_runner.save()
	frappe.db.commit()

	try:
		# Get app path
		app_path = frappe.get_app_path("councilsonline")
		frontend_path = os.path.join(os.path.dirname(app_path), "frontend")

		# Build command based on test suite
		cmd = []
		cwd = None

		if test_runner.test_suite == "Frontend Unit Tests":
			cwd = frontend_path
			cmd = ["npm", "run", "test:run"]
			if test_runner.test_file:
				cmd.append(test_runner.test_file)

		elif test_runner.test_suite == "Frontend E2E Tests":
			cwd = frontend_path
			cmd = ["npx", "playwright", "test"]
			if test_runner.test_file:
				cmd.append(test_runner.test_file)
			cmd.extend(["--reporter=json"])

		elif test_runner.test_suite == "Backend Unit Tests":
			cwd = frappe.get_site_path("..")
			cmd = ["bench", "run-tests", "--app", "councilsonline"]
			if test_runner.test_file:
				cmd.extend(["--module", test_runner.test_file])

		elif test_runner.test_suite == "Backend Integration Tests":
			cwd = frappe.get_site_path("..")
			cmd = ["bench", "run-tests", "--app", "councilsonline", "--integration"]

		elif test_runner.test_suite == "All Tests":
			# Run all test suites sequentially
			results = []
			for suite in ["Frontend Unit Tests", "Backend Unit Tests"]:
				result = frappe.get_doc({
					"doctype": "Test Runner",
					"test_suite": suite,
					"test_type": test_runner.test_type,
					"status": "Pending"
				})
				result.insert()
				frappe.db.commit()
				execute_tests(result.name)
				results.append(result.name)

			# Aggregate results
			test_runner.output = f"Executed {len(results)} test suites: {', '.join(results)}"
			test_runner.status = "Completed"
			test_runner.completed_at = datetime.now()
			test_runner.save()
			frappe.db.commit()
			return

		# Execute command
		process = subprocess.Popen(
			cmd,
			cwd=cwd,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)

		stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout

		# Parse output
		test_runner.output = stdout
		test_runner.error_output = stderr

		# Try to parse test results
		if "Frontend Unit Tests" in test_runner.test_suite:
			# Parse Vitest output
			lines = stdout.split("\n")
			for line in lines:
				if "Test Files" in line:
					# Example: "Test Files  1 failed | 5 passed (6)"
					parts = line.split()
					for i, part in enumerate(parts):
						if part == "failed" and i > 0:
							test_runner.failed_tests = int(parts[i-1])
						elif part == "passed" and i > 0:
							test_runner.passed_tests = int(parts[i-1])
				elif "Tests" in line and "passed" in line:
					# Example: "Tests  71 passed (71)"
					parts = line.split()
					for i, part in enumerate(parts):
						if part == "passed" and i > 0:
							test_runner.total_tests = int(parts[i-1])
							test_runner.passed_tests = int(parts[i-1])

		elif "Backend" in test_runner.test_suite:
			# Parse pytest/unittest output
			lines = stdout.split("\n")
			for line in lines:
				if " passed" in line or " failed" in line:
					# Try to extract counts
					import re
					passed_match = re.search(r'(\d+) passed', line)
					failed_match = re.search(r'(\d+) failed', line)
					if passed_match:
						test_runner.passed_tests = int(passed_match.group(1))
					if failed_match:
						test_runner.failed_tests = int(failed_match.group(1))
					test_runner.total_tests = (test_runner.passed_tests or 0) + (test_runner.failed_tests or 0)

		# Set status based on return code
		if process.returncode == 0:
			test_runner.status = "Completed"
		else:
			test_runner.status = "Failed"

		test_runner.completed_at = datetime.now()

		# Calculate duration
		if test_runner.started_at:
			duration = (test_runner.completed_at - test_runner.started_at).total_seconds()
			test_runner.duration = duration

		test_runner.save()
		frappe.db.commit()

	except Exception as e:
		frappe.log_error(f"Test execution failed: {str(e)}", "Test Runner Error")
		test_runner.status = "Failed"
		test_runner.error_output = str(e)
		test_runner.completed_at = datetime.now()
		test_runner.save()
		frappe.db.commit()


@frappe.whitelist()
def get_test_statistics():
	"""
	Get overall test statistics

	Returns:
		dict: Statistics about recent test runs
	"""
	# Get recent test runs (last 30 days)
	from frappe.utils import add_days, nowdate

	recent_tests = frappe.get_all(
		"Test Runner",
		filters={
			"creation": [">=", add_days(nowdate(), -30)]
		},
		fields=["name", "test_suite", "status", "total_tests", "passed_tests", "failed_tests", "duration", "creation"],
		order_by="creation desc",
		limit=50
	)

	# Calculate statistics
	total_runs = len(recent_tests)
	successful_runs = len([t for t in recent_tests if t.status == "Completed"])
	failed_runs = len([t for t in recent_tests if t.status == "Failed"])

	# Group by suite
	by_suite = {}
	for test in recent_tests:
		suite = test.test_suite
		if suite not in by_suite:
			by_suite[suite] = {
				"total_runs": 0,
				"successful": 0,
				"failed": 0,
				"total_tests": 0,
				"passed_tests": 0,
				"failed_tests": 0
			}

		by_suite[suite]["total_runs"] += 1
		if test.status == "Completed":
			by_suite[suite]["successful"] += 1
		elif test.status == "Failed":
			by_suite[suite]["failed"] += 1

		by_suite[suite]["total_tests"] += test.total_tests or 0
		by_suite[suite]["passed_tests"] += test.passed_tests or 0
		by_suite[suite]["failed_tests"] += test.failed_tests or 0

	return {
		"total_runs": total_runs,
		"successful_runs": successful_runs,
		"failed_runs": failed_runs,
		"success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
		"by_suite": by_suite,
		"recent_tests": recent_tests[:10]  # Last 10 test runs
	}

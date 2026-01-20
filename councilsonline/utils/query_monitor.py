"""
Database Query Monitoring Utility
Logs slow queries and provides performance insights for optimization
"""

import frappe
from frappe.utils import now, time_diff_in_seconds
import time
from contextlib import contextmanager


class QueryMonitor:
	"""Monitor database queries for performance analysis"""

	def __init__(self, threshold_ms=100):
		"""
		Initialize query monitor

		Args:
			threshold_ms: Log queries slower than this threshold (milliseconds)
		"""
		self.threshold_ms = threshold_ms
		self.slow_queries = []

	@contextmanager
	def monitor(self, query_name="Unknown Query"):
		"""Context manager to monitor a query's execution time

		Usage:
			monitor = QueryMonitor(threshold_ms=50)
			with monitor.monitor("Get all requests"):
				requests = frappe.get_all("Request", ...)
		"""
		start_time = time.time()

		try:
			yield
		finally:
			end_time = time.time()
			duration_ms = (end_time - start_time) * 1000

			if duration_ms > self.threshold_ms:
				self.slow_queries.append({
					"query": query_name,
					"duration_ms": round(duration_ms, 2),
					"timestamp": now()
				})

				frappe.logger().warning(
					f"Slow query detected: {query_name} took {duration_ms:.2f}ms "
					f"(threshold: {self.threshold_ms}ms)"
				)

	def get_slow_queries(self):
		"""Get list of slow queries detected"""
		return self.slow_queries

	def log_slow_queries(self):
		"""Log all slow queries to Error Log"""
		if not self.slow_queries:
			return

		frappe.log_error(
			title="Slow Queries Detected",
			message=f"Found {len(self.slow_queries)} slow queries:\n\n" +
					"\n".join([
						f"- {q['query']}: {q['duration_ms']}ms at {q['timestamp']}"
						for q in self.slow_queries
					])
		)


def log_query_stats(method_name, queries_before, queries_after):
	"""
	Log query statistics for an API method

	Args:
		method_name: Name of the API method
		queries_before: Query count before execution
		queries_after: Query count after execution
	"""
	query_count = queries_after - queries_before

	if query_count > 10:
		frappe.logger().warning(
			f"High query count in {method_name}: {query_count} queries executed"
		)


@frappe.whitelist()
def get_query_analytics(hours=24):
	"""
	Get query analytics from Error Log

	Args:
		hours: Number of hours to analyze

	Returns:
		dict: Query analytics
	"""
	from frappe.utils import add_to_date, now_datetime

	# Only allow System Managers to view query analytics
	if not frappe.has_permission("System Manager"):
		frappe.throw("Insufficient permissions")

	start_time = add_to_date(now_datetime(), hours=-hours)

	# Get slow query logs
	slow_query_logs = frappe.get_all(
		"Error Log",
		filters={
			"creation": [">=", start_time],
			"error": ["like", "%Slow query%"]
		},
		fields=["creation", "error", "method"],
		order_by="creation desc",
		limit=100
	)

	return {
		"total_slow_queries": len(slow_query_logs),
		"slow_queries": slow_query_logs,
		"time_range_hours": hours
	}


@contextmanager
def track_queries(operation_name):
	"""
	Context manager to track query count for an operation

	Usage:
		with track_queries("Load dashboard"):
			# ... code that executes queries
			pass
	"""
	# Get initial query count
	initial_count = frappe.db.sql("SELECT FOUND_ROWS()")[0][0] if frappe.db.sql_list else 0
	start_time = time.time()

	try:
		yield
	finally:
		# Get final query count (approximate)
		duration_ms = (time.time() - start_time) * 1000

		if duration_ms > 500:  # Log operations taking >500ms
			frappe.logger().info(
				f"Operation '{operation_name}' took {duration_ms:.2f}ms"
			)

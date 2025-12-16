"""
Rate Limiting Utility
Prevents abuse of API endpoints, especially guest-accessible ones
"""

import frappe
from functools import wraps


def rate_limit(calls=10, period=60):
	"""Rate limit decorator for API methods

	Args:
		calls: Number of calls allowed within the period
		period: Time period in seconds

	Example:
		@frappe.whitelist(allow_guest=True)
		@rate_limit(calls=5, period=60)  # 5 calls per minute
		def create_draft_request(data):
			pass
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			# Get client IP address
			ip_address = frappe.local.request_ip or "unknown"

			# Create cache key based on function name and IP
			cache_key = f"rate_limit:{func.__name__}:{ip_address}"

			# Get Redis cache
			cache = frappe.cache()

			# Get current call count
			calls_made = cache.get(cache_key)

			if calls_made is None:
				# First call - set counter
				cache.setex(cache_key, period, 1)
			elif int(calls_made) >= calls:
				# Rate limit exceeded
				frappe.throw(
					f"Rate limit exceeded. You can make {calls} requests per {period} seconds. "
					f"Please try again later.",
					frappe.RateLimitExceededError
				)
			else:
				# Increment counter
				cache.incr(cache_key)

			# Execute the actual function
			return func(*args, **kwargs)

		return wrapper
	return decorator


def get_rate_limit_status(func_name, ip_address=None):
	"""Get current rate limit status for debugging

	Args:
		func_name: Name of the function
		ip_address: IP address (defaults to current request IP)

	Returns:
		dict: {"calls_made": int, "limit": int, "ttl": int}
	"""
	if ip_address is None:
		ip_address = frappe.local.request_ip or "unknown"

	cache_key = f"rate_limit:{func_name}:{ip_address}"
	cache = frappe.cache()

	calls_made = cache.get(cache_key) or 0
	ttl = cache.ttl(cache_key)

	return {
		"calls_made": int(calls_made),
		"ttl_seconds": ttl if ttl > 0 else 0,
		"ip_address": ip_address
	}


def clear_rate_limit(func_name, ip_address=None):
	"""Clear rate limit for specific function/IP (admin only)

	Args:
		func_name: Name of the function
		ip_address: IP address (defaults to current request IP)
	"""
	if not frappe.has_permission("System Manager"):
		frappe.throw("Only System Managers can clear rate limits")

	if ip_address is None:
		ip_address = frappe.local.request_ip or "unknown"

	cache_key = f"rate_limit:{func_name}:{ip_address}"
	cache = frappe.cache()
	cache.delete(cache_key)

	frappe.msgprint(f"Rate limit cleared for {func_name} from {ip_address}")

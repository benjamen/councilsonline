"""
Frontend SPA handler - serves the Vue.js application for all /frontend/* routes
"""

import frappe

# This tells Frappe to serve frontend.html for all paths under /frontend/*
# The Vue Router will then handle the client-side routing
no_cache = 1

def get_context(context):
    """
    This function is called for all requests to /frontend and /frontend/*
    It returns the context that will be passed to frontend.html template
    """
    # Add any context variables needed by the frontend
    # The boot dict is automatically added by Frappe
    context.no_cache = 1

    # Add CSRF token to boot data so it's available as window.csrf_token
    csrf_token = frappe.sessions.get_csrf_token()
    context.boot = {
        'csrf_token': csrf_token,
        'user': frappe.session.user
    }

    return context

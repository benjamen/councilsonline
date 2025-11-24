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

    return context

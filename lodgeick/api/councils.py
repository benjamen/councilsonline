# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Council Configuration & Management API - Handles council settings, statistics, and request types
"""

import frappe
from frappe import _
from frappe.utils import cint, getdate


@frappe.whitelist()
def get_staff_users():
    """
    Get list of staff users with their roles for assignment

    Returns:
        list: List of users with their full name, email, and roles
    """
    try:
        users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User"
            },
            fields=["name", "email", "full_name"],
            order_by="full_name asc"
        )

        # Get roles for each user
        for user in users:
            user_roles = frappe.get_all(
                "Has Role",
                filters={"parent": user.name},
                fields=["role"],
                pluck="role"
            )
            user["roles"] = user_roles
            # Create a display name with primary role
            primary_role = user_roles[0] if user_roles else "User"
            user["display_name"] = f"{user.full_name or user.email} ({primary_role})"

        return users

    except Exception as e:
        frappe.log_error(f"Get Staff Users Error: {str(e)}")
        raise


@frappe.whitelist(allow_guest=True)
def get_council():
    """
    Get the single council for this site (Single DocType)

    Returns:
        dict: Council details including branding and configuration
    """
    council = frappe.get_single("Council")

    return {
        "council_code": council.council_code,
        "council_name": council.council_name,
        "official_name": council.official_name,
        # Branding
        "app_name": council.app_name,
        "tagline": council.tagline,
        "logo": council.logo,
        "favicon": council.favicon,
        "primary_color": council.primary_color,
        "secondary_color": council.secondary_color,
        "accent_color": council.accent_color,
        # Contact
        "website": council.website,
        "contact_email": council.contact_email,
        "contact_phone": council.contact_phone,
        # Portal settings
        "redirect_dashboard_to_council": council.redirect_dashboard_to_council,
        "allow_system_wide_dashboard": council.allow_system_wide_dashboard,
        "show_council_switcher": council.show_council_switcher,
        "custom_domain": council.custom_domain,
        "login_page_custom_html": council.login_page_custom_html,
    }


@frappe.whitelist(allow_guest=True)
def get_request_types():
    """
    Get enabled request types for this site's council

    Returns:
        list: List of enabled request types with council-specific pricing
    """
    council = frappe.get_single("Council")

    enabled_types = []

    for rt in council.enabled_request_types:
        if rt.is_enabled:
            request_type_doc = frappe.get_doc("Request Type", rt.request_type)

            enabled_types.append({
                "name": request_type_doc.name,
                "type_name": request_type_doc.type_name,
                "request_type_name": request_type_doc.type_name,  # Alias for frontend compatibility
                "type_code": request_type_doc.type_code,
                "category": request_type_doc.category,
                "description": rt.brief_description if rt.brief_description else (request_type_doc.description if hasattr(request_type_doc, 'description') else ""),
                "base_fee": rt.base_fee_override if rt.base_fee_override else request_type_doc.base_fee,
                "sla_days": rt.sla_days_override if rt.sla_days_override else request_type_doc.processing_sla_days,
                "fee_calculation_method": request_type_doc.fee_calculation_method,
                "process_description": rt.process_description or "",
                # Smart defaults based on category
                "requires_property": request_type_doc.requires_property if hasattr(request_type_doc, 'requires_property') else (request_type_doc.category != "Social Assistance"),
                "requires_payment": request_type_doc.requires_payment if hasattr(request_type_doc, 'requires_payment') else (request_type_doc.base_fee > 0)
            })

    return enabled_types


@frappe.whitelist()
def get_council_stats(council_code=None):
    """
    Get statistics for the council (single-tenant)

    Args:
        council_code: Deprecated, kept for backwards compatibility

    Returns:
        dict: Council statistics
    """
    # Single-tenant: Get the single Council instance
    council = frappe.get_single("Council")

    # Get monthly request count
    monthly_count = council.get_monthly_request_count()

    # Get total requests all time (single-tenant: no council filter)
    total_requests = frappe.db.count("Request")

    # Get requests by workflow_state (single-tenant)
    requests_by_status = frappe.db.sql("""
        SELECT workflow_state as status, COUNT(*) as count
        FROM `tabRequest`
        GROUP BY workflow_state
    """, as_dict=True)

    return {
        "council_name": council.council_name,
        "is_active": council.is_active,
        "is_license_valid": council.is_license_valid(),
        "monthly_request_count": monthly_count,
        "monthly_quota": council.max_requests_per_month,
        "total_requests": total_requests,
        "requests_by_status": requests_by_status,
        "enabled_request_types_count": len([rt for rt in council.enabled_request_types if rt.is_enabled])
    }


@frappe.whitelist(allow_guest=True)
def get_council_landing_page(council_code):
    """
    Get Council Landing Page configuration for a council.
    Returns default values if no landing page configured.

    Args:
        council_code: Council code

    Returns:
        dict: Landing page configuration
    """
    council_code = council_code.upper()

    # Verify council exists
    if not frappe.db.exists("Council", council_code):
        frappe.throw(_("Council not found: {0}").format(council_code))

    # Get landing page using SQL to avoid DocType cache issues
    landing_pages = frappe.db.sql("""
        SELECT *
        FROM `tabCouncil Landing Page`
        WHERE council = %s AND is_published = 1
        LIMIT 1
    """, (council_code,), as_dict=True)

    if landing_pages:
        return landing_pages[0]

    # Return defaults if no landing page configured
    council = frappe.get_doc("Council", council_code)
    return {
        "council": council_code,
        "is_published": 0,
        "hero_title": f"Welcome to {council.council_name}",
        "hero_subtitle": "Submit planning applications, building consents, and resource consent requests online",
        "primary_cta_text": "Start New Request",
        "primary_cta_link": "/frontend/request/new",
        "show_request_types": 1,
        "intro_html": None,
        "hero_image": None,
        "meta_title": None,
        "meta_description": None
    }


@frappe.whitelist()
def get_council_requests(council_code):
    """
    Get requests for current user filtered by council.
    Used by council-specific dashboard.

    Args:
        council_code: Council code to filter by

    Returns:
        list: Requests for this council
    """
    user = frappe.session.user

    requests = frappe.get_all(
        "Request",
        filters={
            "requester": user,
            "council": council_code
        },
        fields=[
            "name", "request_number", "request_type", "status",
            "property_address", "brief_description", "creation",
            "submitted_date", "statutory_clock_started",
            "working_days_elapsed", "council"
        ],
        order_by="modified desc"
    )

    # Enrich with council name
    for req in requests:
        if req.get("council"):
            council_name = frappe.db.get_value("Council", req["council"], "council_name")
            req["council_name"] = council_name

    return requests


@frappe.whitelist()
def should_redirect_to_council_dashboard(council_code):
    """
    Check if user should be redirected to council-specific dashboard.
    Used by route guard on /dashboard.

    Args:
        council_code: Council code to check settings for

    Returns:
        dict: Redirect settings for this council
    """
    try:
        council = frappe.get_doc("Council", council_code)
        return {
            "should_redirect": int(council.redirect_dashboard_to_council or 1),
            "allow_system_wide": int(council.allow_system_wide_dashboard or 0),
            "show_switcher": int(council.show_council_switcher or 0),
            "council_name": council.council_name,
            "primary_color": council.primary_color
        }
    except frappe.DoesNotExistError:
        return {
            "should_redirect": False,
            "allow_system_wide": True,
            "show_switcher": False
        }


@frappe.whitelist(allow_guest=True)
def get_council_settings(council_code):
    """
    Get council portal and website settings.
    Used for branding and configuration in council-specific pages.

    Args:
        council_code: Council code

    Returns:
        dict: Council settings
    """
    try:
        council = frappe.get_doc("Council", council_code)
        return {
            "council_code": council.council_code,
            "council_name": council.council_name,
            "official_name": council.official_name,
            "logo": council.logo,
            "primary_color": council.primary_color,
            "secondary_color": council.secondary_color,
            "redirect_dashboard_to_council": int(council.redirect_dashboard_to_council or 1),
            "allow_system_wide_dashboard": int(council.allow_system_wide_dashboard or 0),
            "show_council_switcher": int(council.show_council_switcher or 0),
            "custom_domain": council.custom_domain,
            "login_page_custom_html": council.login_page_custom_html,
            "contact_email": council.contact_email,
            "contact_phone": council.contact_phone,
            "website": council.website
        }
    except frappe.DoesNotExistError:
        frappe.throw(_("Council not found: {0}").format(council_code))


@frappe.whitelist(allow_guest=True)
def get_council_request_types(council_code):
    """
    Get enabled request types for a specific council with council-specific configuration

    Args:
        council_code: Council code (e.g., "HCC" for Hutt City Council)

    Returns:
        list: List of enabled request types with council-specific pricing, description, and process
    """
    try:
        council = frappe.get_doc("Council", council_code)

        if not council.is_active:
            return []

        result = []

        for council_rt in council.enabled_request_types:
            if not council_rt.is_enabled:
                continue

            # Get the base request type
            request_type = frappe.get_doc("Request Type", council_rt.request_type)

            # Build result with council overrides
            rt_data = {
                "name": request_type.name,
                "type_name": request_type.type_name,
                "category": getattr(request_type, 'category', None),
                "description": council_rt.brief_description or getattr(request_type, 'description', ''),
                "base_fee": council_rt.base_fee_override or getattr(request_type, 'base_fee', 0),
                "processing_sla_days": council_rt.sla_days_override or getattr(request_type, 'processing_sla_days', 20),
                "is_active": getattr(request_type, 'is_active', 1)
            }

            result.append(rt_data)

        return result

    except frappe.DoesNotExistError:
        frappe.throw(_("Council not found: {0}").format(council_code))
    except Exception as e:
        frappe.log_error(
            title="Error fetching council request types",
            message=str(e)
        )
        frappe.throw(_("Error fetching request types for council"))

# Copyright (c) 2025, CouncilsOnline and contributors
# For license information, please see license.txt

"""
Address Search & Validation API
Handles property address lookups for NZ, AU, and PH
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def search_property_address(query):
    """
    Search for property addresses using the LINZ property API

    Args:
        query: Address search string

    Returns:
        dict: Search results with property and hazard information
    """
    import requests

    if not query or len(query) < 3:
        return {"results": []}

    try:
        # Call the property API service
        # Note: The property API should be running on localhost:3000
        property_api_url = frappe.conf.get("property_api_url", "http://localhost:3000")

        response = requests.get(
            f"{property_api_url}/api/search",
            params={"q": query},
            timeout=10
        )

        if response.status_code != 200:
            frappe.log_error(
                title="Property API Error",
                message=f"Status: {response.status_code}, Response: {response.text}"
            )
            return {"results": []}

        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        frappe.log_error(
            title="Property API Connection Error",
            message=str(e)
        )
        return {"results": []}
    except Exception as e:
        frappe.log_error(
            title="Property Search Error",
            message=str(e)
        )
        return {"results": []}


@frappe.whitelist(allow_guest=True)
def search_property_addresses(query):
    """
    Alias for search_property_address to match AddressLookup component API call

    Args:
        query: Address search string

    Returns:
        list: Array of address results in standardized format
    """
    result = search_property_address(query)

    # If the result has a 'results' key, return it directly
    if isinstance(result, dict) and 'results' in result:
        return result['results']

    # Otherwise return the result as-is
    return result if isinstance(result, list) else []


@frappe.whitelist(allow_guest=True)
def search_addresses_universal(query, country):
    """
    Universal address lookup for multiple countries (NZ, AU, PH)

    Args:
        query: Address search string
        country: Country code (NZ, AU, PH)

    Returns:
        list: Array of address results in standardized format
    """
    import requests

    if not query or len(query) < 3:
        return []

    if not country:
        frappe.throw(_("Country code is required"))

    try:
        if country == "NZ":
            # Use existing NZ property API
            result = search_property_address(query)
            if isinstance(result, dict) and 'results' in result:
                return result['results']
            return result if isinstance(result, list) else []

        elif country == "AU":
            # Australia address lookup using GNAF or similar service
            # For now, return stub data for development
            return search_australia_addresses(query)

        elif country == "PH":
            # Philippines address lookup
            # For now, return stub data for development
            return search_philippines_addresses(query)

        else:
            frappe.throw(_("Unsupported country code: {0}").format(country))

    except Exception as e:
        frappe.log_error(
            title=f"Universal Address Search Error ({country})",
            message=str(e)
        )
        return []


def search_australia_addresses(query):
    """
    Search for addresses in Australia

    TODO: Integrate with GNAF (Geocoded National Address File) or commercial API
    For now, returns stub data for development

    Args:
        query: Address search string

    Returns:
        list: Array of address results
    """
    # Stub implementation - replace with actual API integration
    # Options for AU:
    # 1. data.gov.au GNAF dataset
    # 2. Google Places API
    # 3. Mapbox Geocoding API
    # 4. Australia Post Address API

    return []


def search_philippines_addresses(query):
    """
    Search for addresses in Philippines

    TODO: Integrate with Philippines address API
    For now, returns stub data for development

    Args:
        query: Address search string

    Returns:
        list: Array of address results
    """
    # Stub implementation - replace with actual API integration
    # Options for PH:
    # 1. Google Places API
    # 2. Nominatim (OpenStreetMap)
    # 3. OneMap Philippines (if available)
    # 4. PhilGIS data

    return []

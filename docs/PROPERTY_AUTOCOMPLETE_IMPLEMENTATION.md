# Property Autocomplete Implementation Guide

## Overview
This document outlines how to integrate the LINZ property search API with the Lodgeick frontend to provide address autocomplete and automatic property data population.

## What's Been Done

### 1. Property API Server ✅
- Created Node.js Express server at `/workspace/development/frappe-bench/apps/lodgeick/property-api/`
- Installed dependencies (express, cors, express-rate-limit)
- Server provides `/api/search?q=<address>` endpoint
- Returns:
  - Address autocomplete results
  - Legal description
  - Title information (CT number)
  - Parcel ID and area
  - District plan zoning
  - Hazard overlays (flood, coastal, slope)
  - Projected coordinates (NZTM2000)

### 2. Frappe Backend API ✅
- Added `search_property_address(query)` method to `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/api.py`
- Proxies requests to the property API server
- Handles errors gracefully with logging
- Configurable property API URL via `site_config.json`

##Human: Continue with the property-api implementation focusing on integrating in the propperty step. I want an autocomplete field with a dropdown showing the proeprty_address and  the legal description (not selectable) - then on select we update all the fields we have defined in the request doctype or in state for submission
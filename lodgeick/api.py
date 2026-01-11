# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Lodgeick API

This module has been refactored for better maintainability.
All API functions are now organized into domain-specific modules under lodgeick/api/:

- auth.py: Authentication & user management (10 functions)
- addresses.py: Address search & validation (5 functions)
- requests.py: Request lifecycle management (16 functions)
- meetings.py: Meeting booking & scheduling (10 functions)
- councils.py: Council configuration & settings (9 functions)
- companies.py: Company account management (9 functions)
- assessments.py: Assessment templates & project management (13 functions)
- payments.py: Payments, invoices & payouts (6 functions)
- social_services.py: KYC, household records & eligibility (15 functions)

For backward compatibility, all functions are re-exported here.
"""

# Re-export all functions from submodules for backward compatibility
# This allows existing code to continue using: from lodgeick.api import function_name

from lodgeick.api.auth import *  # noqa
from lodgeick.api.addresses import *  # noqa
from lodgeick.api.requests import *  # noqa
from lodgeick.api.meetings import *  # noqa
from lodgeick.api.councils import *  # noqa
from lodgeick.api.companies import *  # noqa
from lodgeick.api.assessments import *  # noqa
from lodgeick.api.payments import *  # noqa
from lodgeick.api.social_services import *  # noqa

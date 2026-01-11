# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Authentication & User Management API - Handles user registration, profile management, and login tracking
"""

import frappe
from frappe import _
import re
from frappe.utils import check_password, update_password
from lodgeick.utils.rate_limit import rate_limit


def validate_nz_phone_number(phone):
    """
    Validate New Zealand phone number format
    Accepts: mobile (02x), landline (03-09), with or without spaces/hyphens
    """
    if not phone:
        return False, "Phone number is required"

    # Remove spaces, hyphens, parentheses
    cleaned = re.sub(r'[\s\-()]', '', phone)

    # Remove international prefix if present
    if cleaned.startswith('+64'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('0064'):
        cleaned = '0' + cleaned[4:]

    # Check if only digits
    if not cleaned.isdigit():
        return False, "Phone number should contain only numbers"

    # Mobile validation (021, 022, 027, 028, 029)
    if re.match(r'^0(2[1278]|29)[0-9]{6,8}$', cleaned):
        return True, ""

    # Landline validation (03-09)
    if re.match(r'^0[3-9][0-9]{7,8}$', cleaned):
        return True, ""

    # Invalid format
    if len(cleaned) < 9:
        return False, "Phone number is too short. NZ phone numbers are 9-10 digits."
    if len(cleaned) > 11:
        return False, "Phone number is too long. NZ phone numbers are 9-10 digits."

    return False, "Invalid NZ phone number. Mobile numbers start with 02, landlines with 03-09."


@frappe.whitelist(allow_guest=True)
@rate_limit(calls=3, period=300)  # 3 registrations per 5 minutes to prevent spam accounts
def register_user(
    email,
    first_name,
    last_name,
    phone,
    password,
    user_role="requester",
    applicant_type="Individual",
    property_address=None,
    property_street=None,
    property_suburb=None,
    property_city=None,
    property_postcode=None,
    property_id=None,
    address_id=None,
    organization_name=None,
    company_number=None,
    trust_name=None
):
    """
    Register a new REQUESTER for Lodgeick (requesters can submit on behalf of themselves or organizations)

    Args:
        email: User's email address
        first_name: First name
        last_name: Last name
        phone: Phone number (NZ format required)
        password: Password
        user_role: User role type - 'requester' (submits requests) or 'agent' (consultant)
        applicant_type: Individual, Company, Trust, or Organisation (entity type)
        property_address: Full property address
        property_street: Street address
        property_suburb: Suburb/locality
        property_city: City
        property_postcode: Postcode
        property_id: Property ID from database
        address_id: Address ID from LINZ
        organization_name: Company or Organisation name
        company_number: Company registration number
        trust_name: Trust name

    Returns:
        dict: Success message and user info
    """

    # Validate required fields
    if not email or not first_name or not last_name or not password or not phone:
        frappe.throw(_("Email, first name, last name, phone, and password are required"))

    # Validate phone number
    phone_valid, phone_error = validate_nz_phone_number(phone)
    if not phone_valid:
        frappe.throw(_(phone_error))

    # Check if user already exists
    if frappe.db.exists("User", email):
        frappe.throw(_("User with this email already exists"))

    try:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "enabled": 1,
            "send_welcome_email": 1,
            "new_password": password,
            "user_type": "Website User"
        })

        # Add Applicant role (Frappe role name remains "Applicant" for database consistency)
        user.append("roles", {"role": "Applicant"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

        # Create User Profile Extended
        try:
            profile = frappe.get_doc({
                "doctype": "User Profile Extended",
                "user": email,
                "full_name": f"{first_name} {last_name}",
                "phone": phone,
                "user_role": "Individual",  # For requesters, user_role is Individual (not Agent)
            })

            # Add address for Individual requesters
            if applicant_type == "Individual" and property_address:
                profile.postal_street = property_street or property_address
                profile.postal_suburb = property_suburb
                profile.postal_city = property_city
                profile.postal_postcode = property_postcode

            # Add property to properties child table if provided
            if property_address and (property_street or property_address):
                profile.append("properties", {
                    "street": property_street or property_address,
                    "suburb": property_suburb,
                    "city": property_city,
                    "postcode": property_postcode,
                    "ownership_status": "Sole Owner",  # Default for individual registration
                    "is_default": 1  # Mark as default property
                })

            profile.flags.ignore_permissions = True
            profile.insert()
        except Exception as e:
            frappe.log_error(f"Error creating user profile: {str(e)}")

        # Create organization record for Company/Organisation/Trust requesters
        if applicant_type in ["Company", "Organisation", "Trust"]:
            org_name = organization_name or trust_name
            if org_name:
                try:
                    org = frappe.get_doc({
                        "doctype": "Organization",
                        "organization_name": org_name,
                        "organization_type": applicant_type,
                        "contact_email": email,
                        "contact_phone": phone,
                        "company_number": company_number if applicant_type == "Company" else None
                    })
                    org.flags.ignore_permissions = True
                    org.insert()

                    # Link user to organization
                    user.organization = org.name
                    user.save(ignore_permissions=True)
                except Exception as e:
                    frappe.log_error(f"Error creating organization: {str(e)}")

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Account created successfully. Please check your email to verify your account."),
            "user": email
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"User Registration Error: {str(e)}")
        frappe.throw(_("Registration failed. Please try again or contact support."))


@frappe.whitelist(allow_guest=True)
def register_agent(
    email,
    first_name,
    last_name,
    phone,
    password,
    user_role="agent",
    agent_type="Sole Trader",
    company_name=None,
    company_number=None,
    nzbn=None,
    trading_name=None,
    business_address=None,
    business_street=None,
    business_suburb=None,
    business_city=None,
    business_postcode=None
):
    """
    Register a new AGENT (Planning Consultant) for Lodgeick

    Args:
        email: User's email address
        first_name: First name
        last_name: Last name
        phone: Phone number (NZ format required)
        password: Password
        user_role: Always 'agent' for this endpoint
        agent_type: 'Sole Trader' or 'Company'
        company_name: Company name (if agent_type is Company)
        company_number: Company registration number
        nzbn: New Zealand Business Number (13 digits)
        trading_name: Trading name (if Sole Trader)
        business_address: Business address
        business_street: Business street
        business_suburb: Business suburb
        business_city: Business city
        business_postcode: Business postcode

    Returns:
        dict: Success message and user info
    """

    # Validate required fields
    if not email or not first_name or not last_name or not password or not phone:
        frappe.throw(_("Email, first name, last name, phone, and password are required"))

    # Validate phone number
    phone_valid, phone_error = validate_nz_phone_number(phone)
    if not phone_valid:
        frappe.throw(_(phone_error))

    # Validate NZBN if provided
    if nzbn:
        cleaned_nzbn = re.sub(r'[\s\-]', '', nzbn)
        if not re.match(r'^\d{13}$', cleaned_nzbn):
            frappe.throw(_("NZBN must be exactly 13 digits"))

    # Check if user already exists
    if frappe.db.exists("User", email):
        frappe.throw(_("User with this email already exists"))

    try:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "enabled": 1,
            "send_welcome_email": 1,
            "new_password": password,
            "user_type": "Website User"
        })

        # Add Agent role (Agents can also submit requests, so add Applicant role too for permissions)
        user.append("roles", {"role": "Agent"})
        user.append("roles", {"role": "Applicant"})

        # Save user
        user.flags.ignore_permissions = True
        user.insert()

        # Create User Profile Extended with Agent role
        try:
            profile = frappe.get_doc({
                "doctype": "User Profile Extended",
                "user": email,
                "full_name": f"{first_name} {last_name}",
                "phone": phone,
                "user_role": "Agent",  # This is an Agent profile
            })

            # Add business details
            if agent_type == "Company" and company_name:
                profile.company_name = company_name
                profile.company_number = company_number
                profile.business_type = "Limited Company"
            else:
                profile.business_type = "Sole Trader"

            # Add business address
            if business_address:
                profile.business_street = business_street or business_address
                profile.business_suburb = business_suburb
                profile.business_city = business_city
                profile.business_postcode = business_postcode

            profile.flags.ignore_permissions = True
            profile.insert()
        except Exception as e:
            frappe.log_error(f"Error creating agent profile: {str(e)}")

        # Create organization record for Company agents
        if agent_type == "Company" and company_name:
            try:
                org = frappe.get_doc({
                    "doctype": "Organization",
                    "organization_name": company_name,
                    "organization_type": "Agent",
                    "contact_email": email,
                    "contact_phone": phone,
                    "company_number": company_number
                })
                org.flags.ignore_permissions = True
                org.insert()

                # Link user to organization
                user.organization = org.name
                user.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Error creating agent organization: {str(e)}")

        frappe.db.commit()

        return {
            "success": True,
            "message": _("Agent account created successfully. Please check your email to verify your account."),
            "user": email
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Agent Registration Error: {str(e)}")
        frappe.throw(_("Registration failed. Please try again or contact support."))


# ============================================================================
# ANALYTICS - LOGIN SOURCE TRACKING
# ============================================================================

@frappe.whitelist()
def track_login_event(source):
    """
    Track login events for analytics (single-tenant)

    Args:
        source: Login source (e.g., 'web', 'mobile', 'api')
    """
    try:
        # Create login tracking record
        login_event = frappe.get_doc({
            "doctype": "Login Event",
            "user": frappe.session.user,
            "source": source,
            "timestamp": frappe.utils.now(),
            "ip_address": frappe.local.request_ip,
            "user_agent": frappe.local.request.headers.get("User-Agent")
        })
        login_event.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True}
    except Exception as e:
        frappe.log_error(f"Failed to track login event: {str(e)}")
        # Don't fail the login if tracking fails
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_login_analytics(council_code=None, from_date=None, to_date=None):
    """
    Get login analytics data

    Args:
        council_code: Optional council filter
        from_date: Start date for analytics
        to_date: End date for analytics

    Returns:
        dict: Analytics data including counts and breakdowns
    """
    filters = {}

    if council_code:
        filters["council"] = council_code

    if from_date:
        filters["timestamp"] = [">=", from_date]

    if to_date:
        if "timestamp" in filters:
            filters["timestamp"] = [[">=", from_date], ["<=", to_date]]
        else:
            filters["timestamp"] = ["<=", to_date]

    # Get login events
    events = frappe.get_all(
        "Login Event",
        filters=filters,
        fields=["source", "council", "timestamp", "user"],
        order_by="timestamp desc"
    )

    # Calculate analytics
    total_logins = len(events)
    system_wide_logins = len([e for e in events if e.source == "system-wide"])
    council_logins = len([e for e in events if e.source == "council-specific"])

    # Council breakdown
    council_breakdown = {}
    for event in events:
        if event.council:
            council_breakdown[event.council] = council_breakdown.get(event.council, 0) + 1

    # Unique users
    unique_users = len(set(e["user"] for e in events))

    return {
        "total_logins": total_logins,
        "system_wide_logins": system_wide_logins,
        "council_specific_logins": council_logins,
        "council_breakdown": council_breakdown,
        "unique_users": unique_users,
        "events": events[:100]  # Return last 100 events
    }


# ============================================================================
# USER PROFILE & SETTINGS API ENDPOINTS
# ============================================================================

@frappe.whitelist(allow_guest=True)
def get_user_profile(user=None):
    """
    Get user profile information including custom fields and organization data

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: User profile data
    """
    if not user:
        user = frappe.session.user

    # Get user document with custom fields
    user_doc = frappe.get_doc("User", user)

    # Get organization data if user has organization link
    organization_data = None
    if user_doc.get("organization"):
        org = frappe.get_doc("Organization", user_doc.organization)
        organization_data = {
            "name": org.name,
            "organization_name": org.organization_name,
            "organization_type": org.organization_type,
            "registration_number": org.registration_number,
            "contact_email": org.contact_email,
            "contact_phone": org.contact_phone,
            "address": org.address,
            "city": org.city,
            "postal_code": org.postal_code
        }

    # Get default council data if set
    default_council_data = None
    if user_doc.get("default_council"):
        council = frappe.get_doc("Council", user_doc.default_council)
        default_council_data = {
            "council_code": council.council_code,
            "council_name": council.council_name,
            "primary_color": council.primary_color
        }

    return {
        "email": user_doc.email,
        "first_name": user_doc.first_name,
        "last_name": user_doc.last_name,
        "full_name": user_doc.full_name,
        "user_image": user_doc.user_image,
        "mobile_no": user_doc.mobile_no,
        "phone": user_doc.phone,
        "bio": user_doc.bio,
        "location": user_doc.location,
        "account_type": user_doc.get("account_type") or "Applicant",
        "requester_type": user_doc.get("requester_type") or "Individual",
        "default_council": user_doc.get("default_council"),
        "default_council_data": default_council_data,
        "organization": user_doc.get("organization"),
        "organization_data": organization_data,
        "enabled": user_doc.enabled,
        "user_type": user_doc.user_type,
        "creation": user_doc.creation,
        "modified": user_doc.modified
    }


@frappe.whitelist()
def update_user_profile(first_name=None, last_name=None, mobile_no=None, phone=None,
                       bio=None, location=None, default_council=None, user_image=None):
    """
    Update user profile information

    Args:
        first_name: User's first name
        last_name: User's last name
        mobile_no: Mobile phone number
        phone: Phone number
        bio: User biography
        location: User location
        default_council: Default council code
        user_image: User profile image URL

    Returns:
        dict: Success status and updated user data
    """
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    # Update fields if provided
    if first_name is not None:
        user_doc.first_name = first_name
    if last_name is not None:
        user_doc.last_name = last_name
    if mobile_no is not None:
        user_doc.mobile_no = mobile_no
    if phone is not None:
        user_doc.phone = phone
    if bio is not None:
        user_doc.bio = bio
    if location is not None:
        user_doc.location = location
    if user_image is not None:
        user_doc.user_image = user_image

    # Update default council if provided
    if default_council is not None:
        # Validate council exists and is active
        if default_council:
            council = frappe.get_doc("Council", default_council)
            if not council.is_active:
                frappe.throw("Selected council is not active")
        user_doc.default_council = default_council

    user_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": get_user_profile(user)
    }


@frappe.whitelist()
def change_password(old_password, new_password):
    """
    Change user password

    Args:
        old_password: Current password
        new_password: New password

    Returns:
        dict: Success status
    """
    from frappe.utils.password import check_password, update_password

    user = frappe.session.user

    # Verify old password
    try:
        check_password(user, old_password)
    except Exception:
        frappe.throw("Current password is incorrect")

    # Update to new password
    update_password(user, new_password)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@frappe.whitelist()
def get_user_organization(user=None):
    """
    Get organization details for the user

    Args:
        user: User email (optional, defaults to current user)

    Returns:
        dict: Organization data or None
    """
    if not user:
        user = frappe.session.user

    user_doc = frappe.get_doc("User", user)

    if not user_doc.get("organization"):
        return None

    org = frappe.get_doc("Organization", user_doc.organization)

    return {
        "name": org.name,
        "organization_name": org.organization_name,
        "organization_type": org.organization_type,
        "registration_number": org.registration_number,
        "contact_email": org.contact_email,
        "contact_phone": org.contact_phone,
        "address": org.address,
        "city": org.city,
        "postal_code": org.postal_code,
        "website": org.website,
        "description": org.description,
        "is_verified": org.is_verified,
        "creation": org.creation,
        "modified": org.modified
    }


@frappe.whitelist()
def update_user_organization(organization_name=None, contact_email=None, contact_phone=None,
                            address=None, city=None, postal_code=None, website=None, description=None):
    """
    Update organization details for the user

    Args:
        organization_name: Organization name
        contact_email: Contact email
        contact_phone: Contact phone
        address: Street address
        city: City
        postal_code: Postal code
        website: Website URL
        description: Organization description

    Returns:
        dict: Success status and updated organization data
    """
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    if not user_doc.get("organization"):
        frappe.throw("No organization linked to this user")

    org = frappe.get_doc("Organization", user_doc.organization)

    # Update fields if provided
    if organization_name is not None:
        org.organization_name = organization_name
    if contact_email is not None:
        org.contact_email = contact_email
    if contact_phone is not None:
        org.contact_phone = contact_phone
    if address is not None:
        org.address = address
    if city is not None:
        org.city = city
    if postal_code is not None:
        org.postal_code = postal_code
    if website is not None:
        org.website = website
    if description is not None:
        org.description = description

    org.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": "Organization updated successfully",
        "organization": get_user_organization(user)
    }

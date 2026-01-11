# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

"""
Lodgeick API Module
Re-exports all API functions from submodules for backward compatibility
"""

# Authentication & User Management
from lodgeick.api.auth import (
	validate_nz_phone_number,
	register_user,
	register_agent,
	track_login_event,
	get_login_analytics,
	get_user_profile,
	update_user_profile,
	change_password,
	get_user_organization,
	update_user_organization
)

# Address Search
from lodgeick.api.addresses import (
	search_property_address,
	search_property_addresses,
	search_addresses_universal,
	search_australia_addresses,
	search_philippines_addresses
)

# Request Management
from lodgeick.api.requests import (
	create_rc_application,
	create_spisc_application,
	update_spisc_application,
	create_draft_request,
	update_draft_request,
	load_draft_request,
	submit_request,
	assign_request,
	get_request_form_meta,
	get_request_type_config,
	send_request_message,
	get_request_communications,
	get_user_requests,
	get_request_summary_data,
	send_request_notification,
	add_internal_note
)

# Meeting Management
from lodgeick.api.meetings import (
	book_council_meeting,
	get_meeting_details,
	get_request_meetings,
	schedule_meeting,
	reschedule_meeting,
	cancel_meeting,
	complete_meeting,
	get_user_meetings,
	get_meeting_config,
	get_available_meeting_slots
)

# Council Configuration
from lodgeick.api.councils import (
	get_staff_users,
	get_council,
	get_request_types,
	get_council_stats,
	get_council_landing_page,
	get_council_requests,
	should_redirect_to_council_dashboard,
	get_council_settings,
	get_council_request_types
)

# Company Management
from lodgeick.api.companies import (
	register_company_account,
	get_user_company_account,
	update_company_account,
	send_company_invitation,
	send_invitation_email,
	accept_company_invitation,
	remove_user_from_company,
	update_user_company_role,
	get_company_users
)

# Assessment & Project Management
from lodgeick.api.assessments import (
	get_request_type_steps,
	apply_council_step_overrides,
	validate_step_data,
	get_step_templates,
	load_step_template,
	save_request_type_config,
	load_request_type_config,
	get_assessment_templates,
	load_assessment_template,
	save_assessment_template,
	get_assessment_stage_types,
	get_spisc_summary_data,
	create_assessment_project_for_request
)

# Payment & Invoices
from lodgeick.api.payments import (
	request_invoice,
	create_payout,
	create_payout_batch,
	generate_bank_file,
	approve_payout_batch,
	add_to_masterlist
)

# Social Services
from lodgeick.api.social_services import (
	submit_kyc_verification,
	verify_kyc,
	check_kyc_status,
	notify_kyc_submission,
	create_household_record,
	update_household_member,
	verify_household_by_barangay,
	get_household_record,
	calculate_eligibility,
	override_eligibility,
	get_eligibility_result,
	run_fraud_check,
	check_duplicate_application,
	check_beneficiary_status,
	detect_identity_fraud
)

__all__ = [
	# Auth
	'validate_nz_phone_number', 'register_user', 'register_agent',
	'track_login_event', 'get_login_analytics', 'get_user_profile',
	'update_user_profile', 'change_password', 'get_user_organization',
	'update_user_organization',
	# Addresses
	'search_property_address', 'search_property_addresses', 'search_addresses_universal',
	'search_australia_addresses', 'search_philippines_addresses',
	# Requests
	'create_rc_application', 'create_spisc_application', 'update_spisc_application',
	'create_draft_request', 'update_draft_request', 'load_draft_request',
	'submit_request', 'assign_request', 'get_request_form_meta',
	'get_request_type_config', 'send_request_message', 'get_request_communications',
	'get_user_requests', 'get_request_summary_data', 'send_request_notification',
	'add_internal_note',
	# Meetings
	'book_council_meeting', 'get_meeting_details', 'get_request_meetings',
	'schedule_meeting', 'reschedule_meeting', 'cancel_meeting',
	'complete_meeting', 'get_user_meetings', 'get_meeting_config',
	'get_available_meeting_slots',
	# Councils
	'get_staff_users', 'get_council', 'get_request_types', 'get_council_stats',
	'get_council_landing_page', 'get_council_requests', 'should_redirect_to_council_dashboard',
	'get_council_settings', 'get_council_request_types',
	# Companies
	'register_company_account', 'get_user_company_account', 'update_company_account',
	'send_company_invitation', 'send_invitation_email', 'accept_company_invitation',
	'remove_user_from_company', 'update_user_company_role', 'get_company_users',
	# Assessments
	'get_request_type_steps', 'apply_council_step_overrides', 'validate_step_data',
	'get_step_templates', 'load_step_template', 'save_request_type_config',
	'load_request_type_config', 'get_assessment_templates', 'load_assessment_template',
	'save_assessment_template', 'get_assessment_stage_types', 'get_spisc_summary_data',
	'create_assessment_project_for_request',
	# Payments
	'request_invoice', 'create_payout', 'create_payout_batch',
	'generate_bank_file', 'approve_payout_batch', 'add_to_masterlist',
	# Social Services
	'submit_kyc_verification', 'verify_kyc', 'check_kyc_status',
	'notify_kyc_submission', 'create_household_record', 'update_household_member',
	'verify_household_by_barangay', 'get_household_record', 'calculate_eligibility',
	'override_eligibility', 'get_eligibility_result', 'run_fraud_check',
	'check_duplicate_application', 'check_beneficiary_status', 'detect_identity_fraud'
]

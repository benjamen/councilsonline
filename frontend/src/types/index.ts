/**
 * TypeScript Type Definitions for Lodgeick
 * Covers Request Types, Applications, and API responses
 */

// ============================================================================
// Request Type Configuration
// ============================================================================

export interface RequestTypeConfig {
	name: string
	request_type_name: string
	request_type_code: string
	category: string
	description?: string
	icon?: string
	is_enabled: number
	steps: StepConfig[]
}

export interface StepConfig {
	step_number: number
	step_code: string
	step_title: string
	step_component: string
	is_enabled: number
	is_required: number
	show_on_review: number
	depends_on?: string
	sections: SectionConfig[]
}

export interface SectionConfig {
	section_code: string
	section_title: string
	section_type: string
	sequence: number
	is_enabled: number
	is_required: number
	show_on_review: number
	depends_on?: string
	fields: FieldConfig[]
}

export interface FieldConfig {
	field_name: string
	field_label: string
	field_type: FieldType
	is_required: number
	is_enabled: number
	show_on_review: number
	validation?: string
	depends_on?: string
	options?: string
	default_value?: any
	help_text?: string
	description?: string
	placeholder?: string
}

export type FieldType =
	| 'Data'
	| 'Select'
	| 'Text'
	| 'Date'
	| 'Currency'
	| 'Check'
	| 'Int'
	| 'Float'
	| 'Attach'
	| 'Link'

// ============================================================================
// Request Document
// ============================================================================

export interface Request {
	name: string
	request_number: string
	request_type: string
	request_category?: string
	status: RequestStatus
	applicant: string
	applicant_name?: string
	council?: string
	property_address?: string
	brief_description?: string
	form_data: Record<string, any>
	current_step: number
	submitted_date?: string
	acknowledged_date?: string
	target_completion_date?: string
	actual_completion_date?: string
	creation: string
	modified: string
	owner: string
	assigned_to?: string
	priority?: string
	is_overdue?: number
	working_days_elapsed?: number
	statutory_clock_started?: number
}

export type RequestStatus =
	| 'Draft'
	| 'Submitted'
	| 'Acknowledged'
	| 'Under Review'
	| 'RFI Issued'
	| 'Approved'
	| 'Approved with Conditions'
	| 'Declined'
	| 'Withdrawn'
	| 'Cancelled'
	| 'Completed'

// ============================================================================
// Application Documents
// ============================================================================

export interface SPISCApplication {
	name: string
	request: string
	applicant_name: string
	age?: number
	gender?: string
	civil_status?: string
	barangay?: string
	municipality?: string
	province?: string
	monthly_income?: number
	household_size?: number
	status?: string
	creation: string
}

export interface ResourceConsentApplication {
	name: string
	request: string
	activity_status?: string
	consent_types?: ConsentType[]
	property_details?: string
	status?: string
	creation: string
}

export interface ConsentType {
	consent_type: string
}

export interface BuildingConsentApplication {
	name: string
	request: string
	building_work_type?: string
	property_details?: string
	status?: string
	creation: string
}

// ============================================================================
// Council
// ============================================================================

export interface Council {
	name: string
	council_name: string
	council_code: string
	region?: string
	logo?: string
	primary_color?: string
	is_enabled: number
}

// ============================================================================
// User
// ============================================================================

export interface User {
	name: string
	email: string
	full_name?: string
	user_type?: string
	user_image?: string
	roles?: string[]
}

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T = any> {
	message: T
	exc?: string
	exc_type?: string
	exception?: string
	_server_messages?: string
}

export interface ResourceResponse<T = any> {
	data: T
	loading: boolean
	error: any
	reload: () => void
	fetch?: () => Promise<void>
}

export interface ListResponse<T> {
	data: T[]
	total_count?: number
}

// ============================================================================
// Form Data Types
// ============================================================================

export interface FormData {
	[key: string]: any
}

export interface ValidationResult {
	valid: boolean
	errors: Record<string, string>
}

// ============================================================================
// RFQ Types
// ============================================================================

export interface RFQAgentDetails {
	name: string
	request: string
	status: string
	agent?: string
	agent_name?: string
	agent_email?: string
	agent_phone?: string
	agent_engaged?: number
	agent_engaged_date?: string
	quote_amount?: number
	quote_details?: string
	quote_received_date?: string
	rfq_message?: string
	created_date: string
}

// ============================================================================
// Assessment Types
// ============================================================================

export interface AssessmentProject {
	name: string
	request: string
	assessment_template: string
	project_owner: string
	statutory_clock_days: number
	overall_status: string
	stages?: AssessmentStage[]
}

export interface AssessmentStage {
	stage_name: string
	sequence: number
	status: string
	tasks?: AssessmentTask[]
}

export interface AssessmentTask {
	task_title: string
	assigned_to?: string
	status: string
	due_date?: string
}

// ============================================================================
// UI State Types
// ============================================================================

export interface ToastNotification {
	id: number
	message: string
	type: 'info' | 'success' | 'warning' | 'error'
	duration: number
	timestamp: Date
}

export interface ErrorState {
	id: number
	message: string
	timestamp: Date
	type: string
	context?: any
}

// ============================================================================
// Store Types
// ============================================================================

export interface RequestStoreState {
	currentRequestId: string | null
	requestTypeCode: string | null
	requestTypeConfig: RequestTypeConfig | null
	formData: FormData
	currentStep: number
	stepValidationStatus: Record<number, boolean>
	isSaving: boolean
	isSubmitting: boolean
	lastSaved: Date | null
	error: string | null
}

export interface CouncilStoreState {
	councils: Council[]
	selectedCouncil: string | null
	lockedCouncil: string | null
	requestTypes: RequestTypeConfig[]
	loading: boolean
	error: string | null
}

export interface ErrorStoreState {
	errors: ErrorState[]
	globalError: any
}

export interface UIStoreState {
	modals: Record<string, boolean>
	loadingStates: Record<string, boolean>
	toasts: ToastNotification[]
	sidebarOpen: boolean
	mobileMenuOpen: boolean
}

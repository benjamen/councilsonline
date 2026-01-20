<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <RequestHeader
      :title="request.data?.request_number || 'Loading...'"
      :subtitle="request.data?.request_type"
      :loading="request.loading"
      @back="goBack"
    >
      <template #actions>
        <StatusBadge v-if="request.data" :status="request.data.workflow_state" />
        <Button
          v-if="request.data?.workflow_state === 'Draft'"
          @click="handleSubmitApplication"
          variant="solid"
          theme="blue"
          :loading="submitting"
        >
          Submit Application
        </Button>
      </template>
    </RequestHeader>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      class="hidden"
      @change="handleFileUpload"
    />

    <!-- Loading State -->
    <div v-if="request.loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-500">Loading request details...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="request.data" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content Column -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview Card -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Application Overview</h2>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-500">Request Number</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.request_number }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Type</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.request_type }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Status</label>
                <div class="mt-1">
                  <StatusBadge :status="request.data.workflow_state" />
                </div>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Submitted Date</label>
                <p class="mt-1 text-sm text-gray-900">{{ formatDate(request.data.creation) }}</p>
              </div>
            </div>

            <div class="mt-6 pt-6 border-t border-gray-200">
              <label class="text-sm font-medium text-gray-500">Brief Description</label>
              <p class="mt-1 text-sm text-gray-900">{{ request.data.brief_description || 'N/A' }}</p>
            </div>

            <div class="mt-4">
              <label class="text-sm font-medium text-gray-500">Detailed Description</label>
              <div class="mt-1 text-sm text-gray-900 prose prose-sm max-w-none" v-html="request.data.detailed_description || 'N/A'"></div>
            </div>
          </div>

          <!-- Property Information - only show if request type has property -->
          <div v-if="hasPropertyDetails" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Property Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div v-if="enrichedRequest.property_address">
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.property_address }}</p>
              </div>
              <div v-if="enrichedRequest.legal_description">
                <label class="text-sm font-medium text-gray-500">Legal Description</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.legal_description }}</p>
              </div>
            </div>
          </div>

          <!-- Applicant Information -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Applicant Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-500">Name</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.full_name || enrichedRequest.requester_name || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Email</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.requester_email || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Phone</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.mobile_number || enrichedRequest.requester_phone || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ formatAddress(enrichedRequest.address_line) || enrichedRequest.applicant_address || 'N/A' }}</p>
              </div>
              <div v-if="enrichedRequest.applicant_company">
                <label class="text-sm font-medium text-gray-500">Company/Organization</label>
                <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.applicant_company }}</p>
              </div>
            </div>
          </div>

          <!-- SPISC Application Details - only show if request is SPISC -->
          <div v-if="request.data?.request_type?.includes('SPISC')" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">SPISC Application Details</h2>

            <div class="space-y-6">
              <!-- Personal Information -->
              <div>
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Personal Information</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Birth Date</label>
                    <p class="mt-1 text-sm text-gray-900">{{ formatDate(enrichedRequest.birth_date) || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Age</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.age || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Sex</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.sex || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Civil Status</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.civil_status || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Household & Economic Information -->
              <div>
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Household & Economic Information</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Household Size</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.household_size || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Living Arrangement</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.living_arrangement || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Monthly Income</label>
                    <p class="mt-1 text-sm text-gray-900">₱{{ enrichedRequest.monthly_income || '0' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Income Source</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.income_source || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">4Ps Beneficiary</label>
                    <p class="mt-1 text-sm text-gray-900">{{ enrichedRequest.is_4ps_beneficiary ? 'Yes' : 'No' }}</p>
                  </div>
                </div>
              </div>

              <!-- Identity Documents -->
              <div>
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Identity Documents</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div v-if="request.data.philsys_id">
                    <label class="text-sm font-medium text-gray-500">PhilSys ID</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.philsys_id }}</p>
                  </div>
                  <div v-if="request.data.sss_number">
                    <label class="text-sm font-medium text-gray-500">SSS Number</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.sss_number }}</p>
                  </div>
                  <div v-if="request.data.osca_id">
                    <label class="text-sm font-medium text-gray-500">OSCA ID</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.osca_id }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Delivery & Payment Preferences - only show if request type collects payment -->
          <div v-if="requestTypeConfig.data?.collect_payment" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Delivery & Payment Preferences</h2>

            <div class="grid grid-cols-2 gap-4">
              <div v-if="request.data.delivery_preference">
                <label class="text-sm font-medium text-gray-500">Delivery Preference</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.delivery_preference }}</p>
              </div>
              <div v-if="request.data.invoice_to">
                <label class="text-sm font-medium text-gray-500">Invoice To</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.invoice_to }}</p>
              </div>
              <div v-if="request.data.invoice_recipient_name">
                <label class="text-sm font-medium text-gray-500">Invoice Recipient Name</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.invoice_recipient_name }}</p>
              </div>
              <div v-if="request.data.invoice_recipient_email">
                <label class="text-sm font-medium text-gray-500">Invoice Recipient Email</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.invoice_recipient_email }}</p>
              </div>
              <div v-if="request.data.purchase_order_number" class="col-span-2">
                <label class="text-sm font-medium text-gray-500">Purchase Order Number</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.purchase_order_number }}</p>
              </div>
            </div>
          </div>

          <!-- Council Meeting Section -->
          <RequestMeetingsSection
            :show="requestTypeConfig.data?.council_meeting_available"
            :meetings="meetings.data"
            :cancelling="cancellingMeeting"
            @book-meeting="handleBookMeeting"
            @edit-meeting="handleEditMeeting"
            @cancel-meeting="handleCancelMeeting"
          />

          <!-- Dynamic Application Data (using step configuration OR fallback to raw data) -->
          <template v-if="reviewSections.length > 0">
            <div
              v-for="step in reviewSections"
              :key="step.step_code"
              class="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <h2 class="text-lg font-semibold text-gray-900 mb-4">{{ step.step_title }}</h2>
              <div class="space-y-4">
                <div
                  v-for="section in step.sections.filter(s => s.show_on_review)"
                  :key="section.section_code"
                >
                  <h3 v-if="section.section_title" class="text-md font-medium text-gray-700 mb-3">
                    {{ section.section_title }}
                  </h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div
                      v-for="field in section.fields.filter(f => f.show_on_review)"
                      :key="field.field_name"
                      class="border-b border-gray-100 pb-3"
                    >
                      <label class="text-sm font-medium text-gray-500">{{ field.review_label || field.field_label }}</label>
                      <p class="mt-1 text-sm text-gray-900">{{ formatFieldValue(field, enrichedRequest[field.field_name]) }}</p>
                    </div>
                  </div>
                </div>
                <p v-if="!hasReviewContent(step)" class="text-gray-500 text-sm">
                  No information to display
                </p>
              </div>
            </div>
          </template>

          <!-- Fallback: Show raw application data if config not loaded -->
          <div v-else-if="parsedFormData && Object.keys(parsedFormData).length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Application Details</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(value, fieldName) in parsedFormData" :key="fieldName" class="border-b border-gray-100 pb-3">
                <label class="text-sm font-medium text-gray-500">{{ formatFieldLabel(fieldName) }}</label>
                <p class="mt-1 text-sm text-gray-900">{{ formatSimpleValue(value) }}</p>
              </div>
            </div>
          </div>

          <!-- Fees & Payments Section -->
          <RequestFeesSection
            :collect-payment="requestTypeConfig.data?.collect_payment"
            :make-payment="requestTypeConfig.data?.make_payment"
            :payment-status="request.data.payment_status"
            :total-fees="request.data.total_fees || 0"
            :total-paid="request.data.total_paid || 0"
            :benefit-amount="requestTypeConfig.data?.base_fee || 0"
            :selected-bank-account="request.data.selected_bank_account"
            @make-payment="handleMakePayment"
          />

          <!-- Documents -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Documents</h2>
              <Button
                @click="handleUploadDocument"
                variant="outline"
                size="sm"
                :loading="uploading"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </template>
                Upload Document
              </Button>
            </div>

            <div v-if="!request.data.attachments || request.data.attachments.length === 0" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="mt-2 text-sm text-gray-500">No documents uploaded yet</p>
            </div>
          </div>
        </div>

        <!-- Sidebar Column -->
        <div class="space-y-6">
          <!-- Timeline -->
          <RequestTimelineCard
            :clock-data="clockData"
            :progress-percent="progressPercent"
            :creation="request.data.creation"
            :modified="request.data.modified"
          />

          <!-- Quick Actions -->
          <RequestActionsCard
            :workflow-state="request.data.workflow_state"
            :council-details="councilDetails"
            :deleting="deleting"
            @edit-draft="handleEditDraft"
            @send-message="handleSendMessage"
            @print-application="handlePrintApplication"
            @delete-draft="handleDeleteDraft"
          />
        </div>
      </div>
    </div>

    <!-- Modals -->
    <SendMessageModal
      v-model:show="showSendMessageModal"
      :request-id="route.params.id"
      @sent="handleMessageSent"
    />

    <BookMeetingModal
      v-model:show="showBookMeetingModal"
      :request-id="route.params.id"
      :request-type-code="requestTypeConfig.data?.type_code"
      :council-code="request.data?.council"
      :meeting="editingMeeting"
      @booked="handleMeetingBooked"
    />

    <PaymentModal
      v-model:show="showPaymentModal"
      :request-id="route.params.id"
      :total-amount="resource.data?.total_fees_incl_gst || 0"
      :fees-excl-gst="resource.data?.total_fees_excl_gst || 0"
      :gst="resource.data?.gst_amount || 0"
      :stripe-enabled="false"
      @invoice-requested="handleInvoiceRequested"
    />
  </div>
</template>

<script setup>
import { Button, createResource } from "frappe-ui"
import { computed, defineAsyncComponent, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import StatusBadge from "../components/StatusBadge.vue"
import RequestActionsCard from "../components/request/RequestActionsCard.vue"
import RequestFeesSection from "../components/request/RequestFeesSection.vue"
import RequestHeader from "../components/request/RequestHeader.vue"
import RequestMeetingsSection from "../components/request/RequestMeetingsSection.vue"
import RequestTimelineCard from "../components/request/RequestTimelineCard.vue"
// Lazy-loaded modals (load on demand to reduce bundle size)
const SendMessageModal = defineAsyncComponent(
	() => import("../components/modals/SendMessageModal.vue"),
)
const BookMeetingModal = defineAsyncComponent(
	() => import("../components/modals/BookMeetingModal.vue"),
)
const PaymentModal = defineAsyncComponent(
	() => import("../components/modals/PaymentModal.vue"),
)
import { useStatutoryClock } from "../composables/useStatutoryClock"

const route = useRoute()
const router = useRouter()

// State
const fileInput = ref(null)
const uploading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const cancellingMeeting = ref(false)
const showSendMessageModal = ref(false)
const showBookMeetingModal = ref(false)

// Get request details
const request = createResource({
	url: "frappe.client.get",
	params: {
		doctype: "Request",
		name: route.params.id,
	},
	auto: true,
})

// Get meetings for this request
const meetings = createResource({
	url: "councilsonline.api.get_request_meetings",
	params: {
		request_id: route.params.id,
	},
	auto: true,
})

// Get request type configuration
const requestTypeConfig = createResource({
	url: "councilsonline.api.get_request_type_config",
	auto: false,
})

// Get council details for contact information
const councilDetails = createResource({
	url: "frappe.client.get",
	auto: false,
})

// Watch for request data and load config
watch(
	() => request.data?.request_type,
	(requestType) => {
		if (requestType) {
			// Pass params directly to fetch() instead of in createResource
			requestTypeConfig.fetch({ request_type_code: requestType })
		}
	},
	{ immediate: true },
)

// Watch for council code and load council details
watch(
	() => request.data?.council,
	(councilCode) => {
		if (councilCode) {
			councilDetails.fetch({
				doctype: "Council",
				name: councilCode,
				fields: ["name", "council_name", "contact_email", "contact_phone"],
			})
		}
	},
	{ immediate: true },
)

// Get statutory clock data from appropriate source (RC Application or Request)
const { clockData, progressPercent } = useStatutoryClock(request)

// Parse form data from draft_full_data as fallback
const parsedFormData = computed(() => {
	if (!request.data) return {}

	try {
		let formData = null
		if (request.data.draft_full_data) {
			formData =
				typeof request.data.draft_full_data === "string"
					? JSON.parse(request.data.draft_full_data)
					: request.data.draft_full_data
		}

		if (!formData) return {}

		// Filter out standard fields
		const standardFields = [
			"name",
			"owner",
			"creation",
			"modified",
			"modified_by",
			"docstatus",
			"idx",
			"council",
			"request_type",
			"request_number",
			"status",
			"requester",
			"requester_name",
			"requester_email",
			"requester_phone",
			"requester_signature",
			"applicant_address",
			"applicant_company",
			"property",
			"property_address",
			"legal_description",
			"brief_description",
			"detailed_description",
			"delivery_preference",
			"invoice_to",
			"invoice_recipient_name",
			"invoice_recipient_email",
			"purchase_order_number",
			"total_fees",
			"total_paid",
			"payment_status",
			"request_category",
			"draft_current_step",
			"draft_total_steps",
			"draft_full_data",
			"form_data",
			"signature_date",
		]

		const filtered = {}
		Object.keys(formData).forEach((key) => {
			if (
				!standardFields.includes(key) &&
				formData[key] !== null &&
				formData[key] !== ""
			) {
				filtered[key] = formData[key]
			}
		})

		return filtered
	} catch (error) {
		console.error("Error parsing form data:", error)
		return {}
	}
})

// Create enriched request data that merges request.data with draft_full_data
const enrichedRequest = computed(() => {
	if (!request.data) return {}

	try {
		let fullFormData = {}
		if (request.data.draft_full_data) {
			fullFormData =
				typeof request.data.draft_full_data === "string"
					? JSON.parse(request.data.draft_full_data)
					: request.data.draft_full_data
		}

		// Merge request.data with full form data from draft_full_data
		// draft_full_data takes precedence for any overlapping keys
		return {
			...request.data,
			...fullFormData,
		}
	} catch (error) {
		console.error("Error merging form data:", error)
		return request.data
	}
})

// Get review sections from request type configuration (same logic as ReviewStep)
const reviewSections = computed(() => {
	if (!requestTypeConfig.data?.steps) return []

	// Filter steps that should show on review
	return requestTypeConfig.data.steps.filter((step) => step.show_on_review)
})

// Check if property details should be displayed (same logic as ReviewStep)
const hasPropertyDetails = computed(() => {
	// Show if request has property address (check enriched data)
	if (enrichedRequest.value?.property_address) {
		return true
	}

	// Check if request type config indicates property is needed
	if (requestTypeConfig.data?.property_required) {
		return true
	}

	return false
})

// Check if a step has any content to show on review
const hasReviewContent = (step) => {
	if (!step.sections) return false

	for (const section of step.sections) {
		if (!section.show_on_review) continue

		for (const field of section.fields) {
			if (field.show_on_review && request.data[field.field_name]) {
				return true
			}
		}
	}

	return false
}

// Format field value for display (same as ReviewStep)
const formatFieldValue = (field, value) => {
	if (value === undefined || value === null || value === "") {
		return "Not provided"
	}

	// Check field type
	if (field.field_type === "Check") {
		return value ? "Yes" : "No"
	}

	if (field.field_type === "Date" && value) {
		// Format date nicely
		try {
			return new Date(value).toLocaleDateString("en-NZ", {
				year: "numeric",
				month: "long",
				day: "numeric",
			})
		} catch (e) {
			return value
		}
	}

	if (field.field_type === "Currency" && value) {
		return `$${Number.parseFloat(value).toFixed(2)}`
	}

	if (Array.isArray(value)) {
		return value.join(", ")
	}

	return value
}

// Helper function to format field labels (convert snake_case to Title Case)
const formatFieldLabel = (fieldName) => {
	return fieldName
		.split("_")
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(" ")
}

// Helper function to format simple values (for fallback display)
const formatSimpleValue = (value) => {
	if (value === null || value === undefined || value === "") {
		return "Not provided"
	}

	if (typeof value === "boolean") {
		return value ? "Yes" : "No"
	}

	if (Array.isArray(value)) {
		return value.join(", ")
	}

	if (typeof value === "object") {
		return JSON.stringify(value)
	}

	// Handle dates
	if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}/.test(value)) {
		try {
			return new Date(value).toLocaleDateString("en-NZ", {
				year: "numeric",
				month: "long",
				day: "numeric",
			})
		} catch (e) {
			return value
		}
	}

	return value
}

// Helper function to format address from address_line object
const formatAddress = (addressObj) => {
	if (!addressObj) return null

	// If it's already a string, return it
	if (typeof addressObj === "string") return addressObj

	// If it's an object with full_address, use that
	if (addressObj.full_address) return addressObj.full_address

	// Otherwise build address from components
	const parts = []
	if (addressObj.address_line) parts.push(addressObj.address_line)
	if (addressObj.barangay) parts.push(`Brgy. ${addressObj.barangay}`)
	if (addressObj.municipality) parts.push(addressObj.municipality)
	if (addressObj.province) parts.push(addressObj.province)
	if (addressObj.zip_code) parts.push(addressObj.zip_code)

	return parts.length > 0 ? parts.join(", ") : null
}

const goBack = () => {
	router.push({ name: "Dashboard" })
}

// Format meeting date with time
const formatMeetingDate = (dateStr) => {
	if (!dateStr) return "Not scheduled"
	try {
		return new Date(dateStr).toLocaleString("en-NZ", {
			weekday: "long",
			year: "numeric",
			month: "long",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		})
	} catch (e) {
		return dateStr
	}
}

const formatDate = (dateStr) => {
	if (!dateStr) return "N/A"
	const date = new Date(dateStr)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
		hour: "2-digit",
		minute: "2-digit",
	})
}

// Quick Actions
const handleUploadDocument = () => {
	fileInput.value.click()
}

const handleFileUpload = async (event) => {
	const files = Array.from(event.target.files)
	if (files.length === 0) return

	uploading.value = true
	try {
		for (const file of files) {
			const formData = new FormData()
			formData.append("file", file)
			formData.append("doctype", "Request")
			formData.append("docname", request.data.name)
			formData.append("is_private", 0)

			await fetch("/api/method/upload_file", {
				method: "POST",
				headers: {
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: formData,
			})
		}

		alert(`${files.length} document(s) uploaded successfully!`)
		request.reload()
		event.target.value = "" // Reset file input
	} catch (error) {
		console.error("Error uploading file:", error)
		alert("Failed to upload document. Please try again.")
	} finally {
		uploading.value = false
	}
}

const handleSendMessage = () => {
	showSendMessageModal.value = true
}

const handleMessageSent = () => {
	// Toast notification would be better than alert to avoid blocking modal close
	// alert('Message sent successfully! The council will respond within 2-3 business days.')
	request.reload()
}

const handlePrintApplication = () => {
	window.print()
}

const handleEditDraft = () => {
	if (!request.data) {
		alert("Error: Request data not loaded")
		return
	}

	if (!request.data.request_type) {
		alert("Error: Request type missing")
		return
	}

	const url = `/request/new?type=${encodeURIComponent(request.data.request_type)}&draft=${encodeURIComponent(request.data.name)}`
	router.push(url)
}

const handleDeleteDraft = async () => {
	if (
		!confirm(
			"Are you sure you want to delete this draft application? This action cannot be undone.",
		)
	) {
		return
	}

	deleting.value = true
	try {
		await fetch("/api/method/frappe.client.delete", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": window.csrf_token,
			},
			body: JSON.stringify({
				doctype: "Request",
				name: request.data.name,
			}),
		})

		alert("Draft deleted successfully")
		router.push({ name: "Dashboard" })
	} catch (error) {
		console.error("Error deleting draft:", error)
		alert("Failed to delete draft. Please try again.")
	} finally {
		deleting.value = false
	}
}

const handleSubmitApplication = async () => {
	if (
		!confirm(
			"Are you sure you want to submit this application? Once submitted, it cannot be edited.",
		)
	) {
		return
	}

	submitting.value = true
	try {
		const response = await fetch(
			"/api/method/councilsonline.councilsonline.doctype.request.request.submit_application",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					request_id: request.data.name,
				}),
			},
		)

		const result = await response.json()

		if (result.message && result.message.success) {
			alert(
				`Application submitted successfully! Request Number: ${result.message.request_number}`,
			)
			request.reload()
		} else {
			throw new Error("Failed to submit application")
		}
	} catch (error) {
		console.error("Error submitting application:", error)
		alert("Failed to submit application. Please try again.")
	} finally {
		submitting.value = false
	}
}

const showPaymentModal = ref(false)

const handleMakePayment = () => {
	showPaymentModal.value = true
}

const handleInvoiceRequested = (invoiceData) => {
	// Show success message
	const message =
		invoiceData.warning ||
		`Invoice requested successfully!\n\nInvoice #${invoiceData.invoice_number}\nAn email has been sent to ${invoiceData.email}`

	alert(message)

	// Reload request to show updated payment status
	resource.reload()
}

const handleBookMeeting = () => {
	showBookMeetingModal.value = true
}

const handleMeetingBooked = async (meetingData) => {
	alert(
		`Meeting request submitted successfully!\n\nMeeting ID: ${meetingData.meeting_id}\nStatus: ${meetingData.status}\n\nA council planner will contact you within 2 business days.`,
	)
	// Clear editing state and reload meetings list
	editingMeeting.value = null
	await meetings.reload()
}

const editingMeeting = ref(null)

const handleEditMeeting = (meeting) => {
	// Store meeting data for pre-filling the modal
	editingMeeting.value = meeting
	showBookMeetingModal.value = true
}

const handleCancelMeeting = async (meeting) => {
	if (
		!confirm(
			`Are you sure you want to cancel this meeting request?\n\nMeeting Type: ${meeting.meeting_type}\nStatus: ${meeting.status}\n\nThis action cannot be undone.`,
		)
	) {
		return
	}

	cancellingMeeting.value = true
	try {
		const response = await fetch("/api/method/councilsonline.api.cancel_meeting", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": window.csrf_token,
			},
			body: JSON.stringify({
				meeting_id: meeting.name,
			}),
		})

		const result = await response.json()

		if (result.message && result.message.success) {
			alert("Meeting cancelled successfully.")
			await meetings.reload()
		} else {
			throw new Error(result.message?.error || "Failed to cancel meeting")
		}
	} catch (error) {
		console.error("Error cancelling meeting:", error)
		alert(
			`Failed to cancel meeting: ${error.message}\n\nPlease try again or contact support.`,
		)
	} finally {
		cancellingMeeting.value = false
	}
}
</script>

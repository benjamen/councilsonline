<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-4">
            <button @click="goBack" class="text-gray-600 hover:text-gray-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900">{{ request.data?.request_number || 'Loading...' }}</h1>
              <p class="text-sm text-gray-500">{{ request.data?.request_type }}</p>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <StatusBadge v-if="request.data" :status="request.data.status" />
            <Button
              v-if="request.data?.status === 'Draft'"
              @click="handleSubmitApplication"
              variant="solid"
              theme="blue"
              :loading="submitting"
            >
              Submit Application
            </Button>
          </div>
        </div>
      </div>
    </header>

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
                  <StatusBadge :status="request.data.status" />
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

          <!-- Property Information -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Property Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-500">Property ID</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.property || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.property_address || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Resource Consent Details (if applicable) -->
          <ResourceConsentDetails
            v-if="request.data?.request_category === 'Resource Consent'"
            :request-id="request.data.name"
          />

          <!-- Applicant Information -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Applicant Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-500">Name</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_name || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Email</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_email || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Phone</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_phone || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_address || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Fees & Payments -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Fees & Payments</h2>
              <span class="text-sm font-medium" :class="request.data.payment_status === 'Paid' ? 'text-green-600' : 'text-orange-600'">
                {{ request.data.payment_status || 'Unpaid' }}
              </span>
            </div>

            <div class="space-y-3">
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="text-sm text-gray-600">Total Fees</span>
                <span class="text-sm font-semibold text-gray-900">${{ (request.data.total_fees || 0).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="text-sm text-gray-600">Total Paid</span>
                <span class="text-sm font-semibold text-green-600">${{ (request.data.total_paid || 0).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center py-2">
                <span class="text-sm font-medium text-gray-900">Outstanding</span>
                <span class="text-sm font-bold text-orange-600">${{ ((request.data.total_fees || 0) - (request.data.total_paid || 0)).toFixed(2) }}</span>
              </div>
            </div>

            <Button
              v-if="(request.data.total_fees || 0) > (request.data.total_paid || 0)"
              @click="handleMakePayment"
              variant="solid"
              theme="blue"
              class="w-full mt-4"
            >
              Make Payment
            </Button>
          </div>

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
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Processing Timeline</h2>

            <!-- Statutory Clock -->
            <div v-if="clockData.statutory_clock_started" class="mb-6 p-4 bg-blue-50 rounded-lg">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-blue-900">Statutory Clock</span>
                <span class="text-xs text-blue-700">{{ clockData.working_days_elapsed }} of 20 days</span>
              </div>
              <div class="w-full bg-blue-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${progressPercent}%` }"
                ></div>
              </div>
              <p class="mt-2 text-xs text-blue-700">
                {{ clockData.statutory_clock_stopped ? 'Clock stopped (RFI issued)' : `${clockData.working_days_remaining} days remaining` }}
              </p>
            </div>

            <!-- Status History -->
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">Application Created</p>
                  <p class="text-xs text-gray-500">{{ formatDate(request.data.creation) }}</p>
                </div>
              </div>

              <div v-if="request.data.modified !== request.data.creation" class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">Last Updated</p>
                  <p class="text-xs text-gray-500">{{ formatDate(request.data.modified) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Meetings -->
          <div v-if="meetings.data && meetings.data.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Pre-Application Meetings</h2>

            <div class="space-y-3">
              <div
                v-for="meeting in meetings.data"
                :key="meeting.name"
                class="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-start justify-between mb-2">
                  <span class="text-sm font-medium text-gray-900">{{ meeting.meeting_type }}</span>
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                    :class="{
                      'bg-yellow-100 text-yellow-800': meeting.status === 'Requested',
                      'bg-blue-100 text-blue-800': meeting.status === 'Scheduled',
                      'bg-green-100 text-green-800': meeting.status === 'Confirmed' || meeting.status === 'Completed',
                      'bg-orange-100 text-orange-800': meeting.status === 'Rescheduled',
                      'bg-red-100 text-red-800': meeting.status === 'Cancelled'
                    }"
                  >
                    {{ meeting.status }}
                  </span>
                </div>

                <div v-if="meeting.scheduled_start" class="flex items-center text-xs text-gray-600 mb-1">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ formatDate(meeting.scheduled_start) }}
                </div>

                <div v-if="meeting.meeting_format" class="flex items-center text-xs text-gray-600 mb-1">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {{ meeting.meeting_format }}
                </div>

                <div v-if="meeting.meeting_location" class="text-xs text-gray-600">
                  {{ meeting.meeting_location }}
                </div>

                <div v-if="meeting.meeting_purpose" class="mt-2 text-xs text-gray-500 line-clamp-2">
                  {{ meeting.meeting_purpose }}
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>

            <div class="space-y-3">
              <Button
                @click="handleSendMessage"
                variant="outline"
                class="w-full justify-start"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </template>
                Send Message
              </Button>

              <Button
                @click="handlePrintApplication"
                variant="outline"
                class="w-full justify-start"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                  </svg>
                </template>
                Print Application
              </Button>

              <Button
                v-if="request.data.status === 'Draft'"
                @click="handleDeleteDraft"
                variant="outline"
                class="w-full justify-start text-red-600 hover:text-red-700"
                :loading="deleting"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </template>
                Delete Draft
              </Button>

              <Button
                v-if="request.data.request_category === 'Resource Consent'"
                @click="handleBookMeeting"
                variant="outline"
                class="w-full justify-start text-green-600 hover:text-green-700"
                :loading="bookingMeeting"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </template>
                Book Pre-Application Meeting
              </Button>
            </div>
          </div>

          <!-- Contact Info -->
          <div class="bg-blue-50 rounded-lg border border-blue-200 p-6">
            <h3 class="text-sm font-semibold text-blue-900 mb-3">Need Help?</h3>
            <p class="text-xs text-blue-800 mb-4">Contact our planning team for assistance with your application.</p>
            <div class="space-y-2 text-xs text-blue-900">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>consents@council.govt.nz</span>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>0800 LODGEICK</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import StatusBadge from '../components/StatusBadge.vue'
import ResourceConsentDetails from '../components/ResourceConsentDetails.vue'
import { useStatutoryClock } from '../composables/useStatutoryClock'

const route = useRoute()
const router = useRouter()

// State
const fileInput = ref(null)
const uploading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const bookingMeeting = ref(false)

// Get request details
const request = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'Request',
    name: route.params.id
  },
  auto: true,
})

// Get meetings for this request
const meetings = createResource({
  url: 'lodgeick.api.get_request_meetings',
  params: {
    request_id: route.params.id
  },
  auto: true,
})

// Get statutory clock data from appropriate source (RC Application or Request)
const { clockData, progressPercent } = useStatutoryClock(request)

const goBack = () => {
  router.push({ name: 'Dashboard' })
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-NZ', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
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
      formData.append('file', file)
      formData.append('doctype', 'Request')
      formData.append('docname', request.data.name)
      formData.append('is_private', 0)

      await fetch('/api/method/upload_file', {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token
        },
        body: formData
      })
    }

    alert(`${files.length} document(s) uploaded successfully!`)
    request.reload()
    event.target.value = '' // Reset file input
  } catch (error) {
    console.error('Error uploading file:', error)
    alert('Failed to upload document. Please try again.')
  } finally {
    uploading.value = false
  }
}

const handleSendMessage = () => {
  // TODO: Implement message modal/dialog
  alert('Send Message feature - Coming soon!\n\nFor now, please contact us at:\nconsents@council.govt.nz\n0800 LODGEICK')
}

const handlePrintApplication = () => {
  window.print()
}

const handleDeleteDraft = async () => {
  if (!confirm('Are you sure you want to delete this draft application? This action cannot be undone.')) {
    return
  }

  deleting.value = true
  try {
    await fetch('/api/method/frappe.client.delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        doctype: 'Request',
        name: request.data.name
      })
    })

    alert('Draft deleted successfully')
    router.push({ name: 'Dashboard' })
  } catch (error) {
    console.error('Error deleting draft:', error)
    alert('Failed to delete draft. Please try again.')
  } finally {
    deleting.value = false
  }
}

const handleSubmitApplication = async () => {
  if (!confirm('Are you sure you want to submit this application? Once submitted, it cannot be edited.')) {
    return
  }

  submitting.value = true
  try {
    const response = await fetch('/api/method/lodgeick.lodgeick.doctype.request.request.submit_application', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: request.data.name
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      alert(`Application submitted successfully! Request Number: ${result.message.request_number}`)
      request.reload()
    } else {
      throw new Error('Failed to submit application')
    }
  } catch (error) {
    console.error('Error submitting application:', error)
    alert('Failed to submit application. Please try again.')
  } finally {
    submitting.value = false
  }
}

const handleMakePayment = () => {
  // TODO: Implement payment integration
  alert('Payment feature - Coming soon!\n\nYou will receive an invoice via email.')
}

const handleBookMeeting = async () => {
  bookingMeeting.value = true
  try {
    const response = await fetch('/api/method/lodgeick.api.book_council_meeting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        request_id: request.data.name,
        meeting_type: 'Pre-Application Meeting'
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      alert(`Pre-Application Meeting request has been submitted! A council officer will contact you within 2 business days to schedule the meeting. Meeting ID: ${result.message.meeting_id}`)
      // Refresh meetings list to show the new meeting
      await meetings.reload()
    } else {
      throw new Error(result.message || 'Failed to book meeting')
    }
  } catch (error) {
    console.error('Error booking meeting:', error)
    alert('Failed to book pre-application meeting. Please try again.')
  } finally {
    bookingMeeting.value = false
  }
}
</script>

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

          <!-- Property Information - only show if request type has property -->
          <div v-if="hasPropertyDetails" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Property Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div v-if="request.data.property_address">
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.property_address }}</p>
              </div>
              <div v-if="request.data.legal_description">
                <label class="text-sm font-medium text-gray-500">Legal Description</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.legal_description }}</p>
              </div>
            </div>
          </div>

          <!-- Applicant Information -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Applicant Information</h2>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-500">Name</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.requester_name || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Email</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.requester_email || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Phone</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.requester_phone || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Address</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_address || 'N/A' }}</p>
              </div>
              <div v-if="request.data.applicant_company">
                <label class="text-sm font-medium text-gray-500">Company/Organization</label>
                <p class="mt-1 text-sm text-gray-900">{{ request.data.applicant_company }}</p>
              </div>
            </div>
          </div>

          <!-- SPISC Application Details - only show if request is SPISC -->
          <div v-if="request.data?.request_type?.includes('SPISC') && request.data.application_name" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">SPISC Application Details</h2>

            <div class="space-y-6">
              <!-- Personal Information -->
              <div>
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Personal Information</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Birth Date</label>
                    <p class="mt-1 text-sm text-gray-900">{{ formatDate(request.data.birth_date) || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Age</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.age || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Sex</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.sex || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Civil Status</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.civil_status || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Household & Economic Information -->
              <div>
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Household & Economic Information</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-500">Household Size</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.household_size || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Living Arrangement</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.living_arrangement || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Monthly Income</label>
                    <p class="mt-1 text-sm text-gray-900">₱{{ request.data.monthly_income || '0' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">Income Source</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.income_source || 'N/A' }}</p>
                  </div>
                  <div>
                    <label class="text-sm font-medium text-gray-500">4Ps Beneficiary</label>
                    <p class="mt-1 text-sm text-gray-900">{{ request.data.is_4ps_beneficiary ? 'Yes' : 'No' }}</p>
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
          <div v-if="requestTypeConfig.data?.council_meeting_available" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h2 class="text-lg font-semibold text-gray-900">Council Meeting</h2>
                <p class="text-sm text-gray-600 mt-1">
                  Schedule a meeting with council planners to discuss your application
                </p>
              </div>

              <!-- Status Badge if meeting exists -->
              <span
                v-if="meetings.data && meetings.data.length > 0"
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="{
                  'bg-yellow-100 text-yellow-800': meetings.data[0].status === 'Requested',
                  'bg-blue-100 text-blue-800': meetings.data[0].status === 'Scheduled' || meetings.data[0].status === 'Confirmed',
                  'bg-green-100 text-green-800': meetings.data[0].status === 'Completed',
                  'bg-gray-100 text-gray-800': meetings.data[0].status === 'Cancelled'
                }"
              >
                {{ meetings.data[0].status }}
              </span>
            </div>

            <!-- Meeting Details (if exists) -->
            <div v-if="meetings.data && meetings.data.length > 0" class="space-y-4">
              <div v-for="meeting in meetings.data" :key="meeting.name" class="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span class="font-medium text-gray-700">Type:</span>
                    <span class="ml-2 text-gray-900">{{ meeting.meeting_type }}</span>
                  </div>
                  <div>
                    <span class="font-medium text-gray-700">Status:</span>
                    <span class="ml-2 text-gray-900">{{ meeting.status }}</span>
                  </div>
                  <div v-if="meeting.scheduled_start" class="col-span-2">
                    <span class="font-medium text-gray-700">Scheduled:</span>
                    <span class="ml-2 text-gray-900">{{ formatMeetingDate(meeting.scheduled_start) }}</span>
                  </div>
                  <div v-if="meeting.meeting_format" class="col-span-2">
                    <span class="font-medium text-gray-700">Format:</span>
                    <span class="ml-2 text-gray-900">{{ meeting.meeting_format }}</span>
                  </div>
                  <div v-if="meeting.meeting_location" class="col-span-2">
                    <span class="font-medium text-gray-700">Location:</span>
                    <span class="ml-2 text-gray-900">{{ meeting.meeting_location }}</span>
                  </div>
                  <div v-if="meeting.google_meet_link" class="col-span-2">
                    <span class="font-medium text-gray-700">Meeting Link:</span>
                    <a :href="meeting.google_meet_link" target="_blank" class="ml-2 text-blue-600 hover:underline">Join Meeting</a>
                  </div>
                </div>

                <div v-if="meeting.meeting_purpose" class="mt-3 pt-3 border-t border-blue-200">
                  <span class="font-medium text-gray-700 text-sm">Purpose:</span>
                  <p class="mt-1 text-sm text-gray-900">{{ meeting.meeting_purpose }}</p>
                </div>

                <!-- Proposed Time Slots (if status is Requested and slots exist) -->
                <div v-if="meeting.status === 'Requested' && meeting.proposed_slots && meeting.proposed_slots.length > 0" class="mt-3 pt-3 border-t border-blue-200">
                  <span class="font-medium text-gray-700 text-sm">Proposed Time Slots:</span>
                  <ul class="mt-2 space-y-1">
                    <li v-for="(slot, index) in meeting.proposed_slots" :key="index" class="text-sm text-gray-900 flex items-center">
                      <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ formatMeetingDate(slot) }}
                    </li>
                  </ul>
                </div>

                <!-- Action Buttons (Edit/Cancel) - only show if meeting is Requested or Scheduled -->
                <div v-if="meeting.status === 'Requested' || meeting.status === 'Scheduled'" class="mt-4 pt-3 border-t border-blue-200 flex space-x-3">
                  <button
                    @click="handleEditMeeting(meeting)"
                    class="flex-1 px-4 py-2 bg-white border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-sm font-medium"
                  >
                    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit Request
                  </button>
                  <button
                    @click="handleCancelMeeting(meeting)"
                    :disabled="cancellingMeeting"
                    class="flex-1 px-4 py-2 bg-white border border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Cancel Meeting
                  </button>
                </div>
              </div>
            </div>

            <!-- Request Meeting Button (if no meeting) -->
            <div v-else class="text-center py-6">
              <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p class="text-sm text-gray-600 mb-4">
                No meeting scheduled yet. Book a meeting to discuss your application with council planners.
              </p>
              <button
                @click="handleBookMeeting"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Request Council Meeting
              </button>
            </div>
          </div>

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
                      <p class="mt-1 text-sm text-gray-900">{{ formatFieldValue(field, request.data[field.field_name]) }}</p>
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

          <!-- Fees & Payments -->
          <div v-if="requestTypeConfig.data?.collect_payment" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
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

          <!-- Payment to be Received (for social services / benefits) -->
          <div v-if="requestTypeConfig.data?.make_payment" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Payment to be Received</h2>
              <span class="text-sm font-medium" :class="request.data.payment_status === 'Paid' ? 'text-green-600' : 'text-orange-600'">
                {{ request.data.payment_status || 'Pending' }}
              </span>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div class="flex items-start">
                <svg class="h-5 w-5 text-blue-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="flex-1">
                  <p class="text-sm font-medium text-blue-900">Benefit Payment Information</p>
                  <p class="text-sm text-blue-700 mt-1">
                    Once your application is approved, you will receive payment from the council.
                    Please ensure your bank details are up to date.
                  </p>
                </div>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="text-sm text-gray-600">Benefit Amount</span>
                <span class="text-sm font-semibold text-gray-900">
                  ${{ requestTypeConfig.data?.base_fee ? requestTypeConfig.data.base_fee.toFixed(2) : '0.00' }}
                </span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="text-sm text-gray-600">Payment Status</span>
                <span class="text-sm font-semibold" :class="request.data.payment_status === 'Paid' ? 'text-green-600' : 'text-orange-600'">
                  {{ request.data.payment_status || 'Pending Approval' }}
                </span>
              </div>
              <div v-if="request.data.selected_bank_account" class="flex justify-between items-center py-2">
                <span class="text-sm text-gray-600">Payment Method</span>
                <span class="text-sm font-medium text-gray-900">Bank Transfer</span>
              </div>
            </div>
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

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>

            <div class="space-y-3">
              <Button
                v-if="request.data.status === 'Draft'"
                @click="handleEditDraft"
                variant="solid"
                theme="blue"
                class="w-full justify-start"
              >
                <template #prefix>
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </template>
                Edit Draft
              </Button>

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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 1 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </template>
                Delete Draft
              </Button>
            </div>
          </div>

          <!-- Contact Info -->
          <div class="bg-blue-50 rounded-lg border border-blue-200 p-6">
            <h3 class="text-sm font-semibold text-blue-900 mb-3">Need Help?</h3>
            <p class="text-xs text-blue-800 mb-4">Contact {{ councilDetails.data?.council_name || 'the council' }} for assistance with your application.</p>
            <div v-if="councilDetails.loading" class="text-xs text-blue-800">
              Loading contact information...
            </div>
            <div v-else-if="councilDetails.data" class="space-y-2 text-xs text-blue-900">
              <div v-if="councilDetails.data.contact_email" class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <a :href="`mailto:${councilDetails.data.contact_email}`" class="hover:underline">
                  {{ councilDetails.data.contact_email }}
                </a>
              </div>
              <div v-if="councilDetails.data.contact_phone" class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <a :href="`tel:${councilDetails.data.contact_phone}`" class="hover:underline">
                  {{ councilDetails.data.contact_phone }}
                </a>
              </div>
            </div>
          </div>
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
      @booked="handleMeetingBooked"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, Button } from 'frappe-ui'
import StatusBadge from '../components/StatusBadge.vue'
import SendMessageModal from '../components/modals/SendMessageModal.vue'
import BookMeetingModal from '../components/modals/BookMeetingModal.vue'
import { useStatutoryClock } from '../composables/useStatutoryClock'

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

// Get request type configuration
const requestTypeConfig = createResource({
  url: 'lodgeick.api.get_request_type_config',
  auto: false,
})

// Get council details for contact information
const councilDetails = createResource({
  url: 'frappe.client.get',
  auto: false,
})

// Watch for request data and load config
watch(() => request.data?.request_type, (requestType) => {
  if (requestType) {
    // Pass params directly to fetch() instead of in createResource
    requestTypeConfig.fetch({ request_type_code: requestType })
  }
}, { immediate: true })

// Watch for council code and load council details
watch(() => request.data?.council, (councilCode) => {
  if (councilCode) {
    councilDetails.fetch({
      doctype: 'Council',
      name: councilCode,
      fields: ['name', 'council_name', 'contact_email', 'contact_phone']
    })
  }
}, { immediate: true })

// Get statutory clock data from appropriate source (RC Application or Request)
const { clockData, progressPercent } = useStatutoryClock(request)

// Parse form data from draft_full_data as fallback
const parsedFormData = computed(() => {
  if (!request.data) return {}

  try {
    let formData = null
    if (request.data.draft_full_data) {
      formData = typeof request.data.draft_full_data === 'string'
        ? JSON.parse(request.data.draft_full_data)
        : request.data.draft_full_data
    }

    if (!formData) return {}

    // Filter out standard fields
    const standardFields = [
      'name', 'owner', 'creation', 'modified', 'modified_by', 'docstatus', 'idx',
      'council', 'request_type', 'request_number', 'status', 'requester',
      'requester_name', 'requester_email', 'requester_phone', 'requester_signature',
      'applicant_address', 'applicant_company', 'property', 'property_address',
      'legal_description', 'brief_description', 'detailed_description',
      'delivery_preference', 'invoice_to', 'invoice_recipient_name',
      'invoice_recipient_email', 'purchase_order_number', 'total_fees',
      'total_paid', 'payment_status', 'request_category', 'draft_current_step',
      'draft_total_steps', 'draft_full_data', 'form_data', 'signature_date'
    ]

    const filtered = {}
    Object.keys(formData).forEach(key => {
      if (!standardFields.includes(key) && formData[key] !== null && formData[key] !== '') {
        filtered[key] = formData[key]
      }
    })

    return filtered
  } catch (error) {
    console.error('Error parsing form data:', error)
    return {}
  }
})

// Get review sections from request type configuration (same logic as ReviewStep)
const reviewSections = computed(() => {
  if (!requestTypeConfig.data?.steps) return []

  // Filter steps that should show on review
  return requestTypeConfig.data.steps.filter(step => step.show_on_review)
})

// Check if property details should be displayed (same logic as ReviewStep)
const hasPropertyDetails = computed(() => {
  // Show if request has property address
  if (request.data?.property_address) {
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
  if (value === undefined || value === null || value === '') {
    return 'Not provided'
  }

  // Check field type
  if (field.field_type === 'Check') {
    return value ? 'Yes' : 'No'
  }

  if (field.field_type === 'Date' && value) {
    // Format date nicely
    try {
      return new Date(value).toLocaleDateString('en-NZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch (e) {
      return value
    }
  }

  if (field.field_type === 'Currency' && value) {
    return `$${parseFloat(value).toFixed(2)}`
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  return value
}

// Helper function to format field labels (convert snake_case to Title Case)
const formatFieldLabel = (fieldName) => {
  return fieldName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Helper function to format simple values (for fallback display)
const formatSimpleValue = (value) => {
  if (value === null || value === undefined || value === '') {
    return 'Not provided'
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  // Handle dates
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value)) {
    try {
      return new Date(value).toLocaleDateString('en-NZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch (e) {
      return value
    }
  }

  return value
}

const goBack = () => {
  router.push({ name: 'Dashboard' })
}

// Format meeting date with time
const formatMeetingDate = (dateStr) => {
  if (!dateStr) return 'Not scheduled'
  try {
    return new Date(dateStr).toLocaleString('en-NZ', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
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
    alert('Error: Request data not loaded')
    return
  }

  if (!request.data.request_type) {
    alert('Error: Request type missing')
    return
  }

  const url = `/request/new?type=${encodeURIComponent(request.data.request_type)}&draft=${encodeURIComponent(request.data.name)}`
  router.push(url)
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

const handleBookMeeting = () => {
  showBookMeetingModal.value = true
}

const handleMeetingBooked = async (meetingData) => {
  alert(`Meeting request submitted successfully!\n\nMeeting ID: ${meetingData.meeting_id}\nStatus: ${meetingData.status}\n\nA council planner will contact you within 2 business days.`)
  // Reload meetings list
  await meetings.reload()
}

const handleEditMeeting = (meeting) => {
  // Re-open the booking modal with existing meeting data
  // The modal should be enhanced to accept a meeting prop for editing
  showBookMeetingModal.value = true
  // TODO: Pass meeting data to modal for pre-filling
  alert('Edit meeting functionality - opening booking modal.\n\nNote: You can submit a new request with updated time slots. The previous request will be updated.')
}

const handleCancelMeeting = async (meeting) => {
  if (!confirm(`Are you sure you want to cancel this meeting request?\n\nMeeting Type: ${meeting.meeting_type}\nStatus: ${meeting.status}\n\nThis action cannot be undone.`)) {
    return
  }

  cancellingMeeting.value = true
  try {
    const response = await fetch('/api/method/lodgeick.api.cancel_meeting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.csrf_token
      },
      body: JSON.stringify({
        meeting_id: meeting.name
      })
    })

    const result = await response.json()

    if (result.message && result.message.success) {
      alert('Meeting cancelled successfully.')
      await meetings.reload()
    } else {
      throw new Error(result.message?.error || 'Failed to cancel meeting')
    }
  } catch (error) {
    console.error('Error cancelling meeting:', error)
    alert(`Failed to cancel meeting: ${error.message}\n\nPlease try again or contact support.`)
  } finally {
    cancellingMeeting.value = false
  }
}
</script>

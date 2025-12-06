<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center p-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading application details...</span>
    </div>

    <!-- Resource Consent Application -->
    <template v-else-if="applicationDoctype === 'Resource Consent Application' && rcApplication">
      <!-- Consent Details -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-blue-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <h3 class="font-semibold text-blue-900">Consent Details</h3>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <!-- Consent Types -->
          <div>
            <span class="text-sm font-medium text-gray-700">Consent Types:</span>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="ct in (rcApplication.consent_types || [])"
                :key="ct.consent_type"
                class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {{ ct.consent_type }}
              </span>
              <span v-if="!rcApplication.consent_types || rcApplication.consent_types.length === 0" class="text-gray-500 text-sm">
                None selected
              </span>
            </div>
          </div>

          <!-- Activity Status -->
          <div>
            <span class="text-sm font-medium text-gray-700">Activity Status:</span>
            <span :class="activityStatusClass(rcApplication.activity_status)" class="ml-2 px-3 py-1 rounded-full text-sm font-medium">
              {{ rcApplication.activity_status || 'Not specified' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Property Information -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 border-b border-green-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <h3 class="font-semibold text-green-900">Property Information</h3>
          </div>
        </div>
        <div class="p-6">
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="rcApplication.property_address_display">
              <dt class="text-sm font-medium text-gray-500">Address</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.property_address_display }}</dd>
            </div>
            <div v-if="rcApplication.legal_description_display">
              <dt class="text-sm font-medium text-gray-500">Legal Description</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.legal_description_display }}</dd>
            </div>
            <div v-if="rcApplication.zoning_display">
              <dt class="text-sm font-medium text-gray-500">Zoning</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.zoning_display }}</dd>
            </div>
            <div v-if="rcApplication.site_area_display">
              <dt class="text-sm font-medium text-gray-500">Site Area</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.site_area_display }} m²</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Affected Parties (if any) -->
      <div v-if="rcApplication.affected_parties && rcApplication.affected_parties.length > 0" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-purple-50 to-indigo-50 px-6 py-4 border-b border-purple-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-6 w-6 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              <h3 class="font-semibold text-purple-900">Affected Parties & Written Approvals</h3>
            </div>
            <div class="bg-blue-100 px-3 py-1 rounded-full">
              <span class="text-2xl font-bold text-blue-900">{{ getApprovalCount() }}</span>
              <span class="text-gray-600"> / </span>
              <span class="text-xl font-semibold text-gray-700">{{ rcApplication.affected_parties.length }}</span>
              <span class="text-xs text-gray-600 ml-1">approvals</span>
            </div>
          </div>
        </div>
        <div class="p-6">
          <table class="min-w-full divide-y divide-gray-300">
            <thead>
              <tr>
                <th class="text-left text-sm font-semibold text-gray-900 pb-2">Party</th>
                <th class="text-left text-sm font-semibold text-gray-900 pb-2">Relationship</th>
                <th class="text-left text-sm font-semibold text-gray-900 pb-2">Approval Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="party in rcApplication.affected_parties" :key="party.name">
                <td class="py-3 text-sm text-gray-900">{{ party.party_name }}</td>
                <td class="py-3 text-sm text-gray-700">{{ party.relationship_type || 'Not specified' }}</td>
                <td class="py-3 text-sm">
                  <span v-if="party.has_written_approval" class="inline-flex items-center text-green-600">
                    <svg class="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    Approval obtained
                  </span>
                  <span v-else class="text-gray-500">No approval</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- AEE Summary (if provided) -->
      <div v-if="rcApplication.assessment_of_effects" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-emerald-50 to-green-50 px-6 py-4 border-b border-emerald-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-emerald-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <h3 class="font-semibold text-emerald-900">Assessment of Environmental Effects</h3>
          </div>
        </div>
        <div class="p-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm font-medium text-gray-700">Word Count:</span>
              <span class="text-lg font-bold text-blue-600">{{ getWordCount(rcApplication.assessment_of_effects) }} words</span>
            </div>
            <div class="prose max-w-none text-sm text-gray-700">
              {{ getExcerpt(rcApplication.assessment_of_effects, 300) }}
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- SPISC Application -->
    <template v-else-if="applicationDoctype === 'SPISC Application' && spiscApplication">
      <!-- Personal Information -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-blue-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <h3 class="font-semibold text-blue-900">Personal Information</h3>
          </div>
        </div>
        <div class="p-6">
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt class="text-sm font-medium text-gray-500">Full Name</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.full_name }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Age</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.age }} years old</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Sex</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.sex }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Civil Status</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.civil_status }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Address Information -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-4 border-b border-green-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <h3 class="font-semibold text-green-900">Residential Address</h3>
          </div>
        </div>
        <div class="p-6">
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <dt class="text-sm font-medium text-gray-500">Complete Address</dt>
              <dd class="mt-1 text-sm text-gray-900">
                {{ spiscApplication.address_line }}, {{ spiscApplication.barangay }}, {{ spiscApplication.municipality }}, {{ spiscApplication.province }}
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Mobile Number</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.mobile_number }}</dd>
            </div>
            <div v-if="spiscApplication.email">
              <dt class="text-sm font-medium text-gray-500">Email</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.email }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Economic & Household Information -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gradient-to-r from-yellow-50 to-amber-50 px-6 py-4 border-b border-yellow-200">
          <div class="flex items-center">
            <svg class="h-6 w-6 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h3 class="font-semibold text-yellow-900">Economic & Household Status</h3>
          </div>
        </div>
        <div class="p-6">
          <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt class="text-sm font-medium text-gray-500">Monthly Income</dt>
              <dd class="mt-1 text-sm text-gray-900">PHP {{ spiscApplication.monthly_income?.toLocaleString() || '0' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Income Source</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.income_source }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Household Size</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.household_size }} members</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Living Arrangement</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.living_arrangement }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">4Ps Beneficiary</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ spiscApplication.is_4ps_beneficiary ? 'Yes' : 'No' }}</dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Eligibility Status (if assessed) -->
      <div v-if="spiscApplication.eligibility_status && spiscApplication.eligibility_status !== 'Pending'" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200"
          :class="spiscApplication.eligibility_status === 'Eligible' ? 'bg-green-50' : 'bg-red-50'">
          <div class="flex items-center">
            <svg class="h-6 w-6 mr-2"
              :class="spiscApplication.eligibility_status === 'Eligible' ? 'text-green-600' : 'text-red-600'"
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h3 class="font-semibold"
              :class="spiscApplication.eligibility_status === 'Eligible' ? 'text-green-900' : 'text-red-900'">
              Eligibility Assessment
            </h3>
          </div>
        </div>
        <div class="p-6">
          <div class="space-y-3">
            <div>
              <span class="text-sm font-medium text-gray-500">Status:</span>
              <span class="ml-2 px-3 py-1 rounded-full text-sm font-medium"
                :class="spiscApplication.eligibility_status === 'Eligible' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                {{ spiscApplication.eligibility_status }}
              </span>
            </div>
            <div v-if="spiscApplication.eligibility_notes">
              <span class="text-sm font-medium text-gray-500">Notes:</span>
              <p class="mt-1 text-sm text-gray-700">{{ spiscApplication.eligibility_notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- No Application Data -->
    <div v-else-if="!loading" class="bg-gray-50 border border-gray-200 rounded-lg p-6">
      <p class="text-gray-600 text-center">No detailed application data available.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
  requestName: {
    type: String,
    required: true
  },
  applicationDoctype: {
    type: String,
    default: null
  },
  applicationName: {
    type: String,
    default: null
  }
})

const loading = ref(false)
const rcApplication = ref(null)
const spiscApplication = ref(null)

onMounted(() => {
  fetchApplicationData()
})

watch(() => [props.applicationDoctype, props.applicationName], () => {
  fetchApplicationData()
})

async function fetchApplicationData() {
  if (!props.applicationDoctype || !props.applicationName) {
    return
  }

  loading.value = true
  try {
    const data = await call('frappe.client.get', {
      doctype: props.applicationDoctype,
      name: props.applicationName
    })

    if (props.applicationDoctype === 'Resource Consent Application') {
      rcApplication.value = data
    } else if (props.applicationDoctype === 'SPISC Application') {
      spiscApplication.value = data
    }
  } catch (error) {
    console.error('[EnhancedApplicationReview] Error fetching application:', error)
  } finally {
    loading.value = false
  }
}

function activityStatusClass(status) {
  const classes = {
    'Permitted': 'bg-green-100 text-green-800',
    'Controlled': 'bg-blue-100 text-blue-800',
    'Restricted Discretionary': 'bg-yellow-100 text-yellow-800',
    'Discretionary': 'bg-orange-100 text-orange-800',
    'Non-Complying': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

function getApprovalCount() {
  if (!rcApplication.value || !rcApplication.value.affected_parties) return 0
  return rcApplication.value.affected_parties.filter(p => p.has_written_approval).length
}

function getWordCount(text) {
  if (!text) return 0
  return text.split(/\s+/).filter(word => word.length > 0).length
}

function getExcerpt(text, maxChars) {
  if (!text) return ''
  if (text.length <= maxChars) return text
  return text.substring(0, maxChars) + '...'
}
</script>

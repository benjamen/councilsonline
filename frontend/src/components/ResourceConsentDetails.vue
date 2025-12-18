<template>
  <div v-if="rcApplication.data" class="space-y-6">
    <!-- Consent Details -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Resource Consent Details</h3>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <dt class="text-sm font-medium text-gray-600">Consent Type</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.data.consent_types || 'N/A' }}</dd>
        </div>

        <div>
          <dt class="text-sm font-medium text-gray-600">Activity Status</dt>
          <dd class="mt-1">
            <span :class="getActivityStatusClass(rcApplication.data.activity_status)" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
              {{ rcApplication.data.activity_status || 'N/A' }}
            </span>
          </dd>
        </div>
      </div>
    </div>

    <!-- Assessment of Effects -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Assessment of Environmental Effects</h3>

      <div class="prose prose-sm max-w-none">
        <div v-html="rcApplication.data.assessment_of_effects || '<p class=\'text-gray-500\'>No AEE provided</p>'"></div>
      </div>

      <div v-if="hasDetailedEffects" class="mt-4 pt-4 border-t border-gray-200">
        <h4 class="text-sm font-semibold text-gray-900 mb-3">Detailed Effects Breakdown</h4>

        <div class="space-y-3">
          <div v-if="rcApplication.data.effects_on_people">
            <dt class="text-xs font-medium text-gray-600">Effects on People</dt>
            <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.effects_on_people"></dd>
          </div>

          <div v-if="rcApplication.data.physical_effects">
            <dt class="text-xs font-medium text-gray-600">Physical Effects</dt>
            <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.physical_effects"></dd>
          </div>

          <div v-if="rcApplication.data.ecosystem_effects">
            <dt class="text-xs font-medium text-gray-600">Ecosystem Effects</dt>
            <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.ecosystem_effects"></dd>
          </div>

          <div v-if="rcApplication.data.cultural_effects">
            <dt class="text-xs font-medium text-gray-600">Cultural/Heritage Effects</dt>
            <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.cultural_effects"></dd>
          </div>
        </div>
      </div>
    </div>

    <!-- Planning Assessment -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Planning Assessment</h3>

      <div class="prose prose-sm max-w-none">
        <div v-html="rcApplication.data.planning_assessment || '<p class=\'text-gray-500\'>No planning assessment provided</p>'"></div>
      </div>

      <div v-if="rcApplication.data.alternatives_considered || rcApplication.data.mitigation_proposed" class="mt-4 pt-4 border-t border-gray-200 space-y-3">
        <div v-if="rcApplication.data.alternatives_considered">
          <dt class="text-sm font-medium text-gray-600">Alternatives Considered</dt>
          <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.alternatives_considered"></dd>
        </div>

        <div v-if="rcApplication.data.mitigation_proposed">
          <dt class="text-sm font-medium text-gray-600">Mitigation Measures</dt>
          <dd class="mt-1 text-sm text-gray-900" v-html="rcApplication.data.mitigation_proposed"></dd>
        </div>
      </div>
    </div>

    <!-- Affected Parties -->
    <div v-if="rcApplication.data.affected_parties && rcApplication.data.affected_parties.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">
        Affected Parties
        <span class="ml-2 text-sm font-normal text-gray-500">({{ rcApplication.data.affected_parties.length }})</span>
      </h3>

      <div class="space-y-2">
        <div v-for="(party, index) in rcApplication.data.affected_parties" :key="index" class="p-3 bg-gray-50 rounded-lg">
          <p class="text-sm font-medium text-gray-900">{{ party.party_name }}</p>
          <p class="text-xs text-gray-500">{{ party.address }}</p>
          <p v-if="party.written_approval_obtained" class="text-xs text-green-600 mt-1">✓ Written approval obtained</p>
        </div>
      </div>

      <div class="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
        <span class="font-medium">{{ rcApplication.data.written_approvals_obtained || 0 }}</span> of {{ rcApplication.data.affected_parties.length }} approvals obtained
      </div>
    </div>

    <!-- Iwi Consultation -->
    <div v-if="rcApplication.data.iwi_consultation_undertaken" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Iwi Consultation</h3>

      <div class="space-y-3">
        <div>
          <dt class="text-sm font-medium text-gray-600">Iwi/Hapū Consulted</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.data.iwi_consulted || 'Not specified' }}</dd>
        </div>

        <div v-if="rcApplication.data.iwi_response_summary">
          <dt class="text-sm font-medium text-gray-600">Response Summary</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ rcApplication.data.iwi_response_summary }}</dd>
        </div>

        <div v-if="rcApplication.data.cultural_impact_assessment">
          <dt class="text-sm font-medium text-gray-600">Cultural Impact Assessment</dt>
          <dd class="mt-1">
            <a :href="rcApplication.data.cultural_impact_assessment" target="_blank" class="text-sm text-blue-600 hover:text-blue-800 underline">
              View CIA Document
            </a>
          </dd>
        </div>
      </div>
    </div>

    <!-- Specialist Reports -->
    <div v-if="rcApplication.data.specialist_reports && rcApplication.data.specialist_reports.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">
        Specialist Reports
        <span class="ml-2 text-sm font-normal text-gray-500">({{ rcApplication.data.specialist_reports.length }})</span>
      </h3>

      <div class="space-y-2">
        <div v-for="(report, index) in rcApplication.data.specialist_reports" :key="index" class="p-3 bg-gray-50 rounded-lg">
          <p class="text-sm font-medium text-gray-900">{{ report.report_type }}</p>
          <p class="text-xs text-gray-500">
            {{ report.specialist_name }}
            <span v-if="report.date_prepared"> | {{ formatDate(report.date_prepared) }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Proposed Conditions -->
    <div v-if="rcApplication.data.proposed_conditions" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Proposed Conditions</h3>

      <div class="prose prose-sm max-w-none">
        <div v-html="rcApplication.data.proposed_conditions"></div>
      </div>
    </div>
  </div>

  <div v-else-if="rcApplication.loading" class="text-center py-12">
    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    <p class="mt-2 text-sm text-gray-500">Loading Resource Consent details...</p>
  </div>

  <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
    <p class="text-gray-500">No Resource Consent Application data available</p>
  </div>
</template>

<script setup>
import { createResource } from "frappe-ui"
import { computed } from "vue"

const props = defineProps({
	requestId: {
		type: String,
		required: true,
	},
})

// Fetch RC Application data with child tables
// Note: We use the request ID as the name since RC Application uses "By fieldname" naming with "request" field
const rcApplication = createResource({
	url: "frappe.client.get",
	params: {
		doctype: "Resource Consent Application",
		name: props.requestId,
	},
	auto: true,
})

const hasDetailedEffects = computed(() => {
	if (!rcApplication.data) return false
	return !!(
		rcApplication.data.effects_on_people ||
		rcApplication.data.physical_effects ||
		rcApplication.data.ecosystem_effects ||
		rcApplication.data.cultural_effects
	)
})

const getActivityStatusClass = (status) => {
	const statusClasses = {
		Controlled: "bg-blue-100 text-blue-800",
		"Restricted Discretionary": "bg-yellow-100 text-yellow-800",
		Discretionary: "bg-orange-100 text-orange-800",
		"Non-Complying": "bg-red-100 text-red-800",
	}
	return statusClasses[status] || "bg-gray-100 text-gray-800"
}

const formatDate = (date) => {
	if (!date) return "N/A"
	return new Date(date).toLocaleDateString("en-NZ", {
		day: "numeric",
		month: "short",
		year: "numeric",
	})
}
</script>

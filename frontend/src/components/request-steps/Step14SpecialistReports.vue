<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Specialist Reports</h2>
    <p class="text-gray-600 mb-8">Upload any specialist reports or assessments supporting your application</p>

    <div class="space-y-6">
      <!-- Info Box -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">About Specialist Reports</h5>
            <p class="text-blue-800 text-sm mt-1">
              Upload any specialist assessments, technical reports, or expert opinions that support your application.
              These might include traffic assessments, acoustic reports, ecological surveys, geotechnical reports, etc.
            </p>
          </div>
        </div>
      </div>

      <!-- Specialist Reports List -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Uploaded Specialist Reports</h3>
        </div>

        <div class="p-6">
          <p class="text-sm text-gray-600 mb-4">
            Use the Attachments section in the main application form to upload specialist reports.
            Reports will automatically appear here once uploaded with the appropriate category.
          </p>

          <div v-if="specialistReports.length > 0" class="space-y-3">
            <div
              v-for="(report, index) in specialistReports"
              :key="index"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50 flex items-start"
            >
              <svg class="w-6 h-6 text-blue-600 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="flex-1">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">{{ report.document_type || 'Specialist Report' }}</p>
                    <p v-if="report.description" class="text-sm text-gray-600 mt-1">{{ report.description }}</p>
                    <p v-if="report.file" class="text-xs text-gray-500 mt-1">{{ report.file.name }}</p>
                  </div>
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                    {{ report.document_category }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-2 text-sm text-gray-500">No specialist reports uploaded yet</p>
            <p class="text-sm text-gray-500">Add reports in the Attachments section if required</p>
          </div>
        </div>
      </div>

      <!-- Common Report Types -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Common Specialist Report Types</h3>
        </div>

        <div class="p-6">
          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Traffic & Transportation</p>
                <p class="text-xs text-gray-600">Traffic impact assessments, parking demand studies</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Acoustic Reports</p>
                <p class="text-xs text-gray-600">Noise assessments, sound insulation reports</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Ecological Assessments</p>
                <p class="text-xs text-gray-600">Biodiversity surveys, vegetation reports</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Geotechnical Reports</p>
                <p class="text-xs text-gray-600">Soil investigations, slope stability assessments</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Landscape & Visual</p>
                <p class="text-xs text-gray-600">Visual impact assessments, landscape plans</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Engineering Reports</p>
                <p class="text-xs text-gray-600">Structural, civil, stormwater assessments</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Archaeological Surveys</p>
                <p class="text-xs text-gray-600">Heritage assessments, archaeological reports</p>
              </div>
            </div>

            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
              <div>
                <p class="font-medium text-sm text-gray-900">Economic Assessments</p>
                <p class="text-xs text-gray-600">Economic impact analyses, cost-benefit studies</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Guidance -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-yellow-900 text-sm">When Are Specialist Reports Required?</h5>
            <ul class="text-yellow-800 text-sm mt-2 space-y-1 list-disc list-inside">
              <li>Council may request specific reports based on the nature and scale of your proposal</li>
              <li>Check the district/regional plan for assessment requirements</li>
              <li>Reports should be prepared by qualified professionals</li>
              <li>Ensure reports address the specific effects of your proposal</li>
              <li>Consider pre-application advice to confirm what reports may be needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

// Filter attachments that are specialist reports
const specialistReports = computed(() => {
  if (!props.modelValue.attachments) return []

  const reportCategories = [
    'Specialist Report',
    'Technical Report',
    'Assessment Report',
    'Engineering Report',
    'Environmental Report'
  ]

  return props.modelValue.attachments.filter(att =>
    reportCategories.some(category =>
      att.document_category?.includes(category) ||
      att.document_type?.includes('Report') ||
      att.document_type?.includes('Assessment')
    )
  )
})
</script>

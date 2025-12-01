<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">National Environmental Standards Assessment</h2>
    <p class="text-gray-600 mb-8">Determine which NES may apply to your proposal (RMA Regulations)</p>

    <div class="space-y-8">
      <!-- NES Screening Checkboxes (FRD 5.1) -->
      <div>
        <h3 class="text-lg font-semibold text-gray-900 mb-4">NES Screening</h3>
        <p class="text-sm text-gray-600 mb-4">
          Select all National Environmental Standards that may be triggered by your proposal. This initial screening helps determine compliance requirements.
        </p>

        <div class="space-y-3">
          <div
            v-for="nes in nesTypes"
            :key="nes.value"
            role="checkbox"
            :aria-checked="getNESData(nes.value).applies"
            :aria-label="`${nes.label} - Click to toggle applicability`"
            :tabindex="0"
            class="border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
            :class="getNESData(nes.value).applies ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
            @click="toggleNES(nes.value)"
            @keydown.space.prevent="toggleNES(nes.value)"
            @keydown.enter.prevent="toggleNES(nes.value)"
          >
            <div class="flex items-start">
              <input
                type="checkbox"
                :checked="getNESData(nes.value).applies"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none"
                readonly
                aria-hidden="true"
              />
              <div class="ml-3 flex-1">
                <h4 class="text-base font-semibold text-gray-900">{{ nes.label }}</h4>
                <p v-if="nes.description" class="text-xs text-gray-600 mt-1">{{ nes.description }}</p>

                <!-- Expandable details when checked -->
                <div v-if="getNESData(nes.value).applies" class="mt-3 space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Description / Compliance Status</label>
                    <textarea
                      v-model="getNESData(nes.value).description"
                      @click.stop
                      rows="3"
                      placeholder="Describe how this NES applies and how you will comply..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    ></textarea>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Compliance Notes</label>
                    <textarea
                      v-model="getNESData(nes.value).compliance_notes"
                      @click.stop
                      rows="2"
                      placeholder="Additional compliance notes or assessment..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- HAIL Questionnaire (FRD 5.2-5.5) - Only show if Contaminated Soil selected -->
      <div v-if="isContaminatedSoilSelected" class="border-t border-gray-200 pt-8">
        <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h5 class="font-semibold text-blue-900 text-sm">HAIL Assessment Required</h5>
              <p class="text-blue-800 text-sm mt-1">
                Since your site may involve contaminants in soil, you must complete the Hazardous Activities and Industries List (HAIL) assessment below.
              </p>
            </div>
          </div>
        </div>

        <h3 class="text-lg font-semibold text-gray-900 mb-4">HAIL Activities Assessment</h3>
        <p class="text-sm text-gray-600 mb-4">
          Identify any current or historical Hazardous Activities and Industries List (HAIL) activities on the site.
        </p>

        <!-- Add HAIL Activity Button -->
        <div class="flex justify-between items-center mb-4">
          <p class="text-sm text-gray-700">
            Add all HAIL activities that have occurred on this site (current or historical)
          </p>
          <button
            @click="showHAILModal = true"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add HAIL Activity
          </button>
        </div>

        <!-- HAIL Activities List -->
        <div v-if="localData.hail_activities && localData.hail_activities.length > 0" class="space-y-3 mb-6">
          <div
            v-for="(activity, index) in localData.hail_activities"
            :key="index"
            class="border border-gray-200 rounded-lg p-4 bg-white flex justify-between items-center"
          >
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ activity.activity_category }}</div>
              <div class="text-sm text-gray-600 mt-1">{{ activity.activity_description }}</div>
              <div v-if="activity.time_period" class="text-xs text-gray-500 mt-1">Time period: {{ activity.time_period }}</div>
            </div>
            <div class="flex gap-2">
              <button
                @click="editHAIL(index)"
                type="button"
                class="text-blue-600 hover:text-blue-800 p-1"
                title="Edit"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click="removeHAIL(index)"
                type="button"
                class="text-red-600 hover:text-red-800 p-1"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State for HAIL -->
        <div v-else class="text-center py-6 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 mb-6">
          <svg class="mx-auto h-10 w-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">No HAIL activities identified</p>
          <p class="text-xs text-gray-500 mt-1">Click "Add HAIL Activity" to document any hazardous activities on this site</p>
        </div>

        <!-- Soil Contamination Assessment -->
        <div class="border-t border-gray-200 pt-6">
          <h4 class="text-base font-semibold text-gray-900 mb-3">Soil Contamination Assessment</h4>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Has a Preliminary Site Investigation (PSI) or Detailed Site Investigation (DSI) been completed?
            </label>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input
                  v-model="localData.soil_investigation_completed"
                  type="radio"
                  :value="true"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Yes</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="localData.soil_investigation_completed"
                  type="radio"
                  :value="false"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">No</span>
              </label>
            </div>
          </div>

          <div v-if="localData.soil_investigation_completed" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Investigation Summary</label>
              <textarea
                v-model="localData.soil_investigation_summary"
                rows="3"
                placeholder="Summarize the key findings from the PSI/DSI..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Upload Investigation Report</label>
              <input
                type="file"
                @change="handleSoilReportUpload"
                accept=".pdf,.doc,.docx"
                class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200"
              />
              <p v-if="localData.soil_investigation_document" class="text-xs text-green-600 mt-1">
                ✓ Document uploaded: {{ localData.soil_investigation_document }}
              </p>
              <p class="mt-1 text-xs text-gray-500">PDF or Word documents only (max 10MB)</p>
            </div>
          </div>
        </div>
      </div>

      <!-- No NES Selected Confirmation -->
      <div v-if="!hasAnyNESSelected" class="border-t border-gray-200 pt-6">
        <div class="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <label class="flex items-start cursor-pointer">
            <input
              v-model="localData.no_nes_confirmed"
              type="checkbox"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900">I confirm that no National Environmental Standards apply to this proposal</span>
              <p class="text-xs text-gray-600 mt-1">
                By checking this box, I confirm that I have reviewed all NES regulations and none are triggered by this activity.
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>

    <!-- HAIL Activity Modal -->
    <Teleport to="body">
      <div
        v-if="showHAILModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeHAILModal"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingHAILIndex !== null ? 'Edit HAIL Activity' : 'Add HAIL Activity' }}
            </h3>
            <button
              @click="closeHAILModal"
              type="button"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Activity Category *</label>
              <select
                v-model="hailForm.activity_category"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select category</option>
                <option v-for="category in hailCategories" :key="category" :value="category">{{ category }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Activity Description *</label>
              <textarea
                v-model="hailForm.activity_description"
                rows="3"
                required
                placeholder="Describe the specific HAIL activity that occurred on this site..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
              <input
                v-model="hailForm.time_period"
                type="text"
                placeholder="e.g., 1950-1985, Current, Historical"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Potential Contaminants</label>
              <input
                v-model="hailForm.contaminants"
                type="text"
                placeholder="e.g., Heavy metals, Petroleum hydrocarbons, Asbestos"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                v-model="hailForm.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select status</option>
                <option value="Current">Current - still operating</option>
                <option value="Historical">Historical - no longer operating</option>
                <option value="Remediated">Remediated - site cleaned up</option>
              </select>
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
            <button
              @click="closeHAILModal"
              type="button"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="saveHAIL"
              type="button"
              :disabled="!isHAILFormValid"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ editingHAILIndex !== null ? 'Update' : 'Add' }} Activity
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, reactive, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// NES Types with FRD descriptions (FRD Section 5.1)
const nesTypes = [
  {
    value: 'Contaminated Soil (HAIL)',
    label: 'NES for Assessing and Managing Contaminants in Soil (HAIL)',
    description: 'Applies if site has had hazardous activities or industries'
  },
  {
    value: 'Air Quality',
    label: 'NES for Air Quality',
    description: 'Regulates emissions and ambient air quality standards'
  },
  {
    value: 'Drinking Water',
    label: 'NES for Sources of Human Drinking Water',
    description: 'Protects drinking water sources from contamination'
  },
  {
    value: 'Freshwater',
    label: 'NES for Freshwater Management',
    description: 'Regulates activities affecting lakes, rivers, wetlands, and aquifers'
  },
  {
    value: 'Plantation Forestry',
    label: 'NES for Plantation Forestry',
    description: 'Applies to commercial forestry operations'
  },
  {
    value: 'Electricity Transmission',
    label: 'NES for Electricity Transmission Activities',
    description: 'Regulates high-voltage transmission lines and infrastructure'
  },
  {
    value: 'Telecommunications',
    label: 'NES for Telecommunication Facilities',
    description: 'Applies to cell towers and telecommunication infrastructure'
  },
  {
    value: 'Other',
    label: 'Other NES',
    description: 'Any other relevant National Environmental Standard'
  }
]

// HAIL Categories (NES Soil Contaminants)
const hailCategories = [
  'Agriculture - Persistent Pesticide Use',
  'Agriculture - Fertiliser Manufacturing/Storage',
  'Chemicals - Manufacturing/Formulation',
  'Fuel Storage - Petrol Station',
  'Fuel Storage - Bulk Fuel Storage',
  'Gas Works',
  'Landfill/Waste Disposal',
  'Metal Treatment - Electroplating/Galvanizing',
  'Mining/Quarrying',
  'Railway Yards',
  'Sheep Dip',
  'Timber Treatment',
  'Other Industrial Activity'
]

// Initialize NES data structure if not exists
if (!localData.value.nes_items) {
  const updatedData = { ...props.modelValue }
  updatedData.nes_items = []
  emit('update:modelValue', updatedData)
}

// Reactive NES data storage
const nesData = reactive({})

const getNESData = (nesType) => {
  if (!nesData[nesType]) {
    // Check if data exists in modelValue
    const existing = localData.value.nes_items?.find(item => item.nes_type === nesType)
    if (existing) {
      nesData[nesType] = { ...existing }
    } else {
      nesData[nesType] = {
        nes_type: nesType,
        applies: false,
        description: '',
        compliance_notes: ''
      }
    }
  }
  return nesData[nesType]
}

const toggleNES = (nesType) => {
  const data = getNESData(nesType)
  data.applies = !data.applies

  // Sync to modelValue
  const updatedData = { ...props.modelValue }
  if (!updatedData.nes_items) updatedData.nes_items = []

  const existingIndex = updatedData.nes_items.findIndex(item => item.nes_type === nesType)

  if (data.applies) {
    if (existingIndex >= 0) {
      updatedData.nes_items[existingIndex] = { ...data }
    } else {
      updatedData.nes_items.push({ ...data })
    }
  } else {
    if (existingIndex >= 0) {
      updatedData.nes_items.splice(existingIndex, 1)
    }
  }

  // Clear no_nes_confirmed if user selects any NES
  if (data.applies) {
    updatedData.no_nes_confirmed = false
  }

  emit('update:modelValue', updatedData)
}

// Check if Contaminated Soil (HAIL) is selected
const isContaminatedSoilSelected = computed(() => {
  return localData.value.nes_items?.some(item =>
    item.nes_type === 'Contaminated Soil (HAIL)' && item.applies
  ) || false
})

// Check if any NES is selected
const hasAnyNESSelected = computed(() => {
  return localData.value.nes_items?.some(item => item.applies) || false
})

// HAIL Modal Management
const showHAILModal = ref(false)
const editingHAILIndex = ref(null)
const hailForm = reactive({
  activity_category: '',
  activity_description: '',
  time_period: '',
  contaminants: '',
  status: ''
})

const resetHAILForm = () => {
  hailForm.activity_category = ''
  hailForm.activity_description = ''
  hailForm.time_period = ''
  hailForm.contaminants = ''
  hailForm.status = ''
}

const editHAIL = (index) => {
  editingHAILIndex.value = index
  const activity = localData.value.hail_activities[index]
  Object.assign(hailForm, activity)
  showHAILModal.value = true
}

const removeHAIL = (index) => {
  if (confirm('Remove this HAIL activity?')) {
    const updatedData = { ...props.modelValue }
    updatedData.hail_activities.splice(index, 1)
    emit('update:modelValue', updatedData)
  }
}

const isHAILFormValid = computed(() => {
  return !!(hailForm.activity_category && hailForm.activity_description?.trim())
})

const saveHAIL = () => {
  if (!isHAILFormValid.value) return

  const updatedData = { ...props.modelValue }
  if (!updatedData.hail_activities) {
    updatedData.hail_activities = []
  }

  const activityData = {
    activity_category: hailForm.activity_category,
    activity_description: hailForm.activity_description,
    time_period: hailForm.time_period,
    contaminants: hailForm.contaminants,
    status: hailForm.status
  }

  if (editingHAILIndex.value !== null) {
    updatedData.hail_activities[editingHAILIndex.value] = activityData
  } else {
    updatedData.hail_activities.push(activityData)
  }

  emit('update:modelValue', updatedData)
  closeHAILModal()
}

const closeHAILModal = () => {
  showHAILModal.value = false
  editingHAILIndex.value = null
  resetHAILForm()
}

// Soil investigation file upload
const handleSoilReportUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      alert('File size exceeds 10MB. Please upload a smaller file.')
      event.target.value = ''
      return
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Please upload a PDF or Word document.')
      event.target.value = ''
      return
    }

    // File upload will be handled by the parent component
    emit('update:modelValue', {
      ...props.modelValue,
      soil_investigation_document: file.name
    })
  }
}
</script>

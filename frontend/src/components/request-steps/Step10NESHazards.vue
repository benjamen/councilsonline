<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">National Environmental Standards & Natural Hazards</h2>
    <p class="text-gray-600 mb-8">Assess compliance with NES and identify natural hazards</p>

    <div class="space-y-8">
      <!-- National Environmental Standards -->
      <div>
        <h3 class="text-xl font-semibold text-gray-900 mb-4">National Environmental Standards (NES)</h3>
        <p class="text-sm text-gray-600 mb-4">
          Indicate which NES may apply to your proposal and confirm compliance
        </p>

        <div class="space-y-3">
          <div
            v-for="nes in nesTypes"
            :key="nes.value"
            class="border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md"
            :class="getNESData(nes.value).applies ? 'border-blue-600 bg-blue-50' : 'border-gray-200'"
            @click="toggleNES(nes.value)"
          >
            <div class="flex items-start">
              <input
                type="checkbox"
                :checked="getNESData(nes.value).applies"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded pointer-events-none"
                readonly
              />
              <div class="ml-3 flex-1">
                <h4 class="text-base font-semibold text-gray-900">{{ nes.label }}</h4>

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

      <!-- Natural Hazards (RMA s104) -->
      <div class="border-t border-gray-200 pt-8">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Natural Hazards (RMA s104)</h3>
        <p class="text-sm text-gray-600 mb-4">
          Under s104(1)(c) RMA, councils must consider the risk of natural hazards. Identify any hazards that may affect the site.
        </p>

        <!-- Add Hazard Button -->
        <div class="flex justify-between items-center mb-4">
          <p class="text-sm text-gray-700">
            Select hazard types that may affect your site and describe mitigation measures
          </p>
          <button
            @click="addHazard"
            type="button"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Natural Hazard
          </button>
        </div>

        <!-- Hazards List -->
        <div v-if="localData.natural_hazards && localData.natural_hazards.length > 0" class="space-y-4">
          <div
            v-for="(hazard, index) in localData.natural_hazards"
            :key="index"
            class="border border-gray-200 rounded-lg p-4 bg-white"
          >
            <div class="flex justify-between items-start mb-4">
              <h4 class="text-base font-semibold text-gray-900">
                Hazard #{{ index + 1 }}
              </h4>
              <button
                @click="removeHazard(index)"
                type="button"
                class="text-red-600 hover:text-red-800 p-1"
                title="Remove"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Hazard Type *</label>
                <select
                  v-model="hazard.hazard_type"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select hazard type</option>
                  <option value="Earthquake">Earthquake</option>
                  <option value="Fire">Fire</option>
                  <option value="Tsunami">Tsunami</option>
                  <option value="Erosion">Erosion</option>
                  <option value="Volcanic">Volcanic & Geothermal</option>
                  <option value="Flood">Flood</option>
                  <option value="Sedimentation">Sedimentation</option>
                  <option value="Subsidence">Subsidence</option>
                  <option value="Wind">Wind</option>
                  <option value="Landslip">Landslip</option>
                  <option value="Drought">Drought</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
                <select
                  v-model="hazard.risk_level"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select risk level</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>

            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Mitigation Measures</label>
              <textarea
                v-model="hazard.mitigation_measures"
                rows="3"
                placeholder="Describe mitigation measures to address this hazard (design features, engineering solutions, management plans)..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">No natural hazards identified</p>
          <p class="text-xs text-gray-500 mt-1">Click "Add Natural Hazard" if any hazards may affect the site</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, reactive } from 'vue'

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

// NES Types matching backend schema
const nesTypes = [
  { value: 'Contaminated Soil (HAIL)', label: 'NES for Assessing and Managing Contaminants in Soil (HAIL)' },
  { value: 'Air Quality', label: 'NES for Air Quality' },
  { value: 'Drinking Water', label: 'NES for Sources of Human Drinking Water' },
  { value: 'Freshwater', label: 'NES for Freshwater Management' },
  { value: 'Plantation Forestry', label: 'NES for Plantation Forestry' },
  { value: 'Electricity Transmission', label: 'NES for Electricity Transmission Activities' },
  { value: 'Telecommunications', label: 'NES for Telecommunication Facilities' },
  { value: 'Other', label: 'Other NES' }
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

  emit('update:modelValue', updatedData)
}

const addHazard = () => {
  const updatedData = { ...props.modelValue }
  if (!updatedData.natural_hazards) {
    updatedData.natural_hazards = []
  }
  updatedData.natural_hazards.push({
    hazard_type: '',
    risk_level: '',
    mitigation_measures: ''
  })
  emit('update:modelValue', updatedData)
}

const removeHazard = (index) => {
  if (confirm('Remove this natural hazard?')) {
    const updatedData = { ...props.modelValue }
    updatedData.natural_hazards.splice(index, 1)
    emit('update:modelValue', updatedData)
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Proposal Details</h2>
    <p class="text-gray-600 mb-8">Describe your proposed activity in detail</p>

    <div class="space-y-6">
      <!-- Add Proposal Detail Button -->
      <div class="flex justify-between items-center">
        <p class="text-sm text-gray-700">
          Add details about different aspects of your proposal (building, earthworks, traffic, etc.)
        </p>
        <button
          @click="addProposalDetail"
          type="button"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Proposal Detail
        </button>
      </div>

      <!-- Proposal Details List -->
      <div v-if="modelValue.proposal_details && modelValue.proposal_details.length > 0" class="space-y-4">
        <div
          v-for="(detail, index) in modelValue.proposal_details"
          :key="index"
          class="border border-gray-200 rounded-lg p-6 bg-white shadow-sm"
        >
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ detail.detail_type || 'Proposal Detail' }} #{{ index + 1 }}
            </h3>
            <button
              @click="removeProposalDetail(index)"
              type="button"
              class="text-red-600 hover:text-red-800 p-1"
              title="Remove"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <!-- Detail Type Selector -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Detail Type *
            </label>
            <select
              v-model="detail.detail_type"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select type</option>
              <option value="Building">Building</option>
              <option value="Earthworks">Earthworks</option>
              <option value="Traffic">Traffic & Parking</option>
              <option value="Operations">Operations</option>
              <option value="Subdivision">Subdivision</option>
              <option value="Discharge">Discharge</option>
              <option value="Water">Water Take/Use</option>
              <option value="Coastal">Coastal Activity</option>
            </select>
          </div>

          <!-- Building Details -->
          <div v-if="detail.detail_type === 'Building'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Building Details</h4>
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Building Height (m)</label>
                <input
                  v-model.number="detail.building_height_m"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 8.5"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Total Floor Area (m²)</label>
                <input
                  v-model.number="detail.total_floor_area_m2"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 250.5"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Earthworks Details -->
          <div v-if="detail.detail_type === 'Earthworks'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Earthworks Details</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="detail.earthworks_description"
                rows="4"
                placeholder="Describe the earthworks proposed..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>

          <!-- Traffic Details -->
          <div v-if="detail.detail_type === 'Traffic'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Traffic & Parking Details</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="detail.traffic_description"
                rows="4"
                placeholder="Describe traffic generation, parking provision, access arrangements..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>

          <!-- Operations Details -->
          <div v-if="detail.detail_type === 'Operations'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Operations Details</h4>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="detail.operations_description"
                rows="4"
                placeholder="Describe hours of operation, activities, processes..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
          </div>

          <!-- Subdivision Details -->
          <div v-if="detail.detail_type === 'Subdivision'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Subdivision Details</h4>
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Number of Lots</label>
                <input
                  v-model.number="detail.subdivision_lots"
                  type="number"
                  placeholder="e.g., 5"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Lot Sizes</label>
                <input
                  v-model="detail.subdivision_lot_sizes"
                  type="text"
                  placeholder="e.g., 800m², 1000m², 1200m²"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          <!-- Discharge Details -->
          <div v-if="detail.detail_type === 'Discharge'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Discharge Details</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Discharge Type</label>
                <select
                  v-model="detail.discharge_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select type</option>
                  <option value="Stormwater">Stormwater</option>
                  <option value="Wastewater">Wastewater</option>
                  <option value="Air">Air</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Receiving Environment</label>
                <input
                  v-model="detail.discharge_receiver"
                  type="text"
                  placeholder="e.g., Reticulated network, stream, land"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Treatment System</label>
                <textarea
                  v-model="detail.discharge_treatment"
                  rows="3"
                  placeholder="Describe treatment systems and methods..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Water Details -->
          <div v-if="detail.detail_type === 'Water'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Water Take/Use Details</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Water Source</label>
                <input
                  v-model="detail.water_source"
                  type="text"
                  placeholder="e.g., River, bore, stream"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Maximum Take (m³/day)</label>
                  <input
                    v-model.number="detail.water_max_take_m3"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 50"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Rate</label>
                  <input
                    v-model="detail.water_rate"
                    type="text"
                    placeholder="e.g., 2 L/s"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Coastal Details -->
          <div v-if="detail.detail_type === 'Coastal'" class="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900">Coastal Activity Details</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Structure Type</label>
                <input
                  v-model="detail.coastal_structure_type"
                  type="text"
                  placeholder="e.g., Jetty, mooring, seawall"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Navigation Effects</label>
                <textarea
                  v-model="detail.coastal_navigation_effects"
                  rows="3"
                  placeholder="Describe potential effects on navigation..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm text-gray-600">No proposal details added yet</p>
        <p class="text-xs text-gray-500 mt-1">Click "Add Proposal Detail" to describe your proposed activity</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const addProposalDetail = () => {
  const updatedData = { ...props.modelValue }
  if (!updatedData.proposal_details) {
    updatedData.proposal_details = []
  }
  updatedData.proposal_details.push({
    detail_type: '',
    building_height_m: null,
    total_floor_area_m2: null,
    earthworks_description: '',
    traffic_description: '',
    operations_description: '',
    subdivision_lots: null,
    subdivision_lot_sizes: '',
    discharge_type: '',
    discharge_receiver: '',
    discharge_treatment: '',
    water_source: '',
    water_max_take_m3: null,
    water_rate: '',
    coastal_structure_type: '',
    coastal_navigation_effects: ''
  })
  emit('update:modelValue', updatedData)
}

const removeProposalDetail = (index) => {
  if (confirm('Remove this proposal detail?')) {
    const updatedData = { ...props.modelValue }
    updatedData.proposal_details.splice(index, 1)
    emit('update:modelValue', updatedData)
  }
}
</script>

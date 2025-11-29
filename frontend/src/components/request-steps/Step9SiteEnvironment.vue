<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Site & Environment</h2>
    <p class="text-gray-600 mb-8">Describe the site and existing environment</p>

    <div class="space-y-6">
      <!-- Site Information -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Site Information</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Site Area (m²)</label>
            <input
              v-model.number="localData.site_area_m2"
              type="number"
              step="0.1"
              placeholder="e.g., 800"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Current Use</label>
            <input
              v-model="localData.current_use"
              type="text"
              placeholder="e.g., Residential dwelling"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- Planning Context -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Planning Context</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Zoning</label>
            <input
              v-model="localData.zoning"
              type="text"
              placeholder="e.g., Residential, Rural, Mixed Use"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Overlays</label>
            <textarea
              v-model="localData.overlays"
              rows="2"
              placeholder="e.g., Heritage overlay, flood zone, outstanding natural landscape"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">List any planning overlays that apply to the site</p>
          </div>
        </div>
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Designations</label>
          <textarea
            v-model="localData.designations"
            rows="2"
            placeholder="e.g., Road designation, network utilities"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500">List any designations affecting the property</p>
        </div>
      </div>

      <!-- Site Description -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Site Description</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Site Topography</label>
            <textarea
              v-model="localData.site_topography"
              rows="4"
              placeholder="Describe the topography (flat, sloping, rolling, steep), aspect, elevation changes..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Existing Vegetation</label>
            <textarea
              v-model="localData.existing_vegetation"
              rows="4"
              placeholder="Describe vegetation on the site (lawns, gardens, mature trees, bush, etc.)"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>

          <div class="flex items-start">
            <input
              type="checkbox"
              v-model="localData.significant_vegetation"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label class="ml-3 text-sm font-medium text-gray-700">
              Significant Indigenous Vegetation Present
              <p class="text-xs text-gray-500 font-normal mt-1">Check if the site contains significant indigenous vegetation or habitats</p>
            </label>
          </div>
        </div>
      </div>

      <!-- Watercourses / Wetlands -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Watercourses / Wetlands</h3>
        <div class="space-y-4">
          <div class="flex items-start">
            <input
              type="checkbox"
              v-model="localData.watercourses_present"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label class="ml-3 text-sm font-medium text-gray-700">
              Watercourses or Wetlands Present
              <p class="text-xs text-gray-500 font-normal mt-1">Check if there are streams, rivers, wetlands, or water bodies on or adjacent to the site</p>
            </label>
          </div>

          <div v-if="localData.watercourses_present" class="pl-7">
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              v-model="localData.watercourses_description"
              rows="4"
              placeholder="Describe the watercourse/wetland (type, location, size, condition, flow characteristics)..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- HAIL Contamination Status -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">HAIL Contamination Status</h3>
        <p class="text-sm text-gray-600 mb-4">
          Hazardous Activities and Industries List (HAIL) - indicate if the site has been used for activities that may have caused contamination
        </p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">HAIL Status *</label>
            <select
              v-model="localData.hail_status"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select status</option>
              <option value="Not Applicable">Not Applicable - Site never used for HAIL activities</option>
              <option value="No Known Contamination">No Known Contamination - HAIL use but no evidence of contamination</option>
              <option value="Potential">Potential Contamination - HAIL use, contamination possible</option>
              <option value="Confirmed">Confirmed Contamination - Contamination identified</option>
            </select>
          </div>

          <div v-if="localData.hail_status === 'Potential' || localData.hail_status === 'Confirmed'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <h5 class="font-semibold text-yellow-900 text-sm">Contaminated Site Notice</h5>
                <p class="text-yellow-800 text-sm mt-1">
                  You may need a Preliminary or Detailed Site Investigation (PSI/DSI) by a qualified contaminated land specialist. Consult the council's environmental health team.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Existing Infrastructure -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Existing Infrastructure</h3>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Infrastructure Description</label>
          <textarea
            v-model="localData.existing_infrastructure"
            rows="4"
            placeholder="Describe existing infrastructure on the site (buildings, driveways, fences, services - water, wastewater, stormwater, power, telecommunications)..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

// Create a computed property for local data that syncs with parent
const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

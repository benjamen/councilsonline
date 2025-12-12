<template>
  <div class="space-y-4">
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-blue-900">Residential Address</h3>
          <p class="text-xs text-blue-700 mt-0.5">Please provide your complete address details</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Province -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Province
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <div class="relative">
          <select
            v-model="localAddress.province"
            @change="onProvinceChange"
            :required="required"
            class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg transition-all"
            :class="{'border-blue-500 ring-2 ring-blue-100': localAddress.province}"
          >
            <option value="">Select Province</option>
            <option v-for="province in provinces" :key="province" :value="province">
              {{ province }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Municipality/City -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Municipality/City
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <div class="relative">
          <select
            v-model="localAddress.municipality"
            @change="onMunicipalityChange"
            :required="required"
            :disabled="!localAddress.province"
            class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            :class="{'border-blue-500 ring-2 ring-blue-100': localAddress.municipality}"
          >
            <option value="">Select Municipality/City</option>
            <option v-for="municipality in municipalities" :key="municipality" :value="municipality">
              {{ municipality }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        <p v-if="!localAddress.province" class="mt-1 text-xs text-gray-500">Select province first</p>
      </div>

      <!-- Barangay -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Barangay
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <div class="relative">
          <select
            v-model="localAddress.barangay"
            @change="updateAddress"
            :required="required"
            :disabled="!localAddress.municipality"
            class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
            :class="{'border-blue-500 ring-2 ring-blue-100': localAddress.barangay}"
          >
            <option value="">Select Barangay</option>
            <option v-for="barangay in barangays" :key="barangay" :value="barangay">
              {{ barangay }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
        </div>
        <p v-if="!localAddress.municipality" class="mt-1 text-xs text-gray-500">Select municipality first</p>
      </div>

      <!-- Street Address -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Street / House No.
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          v-model="localAddress.street"
          @input="updateAddress"
          type="text"
          :required="required"
          placeholder="e.g., 123 Main Street, Blk 5 Lot 10"
          class="block w-full px-3 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
          :class="{'border-blue-500 ring-2 ring-blue-100': localAddress.street}"
        />
      </div>

      <!-- ZIP Code -->
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          ZIP Code
          <span class="text-gray-500 text-xs font-normal">(Optional)</span>
        </label>
        <input
          v-model="localAddress.zipCode"
          @input="updateAddress"
          type="text"
          placeholder="e.g., 1630"
          maxlength="4"
          class="block w-full px-3 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all max-w-xs"
        />
      </div>
    </div>

    <!-- Address Preview -->
    <div v-if="fullAddress" class="bg-green-50 border border-green-200 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-green-900">Complete Address</p>
          <p class="text-sm text-green-700 mt-1">{{ fullAddress }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Object],
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const localAddress = ref({
  street: '',
  barangay: '',
  municipality: '',
  province: '',
  zipCode: ''
})

// Philippines provinces (major ones - can be expanded)
const provinces = [
  'Metro Manila',
  'Rizal',
  'Cavite',
  'Laguna',
  'Bulacan',
  'Pampanga',
  'Batangas',
  'Quezon',
  'Cebu',
  'Davao del Sur',
  'Benguet',
  'Iloilo',
  'Negros Occidental',
  'Pangasinan',
  'Albay'
]

// Municipalities by province (can be expanded with API)
const municipalitiesData = {
  'Metro Manila': [
    'Manila City',
    'Quezon City',
    'Makati City',
    'Pasig City',
    'Taguig City',
    'Mandaluyong City',
    'Pasay City',
    'Parañaque City',
    'Las Piñas City',
    'Muntinlupa City',
    'Caloocan City',
    'Malabon City',
    'Navotas City',
    'Valenzuela City',
    'Marikina City',
    'San Juan City',
    'Pateros'
  ],
  'Rizal': [
    'Taytay',
    'Antipolo City',
    'Cainta',
    'Binangonan',
    'San Mateo',
    'Rodriguez (Montalban)',
    'Angono',
    'Cardona',
    'Jalajala',
    'Morong',
    'Pililla',
    'Tanay',
    'Teresa',
    'Baras'
  ],
  'Cavite': [
    'Bacoor City',
    'Cavite City',
    'Dasmarinas City',
    'Imus City',
    'Tagaytay City',
    'Trece Martires City',
    'General Trias',
    'Silang',
    'Kawit',
    'Noveleta',
    'Rosario',
    'Tanza',
    'Naic'
  ]
}

// Barangays by municipality (sample data - Taytay as example)
const barangaysData = {
  'Taytay': [
    'Dolores',
    'San Juan',
    'Muzon',
    'San Isidro',
    'Sta. Ana',
    'Poblacion',
    'Bagumbayan',
    'Bamban',
    'Calumpang',
    'Dalig',
    'Dolores',
    'San Juan',
    'Muzon'
  ],
  'Manila City': [
    'Ermita',
    'Intramuros',
    'Malate',
    'Paco',
    'Pandacan',
    'Port Area',
    'Quiapo',
    'Sampaloc',
    'San Andres',
    'San Miguel',
    'San Nicolas',
    'Santa Ana',
    'Santa Cruz',
    'Santa Mesa',
    'Tondo'
  ],
  'Quezon City': [
    'Bagong Pag-asa',
    'Bahay Toro',
    'Batasan Hills',
    'Commonwealth',
    'Cubao',
    'Fairview',
    'Kamuning',
    'Novaliches',
    'Project 4',
    'Tatalon',
    'Teacher\'s Village'
  ]
}

const municipalities = computed(() => {
  if (!localAddress.value.province) return []
  return municipalitiesData[localAddress.value.province] || []
})

const barangays = computed(() => {
  if (!localAddress.value.municipality) return []
  return barangaysData[localAddress.value.municipality] || ['Other - Please specify in Street field']
})

const fullAddress = computed(() => {
  const parts = []
  if (localAddress.value.street) parts.push(localAddress.value.street)
  if (localAddress.value.barangay) parts.push(`Brgy. ${localAddress.value.barangay}`)
  if (localAddress.value.municipality) parts.push(localAddress.value.municipality)
  if (localAddress.value.province) parts.push(localAddress.value.province)
  if (localAddress.value.zipCode) parts.push(localAddress.value.zipCode)

  return parts.length > 0 ? parts.join(', ') : ''
})

const onProvinceChange = () => {
  // Reset dependent fields when province changes
  localAddress.value.municipality = ''
  localAddress.value.barangay = ''
  updateAddress()
}

const onMunicipalityChange = () => {
  // Reset barangay when municipality changes
  localAddress.value.barangay = ''
  updateAddress()
}

const updateAddress = () => {
  // Emit both the full address string and individual fields
  emit('update:modelValue', {
    full_address: fullAddress.value,
    address_line: localAddress.value.street,
    barangay: localAddress.value.barangay,
    municipality: localAddress.value.municipality,
    province: localAddress.value.province,
    zip_code: localAddress.value.zipCode
  })
}

// Initialize from modelValue if provided
onMounted(() => {
  if (props.modelValue) {
    if (typeof props.modelValue === 'string') {
      // Try to parse string address
      // This is a simple parser - can be enhanced
      const parts = props.modelValue.split(',').map(p => p.trim())
      if (parts.length >= 3) {
        localAddress.value.street = parts[0] || ''
        localAddress.value.barangay = parts[1]?.replace('Brgy. ', '') || ''
        localAddress.value.municipality = parts[2] || ''
        localAddress.value.province = parts[3] || ''
        localAddress.value.zipCode = parts[4] || ''
      }
    } else if (typeof props.modelValue === 'object') {
      localAddress.value = { ...localAddress.value, ...props.modelValue }
    }
  }
})

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  if (newVal && typeof newVal === 'object') {
    localAddress.value = { ...localAddress.value, ...newVal }
  }
})
</script>

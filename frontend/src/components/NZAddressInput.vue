<template>
  <div class="space-y-4">
    <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-green-900">Property Location</h3>
          <p class="text-xs text-green-700 mt-0.5">Provide the complete property address</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Street Address -->
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Street Address
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          v-model="localAddress.street_address"
          type="text"
          :required="required"
          class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
          :class="{'border-green-500 ring-2 ring-green-100': localAddress.street_address}"
          placeholder="123 Main Street"
          @input="emitUpdate"
        />
      </div>

      <!-- Suburb -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Suburb</label>
        <input
          v-model="localAddress.suburb"
          type="text"
          class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
          placeholder="Petone"
          @input="emitUpdate"
        />
      </div>

      <!-- City -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          City
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <select
          v-model="localAddress.city"
          :required="required"
          class="block w-full pl-3 pr-10 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
          :class="{'border-green-500 ring-2 ring-green-100': localAddress.city}"
          @change="emitUpdate"
        >
          <option value="">Select City</option>
          <option value="Lower Hutt">Lower Hutt</option>
          <option value="Upper Hutt">Upper Hutt</option>
          <option value="Wellington">Wellington</option>
          <option value="Porirua">Porirua</option>
          <option value="Kapiti Coast">Kapiti Coast</option>
          <option value="Masterton">Masterton</option>
          <option value="South Wairarapa">South Wairarapa</option>
          <option value="Carterton">Carterton</option>
        </select>
      </div>

      <!-- Postcode -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Postcode
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          v-model="localAddress.postcode"
          type="text"
          :required="required"
          maxlength="4"
          pattern="[0-9]{4}"
          class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
          :class="{'border-green-500 ring-2 ring-green-100': localAddress.postcode}"
          placeholder="5011"
          @input="emitUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const localAddress = ref({
  street_address: '',
  suburb: '',
  city: '',
  postcode: ''
})

onMounted(() => {
  if (props.modelValue) {
    localAddress.value = { ...localAddress.value, ...props.modelValue }
  }
})

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    localAddress.value = { ...localAddress.value, ...newVal }
  }
}, { deep: true })

function emitUpdate() {
  emit('update:modelValue', localAddress.value)
}
</script>

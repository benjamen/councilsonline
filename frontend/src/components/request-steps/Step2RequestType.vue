<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Application Type</h2>
    <p class="text-gray-600 mb-8">Choose the type of consent you wish to apply for</p>

    <div v-if="requestTypes.loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else class="grid md:grid-cols-2 gap-4">
      <div
        v-for="type in requestTypes.data"
        :key="type.name"
        @click="selectType(type)"
        class="border-2 rounded-lg p-6 cursor-pointer transition-all hover:shadow-md"
        :class="modelValue.request_type === type.name ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ type.type_name }}</h3>
            <p class="text-sm text-gray-600" v-html="type.description || 'No description available'"></p>
            <div class="mt-4 flex items-center space-x-4 text-xs text-gray-500">
              <span v-if="type.base_fee">Fee: ${{ type.base_fee }}</span>
              <span v-if="type.processing_sla_days">{{ type.processing_sla_days }} days</span>
              <span v-if="type.category" class="px-2 py-1 bg-gray-100 rounded">{{ type.category }}</span>
            </div>
          </div>
          <div v-if="modelValue.request_type === type.name" class="ml-4">
            <div class="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>
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
  },
  requestTypes: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'type-selected'])

const selectType = (type) => {
  console.log('[Step2RequestType] selectType called with:', type.name)
  console.log('[Step2RequestType] props.modelValue:', props.modelValue)
  console.log('[Step2RequestType] props.modelValue.council:', props.modelValue.council)

  const updatedValue = {
    ...props.modelValue,
    request_type: type.name
  }

  console.log('[Step2RequestType] Emitting updatedValue:', updatedValue)
  emit('update:modelValue', updatedValue)
  emit('type-selected', type.name)
}
</script>

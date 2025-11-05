<template>
  <div class="bg-gray-50 rounded-xl p-6 hover:shadow-lg transition-shadow duration-300 border border-gray-100">
    <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
      <FeatherIcon :name="icon" class="w-6 h-6 text-blue-600" />
    </div>
    <h4 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h4>
    <p class="text-gray-600 text-sm leading-relaxed">{{ description }}</p>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})
</script>

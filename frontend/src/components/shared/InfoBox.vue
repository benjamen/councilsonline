<template>
  <div
    class="border rounded-lg p-4"
    :class="variantClasses"
  >
    <div class="flex items-start">
      <svg class="w-5 h-5 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div class="flex-1">
        <h5 class="font-semibold text-sm" :class="titleClass">{{ title }}</h5>
        <div class="text-sm mt-1" :class="contentClass">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: "info", // "info", "warning", "success", "error"
    validator: (value) => ["info", "warning", "success", "error"].includes(value)
  }
})

const variantClasses = computed(() => {
  const variants = {
    info: "bg-blue-50 border-blue-200",
    warning: "bg-yellow-50 border-yellow-200",
    success: "bg-green-50 border-green-200",
    error: "bg-red-50 border-red-200"
  }
  return variants[props.variant]
})

const titleClass = computed(() => {
  const classes = {
    info: "text-blue-900",
    warning: "text-yellow-900",
    success: "text-green-900",
    error: "text-red-900"
  }
  return classes[props.variant]
})

const contentClass = computed(() => {
  const classes = {
    info: "text-blue-800",
    warning: "text-yellow-800",
    success: "text-green-800",
    error: "text-red-800"
  }
  return classes[props.variant]
})
</script>

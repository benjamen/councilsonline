<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600 mb-1">{{ title }}</p>
        <p class="text-3xl font-bold" :class="valueColor">{{ value }}</p>
      </div>
      <div :class="iconBgColor" class="w-12 h-12 rounded-lg flex items-center justify-center">
        <FeatherIcon :name="icon" :class="iconColor" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue'
  }
})

const colorConfig = {
  blue: {
    value: 'text-blue-600',
    iconBg: 'bg-blue-100',
    icon: 'text-blue-600'
  },
  green: {
    value: 'text-green-600',
    iconBg: 'bg-green-100',
    icon: 'text-green-600'
  },
  yellow: {
    value: 'text-yellow-600',
    iconBg: 'bg-yellow-100',
    icon: 'text-yellow-600'
  },
  orange: {
    value: 'text-orange-600',
    iconBg: 'bg-orange-100',
    icon: 'text-orange-600'
  },
  red: {
    value: 'text-red-600',
    iconBg: 'bg-red-100',
    icon: 'text-red-600'
  }
}

const valueColor = computed(() => colorConfig[props.color]?.value || colorConfig.blue.value)
const iconBgColor = computed(() => colorConfig[props.color]?.iconBg || colorConfig.blue.iconBg)
const iconColor = computed(() => colorConfig[props.color]?.icon || colorConfig.blue.icon)
</script>

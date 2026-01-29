<template>
  <!-- Generic skeleton shapes -->
  <div v-if="type === 'text'" :class="['bg-gray-200 rounded animate-pulse', sizeClasses]"></div>

  <div v-else-if="type === 'circle'" :class="['bg-gray-200 rounded-full animate-pulse', sizeClasses]"></div>

  <div v-else-if="type === 'card'" class="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
    <div class="flex items-center space-x-4">
      <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
      <div class="flex-1 space-y-2">
        <div class="h-4 bg-gray-200 rounded w-1/3"></div>
        <div class="h-6 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
  </div>

  <!-- Stats Card Skeleton -->
  <div v-else-if="type === 'stat-card'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
    <div class="flex items-center justify-between">
      <div class="space-y-2">
        <div class="h-4 bg-gray-200 rounded w-24"></div>
        <div class="h-8 bg-gray-200 rounded w-16"></div>
      </div>
      <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
    </div>
  </div>

  <!-- Table Row Skeleton -->
  <div v-else-if="type === 'table-row'" class="flex items-center px-4 py-4 border-b border-gray-200 animate-pulse">
    <div class="flex-1 grid grid-cols-6 gap-4">
      <div class="h-4 bg-gray-200 rounded"></div>
      <div class="h-4 bg-gray-200 rounded col-span-2"></div>
      <div class="h-4 bg-gray-200 rounded"></div>
      <div class="h-4 bg-gray-200 rounded"></div>
      <div class="h-4 bg-gray-200 rounded w-16 ml-auto"></div>
    </div>
  </div>

  <!-- Mobile Card Skeleton -->
  <div v-else-if="type === 'mobile-card'" class="p-4 border-b border-gray-200 animate-pulse">
    <div class="flex justify-between items-start mb-2">
      <div class="h-4 bg-gray-200 rounded w-24"></div>
      <div class="h-5 bg-gray-200 rounded w-16"></div>
    </div>
    <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div class="flex justify-between items-center">
      <div class="h-3 bg-gray-200 rounded w-20"></div>
      <div class="h-3 bg-gray-200 rounded w-16"></div>
    </div>
  </div>

  <!-- Form Field Skeleton -->
  <div v-else-if="type === 'form-field'" class="space-y-2 animate-pulse">
    <div class="h-4 bg-gray-200 rounded w-24"></div>
    <div class="h-10 bg-gray-200 rounded"></div>
  </div>

  <!-- Profile Header Skeleton -->
  <div v-else-if="type === 'profile-header'" class="flex items-center space-x-6 animate-pulse">
    <div class="w-24 h-24 bg-gray-200 rounded-full"></div>
    <div class="space-y-2">
      <div class="h-6 bg-gray-200 rounded w-48"></div>
      <div class="h-4 bg-gray-200 rounded w-32"></div>
      <div class="h-3 bg-gray-200 rounded w-40"></div>
    </div>
  </div>

  <!-- Section with multiple form fields -->
  <div v-else-if="type === 'form-section'" class="space-y-6 animate-pulse">
    <div class="h-6 bg-gray-200 rounded w-32 mb-4"></div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="n in (count || 4)" :key="n" class="space-y-2">
        <div class="h-4 bg-gray-200 rounded w-24"></div>
        <div class="h-10 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>

  <!-- Navigation Tab Skeleton -->
  <div v-else-if="type === 'nav-tab'" class="w-full px-4 py-3 rounded-lg animate-pulse">
    <div class="flex items-center space-x-3">
      <div class="w-5 h-5 bg-gray-200 rounded"></div>
      <div class="h-4 bg-gray-200 rounded w-24"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value) => [
      'text', 'circle', 'card', 'stat-card', 'table-row',
      'mobile-card', 'form-field', 'profile-header',
      'form-section', 'nav-tab'
    ].includes(value)
  },
  width: {
    type: String,
    default: 'full'
  },
  height: {
    type: String,
    default: '4'
  },
  count: {
    type: Number,
    default: 4
  }
})

const sizeClasses = computed(() => {
  const widthClass = props.width === 'full' ? 'w-full' : `w-${props.width}`
  const heightClass = `h-${props.height}`
  return `${widthClass} ${heightClass}`
})
</script>

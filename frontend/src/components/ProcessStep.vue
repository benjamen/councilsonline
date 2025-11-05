<template>
  <div class="text-center relative">
    <!-- Step Number -->
    <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-4 shadow-lg">
      {{ number }}
    </div>

    <!-- Connector Line (hidden on last step) -->
    <div v-if="number !== '4'" class="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-blue-200 -z-10" style="transform: translateX(50%)"></div>

    <h4 class="text-xl font-semibold text-gray-900 mb-2">{{ title }}</h4>
    <p class="text-gray-600 text-sm">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  number: {
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

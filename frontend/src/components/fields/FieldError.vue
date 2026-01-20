<template>
  <div>
    <p v-if="error" class="mt-1 text-xs text-red-600">
      {{ error }}
    </p>
    <p v-else-if="description" class="mt-1 text-xs text-gray-500">
      {{ description }}
    </p>
  </div>
</template>

<script setup>
defineProps({
	error: {
		type: String,
		default: "",
	},
	description: {
		type: String,
		default: "",
	},
})
</script>

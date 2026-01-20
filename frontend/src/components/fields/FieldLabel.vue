<template>
  <label
    :for="fieldName"
    class="block text-sm font-medium text-gray-700 mb-2 flex items-center"
  >
    <span>{{ label }}</span>
    <span v-if="required" class="text-red-500 ml-1">*</span>
    <Tooltip v-if="helpText" :text="helpText" />
  </label>
</template>

<script setup>
import Tooltip from "../Tooltip.vue"

defineProps({
	fieldName: {
		type: String,
		required: true,
	},
	label: {
		type: String,
		required: true,
	},
	required: {
		type: Boolean,
		default: false,
	},
	helpText: {
		type: String,
		default: "",
	},
})
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Council</h2>
    <p class="text-gray-600 mb-8">Choose the council that will process your application</p>

    <CouncilSelector
      :model-value="modelValue.council"
      @update:model-value="updateCouncil"
      display-mode="cards"
      :required="true"
      :show-selected-info="true"
      label=""
      :show-label="false"
    />
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from "vue"
import CouncilSelector from "../CouncilSelector.vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue", "council-change"])

const updateCouncil = (council) => {
	console.log("[Step1CouncilSelection] updateCouncil called with:", council)
	console.log("[Step1CouncilSelection] Current modelValue:", props.modelValue)

	emit("update:modelValue", {
		...props.modelValue,
		council: council,
	})
	emit("council-change", council)

	console.log("[Step1CouncilSelection] Emitted events")
}
</script>

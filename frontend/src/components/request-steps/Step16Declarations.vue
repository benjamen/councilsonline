<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Statutory Declarations</h2>
    <p class="text-gray-600 mb-8">Confirm compliance with RMA requirements</p>

    <div class="space-y-6">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-blue-900 text-sm">Statutory Declarations Required</h5>
            <p class="text-blue-800 text-sm mt-1">
              Under the Resource Management Act 1991, you must confirm the following declarations before submitting your application.
            </p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="border-2 rounded-lg p-4" :class="localData.declaration_rma_compliance ? 'border-green-600 bg-green-50' : 'border-gray-200'">
          <label class="flex items-start cursor-pointer">
            <input
              type="checkbox"
              v-model="localData.declaration_rma_compliance"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3 flex-1">
              <span class="font-medium text-gray-900">RMA Compliance Declaration *</span>
              <p class="text-sm text-gray-600 mt-1">
                I confirm that this application complies with the requirements of Schedule 4 of the Resource Management Act 1991 and contains all required information for the council to process this application.
              </p>
            </div>
          </label>
        </div>

        <div class="border-2 rounded-lg p-4" :class="localData.declaration_public_information ? 'border-green-600 bg-green-50' : 'border-gray-200'">
          <label class="flex items-start cursor-pointer">
            <input
              type="checkbox"
              v-model="localData.declaration_public_information"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3 flex-1">
              <span class="font-medium text-gray-900">Public Information Declaration *</span>
              <p class="text-sm text-gray-600 mt-1">
                I understand that this application and supporting documents will become public information and may be made available to any person upon request under the Local Government Official Information and Meetings Act 1987.
              </p>
            </div>
          </label>
        </div>

        <div class="border-2 rounded-lg p-4" :class="localData.declaration_authorized ? 'border-green-600 bg-green-50' : 'border-gray-200'">
          <label class="flex items-start cursor-pointer">
            <input
              type="checkbox"
              v-model="localData.declaration_authorized"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div class="ml-3 flex-1">
              <span class="font-medium text-gray-900">Authorization Declaration *</span>
              <p class="text-sm text-gray-600 mt-1">
                I confirm that I am authorized to make this application on behalf of the applicant and that all information provided is true and correct to the best of my knowledge.
              </p>
            </div>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Local data
const localData = ref({
	declaration_rma_compliance:
		props.modelValue.declaration_rma_compliance || false,
	declaration_public_information:
		props.modelValue.declaration_public_information || false,
	declaration_authorized: props.modelValue.declaration_authorized || false,
})

// Watch for external changes
watch(
	() => [
		props.modelValue.declaration_rma_compliance,
		props.modelValue.declaration_public_information,
		props.modelValue.declaration_authorized,
	],
	([newRma, newPublic, newAuth]) => {
		localData.value.declaration_rma_compliance = newRma || false
		localData.value.declaration_public_information = newPublic || false
		localData.value.declaration_authorized = newAuth || false
	},
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			declaration_rma_compliance: newVal.declaration_rma_compliance,
			declaration_public_information: newVal.declaration_public_information,
			declaration_authorized: newVal.declaration_authorized,
		})
	},
	{ deep: true },
)
</script>

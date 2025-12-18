<template>
  <div class="space-y-4">
    <div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-purple-600 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-purple-900">Activity Status</h3>
          <p class="text-xs text-purple-700 mt-0.5">Select the RMA activity classification for your proposal</p>
        </div>
      </div>
    </div>

    <div class="space-y-3">
      <!-- Permitted Activity -->
      <label
        class="cursor-pointer block rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="localValue === 'Permitted' ? 'border-green-500 bg-green-50 ring-2 ring-green-200' : 'border-gray-300 bg-white hover:border-green-300'"
      >
        <div class="flex items-start">
          <input
            type="radio"
            value="Permitted"
            v-model="localValue"
            @change="emitUpdate"
            class="mt-1 h-4 w-4 text-green-600 focus:ring-green-500"
          />
          <div class="ml-3 flex-1">
            <div class="flex items-center">
              <span class="text-sm font-semibold" :class="localValue === 'Permitted' ? 'text-green-900' : 'text-gray-900'">
                Permitted Activity
              </span>
              <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                Lowest impact
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Complies with all district/regional plan rules. No consent required.
            </p>
          </div>
        </div>
      </label>

      <!-- Controlled Activity -->
      <label
        class="cursor-pointer block rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="localValue === 'Controlled' ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-300 bg-white hover:border-blue-300'"
      >
        <div class="flex items-start">
          <input
            type="radio"
            value="Controlled"
            v-model="localValue"
            @change="emitUpdate"
            class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
          />
          <div class="ml-3 flex-1">
            <div class="flex items-center">
              <span class="text-sm font-semibold" :class="localValue === 'Controlled' ? 'text-blue-900' : 'text-gray-900'">
                Controlled Activity
              </span>
              <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                Must be granted
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Consent must be granted but conditions may be imposed. Council control is restricted to specified matters.
            </p>
          </div>
        </div>
      </label>

      <!-- Restricted Discretionary -->
      <label
        class="cursor-pointer block rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="localValue === 'Restricted Discretionary' ? 'border-yellow-500 bg-yellow-50 ring-2 ring-yellow-200' : 'border-gray-300 bg-white hover:border-yellow-300'"
      >
        <div class="flex items-start">
          <input
            type="radio"
            value="Restricted Discretionary"
            v-model="localValue"
            @change="emitUpdate"
            class="mt-1 h-4 w-4 text-yellow-600 focus:ring-yellow-500"
          />
          <div class="ml-3 flex-1">
            <div class="flex items-center">
              <span class="text-sm font-semibold" :class="localValue === 'Restricted Discretionary' ? 'text-yellow-900' : 'text-gray-900'">
                Restricted Discretionary
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Council discretion is restricted to specified matters. Non-notification may apply.
            </p>
          </div>
        </div>
      </label>

      <!-- Discretionary Activity -->
      <label
        class="cursor-pointer block rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="localValue === 'Discretionary' ? 'border-orange-500 bg-orange-50 ring-2 ring-orange-200' : 'border-gray-300 bg-white hover:border-orange-300'"
      >
        <div class="flex items-start">
          <input
            type="radio"
            value="Discretionary"
            v-model="localValue"
            @change="emitUpdate"
            class="mt-1 h-4 w-4 text-orange-600 focus:ring-orange-500"
          />
          <div class="ml-3 flex-1">
            <div class="flex items-center">
              <span class="text-sm font-semibold" :class="localValue === 'Discretionary' ? 'text-orange-900' : 'text-gray-900'">
                Discretionary Activity
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Council has full discretion to grant or decline. May require notification.
            </p>
          </div>
        </div>
      </label>

      <!-- Non-Complying Activity -->
      <label
        class="cursor-pointer block rounded-lg border-2 p-4 transition-all hover:shadow-md"
        :class="localValue === 'Non-Complying' ? 'border-red-500 bg-red-50 ring-2 ring-red-200' : 'border-gray-300 bg-white hover:border-red-300'"
      >
        <div class="flex items-start">
          <input
            type="radio"
            value="Non-Complying"
            v-model="localValue"
            @change="emitUpdate"
            class="mt-1 h-4 w-4 text-red-600 focus:ring-red-500"
          />
          <div class="ml-3 flex-1">
            <div class="flex items-center">
              <span class="text-sm font-semibold" :class="localValue === 'Non-Complying' ? 'text-red-900' : 'text-gray-900'">
                Non-Complying Activity
              </span>
              <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                Highest scrutiny
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-1">
              Contravenes plan objectives and policies. Subject to Section 104D gateway test.
            </p>
          </div>
        </div>
      </label>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: String,
		default: "",
	},
	required: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

const localValue = ref("")

onMounted(() => {
	if (props.modelValue) {
		localValue.value = props.modelValue
	}
})

watch(
	() => props.modelValue,
	(newVal) => {
		localValue.value = newVal || ""
	},
)

function emitUpdate() {
	emit("update:modelValue", localValue.value)
}
</script>

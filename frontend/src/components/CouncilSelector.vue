<template>
  <div class="council-selector">
    <div v-if="showLabel" class="mb-2">
      <label class="text-sm font-medium text-gray-700">
        {{ label }}
        <span v-if="required" class="text-red-500">*</span>
      </label>
      <p v-if="description" class="text-xs text-gray-500 mt-1">
        {{ description }}
      </p>
    </div>

    <div v-if="loading" class="animate-pulse">
      <div class="h-10 bg-gray-200 rounded"></div>
    </div>

    <div v-else-if="error" class="text-sm text-red-600">
      {{ error }}
    </div>

    <div v-else class="space-y-3">
      <select
        v-if="displayMode === 'dropdown'"
        v-model="localSelectedCouncil"
        @change="handleCouncilChange"
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        :disabled="disabled"
        :required="required"
      >
        <option value="">{{ placeholder }}</option>
        <option
          v-for="council in councils"
          :key="council.council_code"
          :value="council.council_code"
        >
          {{ council.council_name }}
        </option>
      </select>

      <div v-else-if="displayMode === 'cards'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <button
          v-for="council in councils"
          :key="council.council_code"
          @click="selectCouncil(council.council_code)"
          :disabled="disabled"
          class="p-4 border-2 rounded-lg text-left transition-all relative"
          :class="[
            localSelectedCouncil === council.council_code
              ? 'border-blue-600 bg-blue-50 ring-2 ring-blue-500 ring-offset-2 shadow-lg'
              : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
          ]"
        >
          <div class="flex items-start space-x-3">
            <div
              v-if="council.logo"
              class="w-12 h-12 flex-shrink-0 rounded overflow-hidden"
            >
              <img
                :src="council.logo"
                :alt="council.council_name"
                class="w-full h-full object-contain"
              />
            </div>
            <div
              v-else
              class="w-12 h-12 flex-shrink-0 rounded flex items-center justify-center text-white font-bold text-lg"
              :style="{ backgroundColor: council.primary_color || '#3B82F6' }"
            >
              {{ council.council_code }}
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h3 class="font-semibold truncate" :class="localSelectedCouncil === council.council_code ? 'text-blue-900' : 'text-gray-900'">
                  {{ council.council_name }}
                </h3>
                <div v-if="localSelectedCouncil === council.council_code" class="ml-2">
                  <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fill-rule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </div>
              </div>
              <p v-if="council.website" class="text-xs text-gray-500 truncate mt-1">
                {{ formatWebsite(council.website) }}
              </p>
              <div v-if="localSelectedCouncil === council.council_code" class="mt-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Selected
                </span>
              </div>
            </div>
          </div>
        </button>
      </div>

      <div v-if="showClearButton && localSelectedCouncil" class="mt-2">
        <button
          @click="clearSelection"
          type="button"
          class="text-sm text-gray-600 hover:text-gray-800 underline"
        >
          Clear selection
        </button>
      </div>
    </div>

    <div
      v-if="localSelectedCouncil && showSelectedInfo"
      class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200"
    >
      <div class="flex items-start space-x-3">
        <div
          class="w-10 h-10 flex-shrink-0 rounded flex items-center justify-center text-white font-bold"
          :style="{ backgroundColor: selectedCouncilData?.primary_color || '#3B82F6' }"
        >
          {{ selectedCouncilData?.council_code }}
        </div>
        <div class="flex-1">
          <h4 class="font-medium text-gray-900">
            {{ selectedCouncilData?.council_name }}
          </h4>
          <p v-if="selectedCouncilData?.contact_email" class="text-xs text-gray-600 mt-1">
            {{ selectedCouncilData?.contact_email }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { useCouncilStore } from "../stores/councilStore"

const props = defineProps({
	modelValue: {
		type: String,
		default: null,
	},
	label: {
		type: String,
		default: "Select Council",
	},
	description: {
		type: String,
		default: "",
	},
	placeholder: {
		type: String,
		default: "Choose a council...",
	},
	displayMode: {
		type: String,
		default: "dropdown", // 'dropdown' or 'cards'
		validator: (value) => ["dropdown", "cards"].includes(value),
	},
	required: {
		type: Boolean,
		default: false,
	},
	disabled: {
		type: Boolean,
		default: false,
	},
	showLabel: {
		type: Boolean,
		default: true,
	},
	showClearButton: {
		type: Boolean,
		default: false,
	},
	showSelectedInfo: {
		type: Boolean,
		default: false,
	},
	autoLoad: {
		type: Boolean,
		default: true,
	},
})

const emit = defineEmits(["update:modelValue", "change"])

const councilStore = useCouncilStore()

const localSelectedCouncil = ref(props.modelValue)

const councils = computed(() => councilStore.activeCouncils)
const loading = computed(() => councilStore.loading)
const error = computed(() => councilStore.error)

const selectedCouncilData = computed(() => {
	if (!localSelectedCouncil.value) return null
	return councils.value.find(
		(c) => c.council_code === localSelectedCouncil.value,
	)
})

const formatWebsite = (url) => {
	return url.replace(/^https?:\/\/(www\.)?/, "")
}

const selectCouncil = (councilCode) => {
	if (props.disabled) return
	localSelectedCouncil.value = councilCode
	handleCouncilChange()
}

const handleCouncilChange = () => {
	emit("update:modelValue", localSelectedCouncil.value)
	emit("change", localSelectedCouncil.value)
}

const clearSelection = () => {
	localSelectedCouncil.value = null
	handleCouncilChange()
}

watch(
	() => props.modelValue,
	(newValue) => {
		localSelectedCouncil.value = newValue
	},
)

onMounted(async () => {
	if (props.autoLoad && councils.value.length === 0) {
		await councilStore.loadCouncils()
	}
})
</script>

<style scoped>
.council-selector {
  @apply w-full;
}
</style>

<template>
<div class="dynamic-step max-w-4xl mx-auto">
    <div class="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
            </div>
            <div class="ml-4 flex-1">
                <h2 class="text-2xl font-bold text-blue-900">{{ stepConfig.step_title }}</h2>
                <p v-if="stepDescription" class="mt-2 text-sm text-blue-700">{{ stepDescription }}</p>
            </div>
        </div>
    </div>

    <div class="space-y-6">
        <div v-for="section in visibleSections" :key="section.section_code" class="section">
            <div class="mb-4 pb-3 border-b-2 border-gray-200">
                <div class="flex items-center">
                    <div class="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                        <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900">
                            {{ section.section_title }}
                            <span v-if="section.is_required" class="text-red-500 ml-1">*</span>
                        </h3>
                        <p v-if="section.section_description" class="text-sm text-gray-600 mt-0.5">
                            {{ section.section_description }}
                        </p>
                    </div>
                </div>
                <div v-if="section.is_required" class="text-xs text-gray-500 mt-2 ml-11">
                    All fields marked with <span class="text-red-500">*</span> are required
                </div>
            </div>

            <div class="section-content">
                <TabGroup v-if="section.section_type === 'Tab'">
                    <TabList class="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-4">
                        <Tab
                            v-for="(tab, idx) in getTabsForSection(section)"
                            :key="idx"
                            v-slot="{ selected }"
                            class="w-full rounded-lg py-2.5 text-sm font-medium leading-5 text-blue-700 ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2"
                            :class="selected ? 'bg-white shadow' : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'"
                        >
                            {{ tab }}
                        </Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel v-for="(tab, idx) in getTabsForSection(section)" :key="idx">
                            <DynamicFieldRenderer
                                :fields="section.fields"
                                v-model="localData"
                            />
                        </TabPanel>
                    </TabPanels>
                </TabGroup>

                <Disclosure v-else-if="section.section_type === 'Accordion'" v-slot="{ open }">
                    <DisclosureButton
                        class="flex w-full justify-between rounded-lg bg-blue-50 px-4 py-3 text-left text-sm font-medium text-blue-900 hover:bg-blue-100 focus:outline-none focus-visible:ring focus-visible:ring-blue-500 focus-visible:ring-opacity-75 mb-2"
                    >
                        <span>{{ section.section_title }}</span>
                        <ChevronUpIcon
                            :class="open ? 'rotate-180 transform' : ''"
                            class="h-5 w-5 text-blue-500"
                        />
                    </DisclosureButton>
                    <DisclosurePanel class="px-4 pt-4 pb-2 text-sm text-gray-500">
                        <DynamicFieldRenderer
                            :fields="section.fields"
                            v-model="localData"
                        />
                    </DisclosurePanel>
                </Disclosure>

                <div v-else class="bg-white p-6 rounded-lg border-2 border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <DynamicFieldRenderer
                        :fields="section.fields"
                        v-model="localData"
                    />
                </div>
            </div>
        </div>
    </div>

    <div class="mt-8 pt-4 border-t border-gray-200">
        <button
            @click="logCurrentData"
            class="px-4 py-2 bg-red-500 text-white rounded-lg shadow hover:bg-red-600 transition"
        >
            🚨 Log Current Data (Debug)
        </button>
        <p class="text-xs text-gray-500 mt-2">Use this button to check if data is being saved correctly to localData/formData.</p>
    </div>
    </div>
</template>

<script setup>
import {
	Disclosure,
	DisclosureButton,
	DisclosurePanel,
	Tab,
	TabGroup,
	TabList,
	TabPanel,
	TabPanels,
} from "@headlessui/vue"
import { ChevronUpIcon } from "@heroicons/vue/20/solid"
import { computed, ref, watch } from "vue"
import DynamicFieldRenderer from "./DynamicFieldRenderer.vue"
// The import for the utility function is commented out to effectively disable the filter
// import { isSectionVisible } from '../utils/conditionalLogic'

const props = defineProps({
	stepConfig: {
		type: Object,
		required: true,
	},
	modelValue: {
		type: Object,
		required: true,
	},
	stepDescription: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

const visibleSections = computed(() => {
	if (!props.stepConfig.sections) return []

	// Filter sections based on depends_on expressions
	return props.stepConfig.sections.filter((section) => {
		if (!section.depends_on) return true
		try {
			return isSectionVisible(section, localData.value)
		} catch (error) {
			console.error(
				`Error evaluating section visibility for ${section.section_code}:`,
				error,
			)
			return true // Fail open - show section on error
		}
	})
})

// Get tabs for tab-based sections (placeholder)
const getTabsForSection = (section) => {
	// For now, return single tab
	// In future, could parse section structure for multiple tabs
	return [section.section_title]
}

// === DEBUG CHANGE 2: Add Debug Function ===
const logCurrentData = () => {
	// Stringify and parse to clone the object and ensure reactivity is not confusing the log
	console.log("--- DYNAMIC STEP DATA LOG ---")
	console.log(
		"Full Form Data (localData):",
		JSON.parse(JSON.stringify(localData.value)),
	)
	console.log("-----------------------------")
	alert(
		"Data logged to console. Check browser console (F12) for the Full Form Data.",
	)
}
// ===========================================

// Initialize default values
watch(
	() => props.stepConfig,
	(config) => {
		if (!config.sections) return

		config.sections.forEach((section) => {
			section.fields.forEach((field) => {
				if (field.default_value && !localData.value[field.field_name]) {
					// To safely update the computed 'localData' (which runs an emit to update the parent's store)
					const newLocalData = { ...localData.value }

					if (field.default_value === "Today" && field.field_type === "Date") {
						newLocalData[field.field_name] = new Date()
							.toISOString()
							.split("T")[0]
					} else {
						newLocalData[field.field_name] = field.default_value
					}

					// Emit the new object to update the parent's modelValue/store.formData
					emit("update:modelValue", newLocalData)
				}
			})
		})
	},
	{ immediate: true, deep: true },
)
</script>

<style scoped>
.dynamic-step {
    max-width: 100%;
}

.section {
    margin-bottom: 2rem;
    scroll-margin-top: 100px; /* For smooth scrolling with fixed headers */
}

.section-content {
    margin-top: 1rem;
}

/* Enhanced tab styling */
:deep(.tab-active) {
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Smooth transitions for all interactive elements */
.section-content > div {
    transition: all 0.2s ease-in-out;
}
</style>
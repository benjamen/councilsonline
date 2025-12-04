<template>
  <div class="dynamic-step">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900">{{ stepConfig.step_title }}</h2>
      <p v-if="stepDescription" class="mt-2 text-sm text-gray-600">{{ stepDescription }}</p>
    </div>

    <!-- Render sections -->
    <div class="space-y-8">
      <div v-for="section in visibleSections" :key="section.section_code" class="section">
        <!-- Section Header -->
        <div class="mb-4">
          <h3 class="text-lg font-semibold text-gray-800">
            {{ section.section_title }}
            <span v-if="section.is_required" class="text-red-500">*</span>
          </h3>
          <div v-if="section.is_required" class="text-xs text-gray-500 mt-1">
            All fields marked with * are required
          </div>
        </div>

        <!-- Section Content -->
        <div class="section-content">
          <!-- Tab-based sections -->
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

          <!-- Accordion-based sections -->
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

          <!-- Regular section (default) -->
          <div v-else class="bg-white p-6 rounded-lg border border-gray-200">
            <DynamicFieldRenderer
              :fields="section.fields"
              v-model="localData"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex justify-between mt-8 pt-6 border-t border-gray-200">
      <button
        v-if="showBackButton"
        @click="$emit('back')"
        type="button"
        class="px-6 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Back
      </button>
      <div v-else></div>

      <button
        @click="handleContinue"
        type="button"
        :disabled="!canProceed"
        class="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {{ isLastStep ? 'Review Application' : 'Continue' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { TabGroup, TabList, Tab, TabPanels, TabPanel, Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ChevronUpIcon } from '@heroicons/vue/20/solid'
import DynamicFieldRenderer from './DynamicFieldRenderer.vue'

const props = defineProps({
  stepConfig: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Object,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  },
  isLastStep: {
    type: Boolean,
    default: false
  },
  stepDescription: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'continue', 'back'])

const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Filter visible sections based on depends_on logic
const visibleSections = computed(() => {
  if (!props.stepConfig.sections) return []

  return props.stepConfig.sections.filter(section => {
    if (!section.is_enabled) return false

    if (section.depends_on) {
      // TODO: Implement proper conditional logic evaluation
      // For now, show all enabled sections
      return true
    }

    return true
  })
})

// Check if user can proceed (all required fields filled)
const canProceed = computed(() => {
  if (!props.stepConfig.is_required) return true

  for (const section of visibleSections.value) {
    if (!section.is_required) continue

    for (const field of section.fields) {
      if (field.is_required) {
        const value = localData.value[field.field_name]

        // Check if field has a value
        if (value === undefined || value === null || value === '') {
          return false
        }

        // For checkboxes, ensure they're checked if required
        if (field.field_type === 'Check' && !value) {
          return false
        }
      }
    }
  }

  return true
})

// Get tabs for tab-based sections (placeholder)
const getTabsForSection = (section) => {
  // For now, return single tab
  // In future, could parse section structure for multiple tabs
  return [section.section_title]
}

// Handle continue button
const handleContinue = () => {
  if (canProceed.value) {
    emit('continue')
  }
}

// Initialize default values
watch(() => props.stepConfig, (config) => {
  if (!config.sections) return

  config.sections.forEach(section => {
    section.fields.forEach(field => {
      if (field.default_value && !localData.value[field.field_name]) {
        if (field.default_value === 'Today' && field.field_type === 'Date') {
          localData.value[field.field_name] = new Date().toISOString().split('T')[0]
        } else {
          localData.value[field.field_name] = field.default_value
        }
      }
    })
  })
}, { immediate: true, deep: true })
</script>

<style scoped>
.dynamic-step {
  max-width: 100%;
}

.section {
  margin-bottom: 2rem;
}

.section-content {
  margin-top: 1rem;
}
</style>

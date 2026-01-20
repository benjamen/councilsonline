<template>
  <div class="border border-gray-200 rounded-lg overflow-hidden">
    <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <button
            @click="$emit('move', 'up')"
            :disabled="isFirst"
            class="p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
            </svg>
          </button>
          <button
            @click="$emit('move', 'down')"
            :disabled="isLast"
            class="p-1 hover:bg-gray-200 rounded disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
        </div>
        <span class="text-sm font-medium text-gray-900">Step {{ stepNumber }}</span>
        <input
          :value="step.step_title"
          @input="$emit('update:step', { ...step, step_title: $event.target.value })"
          type="text"
          class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Step Title"
        />
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="$emit('toggle')"
          class="text-sm text-gray-600 hover:text-gray-900"
        >
          {{ step.expanded ? 'Collapse' : 'Expand' }}
        </button>
        <button
          @click="$emit('delete')"
          class="text-sm text-red-600 hover:text-red-700"
        >
          Delete
        </button>
      </div>
    </div>

    <div v-if="step.expanded" class="p-4">
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Step Code</label>
          <input
            :value="step.step_code"
            @input="$emit('update:step', { ...step, step_code: $event.target.value })"
            type="text"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm"
            placeholder="e.g., applicant_details"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Component</label>
          <select
            :value="step.step_component"
            @change="$emit('update:step', { ...step, step_component: $event.target.value })"
            class="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="DynamicStepRenderer">Dynamic Step Renderer</option>
            <option value="Custom">Custom Component</option>
          </select>
        </div>
      </div>

      <div class="flex gap-4 mb-4">
        <label class="flex items-center text-sm">
          <input
            :checked="step.is_required"
            @change="$emit('update:step', { ...step, is_required: $event.target.checked })"
            type="checkbox"
            class="mr-2"
          />
          Required
        </label>
        <label class="flex items-center text-sm">
          <input
            :checked="step.show_on_review"
            @change="$emit('update:step', { ...step, show_on_review: $event.target.checked })"
            type="checkbox"
            class="mr-2"
          />
          Show on Review
        </label>
      </div>

      <div class="mt-4">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-sm font-medium text-gray-700">Sections</h4>
          <button
            @click="$emit('add-section')"
            class="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
          >
            + Add Section
          </button>
        </div>

        <div v-if="!step.sections || step.sections.length === 0" class="text-xs text-gray-500 text-center py-4">
          No sections yet
        </div>

        <div v-else class="space-y-3">
          <SectionCard
            v-for="(section, sectionIndex) in step.sections"
            :key="sectionIndex"
            :section="section"
            @update:section="(updatedSection) => $emit('update-section', sectionIndex, updatedSection)"
            @delete="$emit('delete-section', sectionIndex)"
            @add-field="$emit('add-field', sectionIndex)"
            @update-field="(fieldIndex, updatedField) => $emit('update-field', sectionIndex, fieldIndex, updatedField)"
            @delete-field="(fieldIndex) => $emit('delete-field', sectionIndex, fieldIndex)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import SectionCard from "./SectionCard.vue"

defineProps({
	step: {
		type: Object,
		required: true,
	},
	stepNumber: {
		type: Number,
		required: true,
	},
	isFirst: {
		type: Boolean,
		default: false,
	},
	isLast: {
		type: Boolean,
		default: false,
	},
})

defineEmits([
	"update:step",
	"delete",
	"move",
	"toggle",
	"add-section",
	"update-section",
	"delete-section",
	"add-field",
	"update-field",
	"delete-field",
])
</script>

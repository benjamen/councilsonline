<template>
  <div class="bg-gray-50 p-3 rounded border border-gray-200">
    <div class="flex items-center justify-between mb-2">
      <input
        :value="section.section_title"
        @input="$emit('update:section', { ...section, section_title: $event.target.value })"
        type="text"
        class="flex-1 px-2 py-1 border border-gray-300 rounded text-sm mr-2"
        placeholder="Section Title"
      />
      <button
        @click="$emit('delete')"
        class="text-xs text-red-600 hover:text-red-700"
      >
        Delete
      </button>
    </div>

    <div class="grid grid-cols-2 gap-2 mb-2">
      <div>
        <label class="block text-xs text-gray-600 mb-1">Section Code</label>
        <input
          :value="section.section_code"
          @input="$emit('update:section', { ...section, section_code: $event.target.value })"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
          placeholder="e.g., personal_info"
        />
      </div>
      <div>
        <label class="block text-xs text-gray-600 mb-1">Section Type</label>
        <select
          :value="section.section_type"
          @change="$emit('update:section', { ...section, section_type: $event.target.value })"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
        >
          <option value="Standard">Standard</option>
          <option value="Tab">Tab</option>
          <option value="Accordion">Accordion</option>
        </select>
      </div>
    </div>

    <div class="mt-3">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-medium text-gray-700">Fields</span>
        <button
          @click="$emit('add-field')"
          class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
        >
          + Add Field
        </button>
      </div>

      <div v-if="!section.fields || section.fields.length === 0" class="text-xs text-gray-400 text-center py-2">
        No fields yet
      </div>

      <div v-else class="space-y-2">
        <FieldCard
          v-for="(field, fieldIndex) in section.fields"
          :key="fieldIndex"
          :field="field"
          @update:field="(updatedField) => $emit('update-field', fieldIndex, updatedField)"
          @delete="$emit('delete-field', fieldIndex)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import FieldCard from "./FieldCard.vue"

defineProps({
	section: {
		type: Object,
		required: true,
	},
})

defineEmits([
	"update:section",
	"delete",
	"add-field",
	"update-field",
	"delete-field",
])
</script>

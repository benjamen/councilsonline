<template>
  <div class="bg-white p-2 rounded border border-gray-200">
    <div class="grid grid-cols-3 gap-2">
      <div class="col-span-2">
        <input
          :value="field.field_label"
          @input="$emit('update:field', { ...field, field_label: $event.target.value })"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
          placeholder="Field Label"
        />
      </div>
      <div>
        <select
          :value="field.field_type"
          @change="$emit('update:field', { ...field, field_type: $event.target.value })"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
        >
          <option value="Data">Text</option>
          <option value="Text">Textarea</option>
          <option value="Select">Select</option>
          <option value="Date">Date</option>
          <option value="Check">Checkbox</option>
          <option value="Currency">Currency</option>
          <option value="Int">Integer</option>
          <option value="Float">Float</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-2 mt-2">
      <div class="col-span-2">
        <input
          :value="field.field_name"
          @input="$emit('update:field', { ...field, field_name: $event.target.value })"
          type="text"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
          placeholder="field_name"
        />
      </div>
      <div class="flex items-center gap-2">
        <label class="flex items-center text-xs">
          <input
            :checked="field.is_required"
            @change="$emit('update:field', { ...field, is_required: $event.target.checked })"
            type="checkbox"
            class="mr-1 text-xs"
          />
          Required
        </label>
        <button
          @click="$emit('delete')"
          class="text-xs text-red-600 hover:text-red-700 ml-auto"
        >
          ✕
        </button>
      </div>
    </div>

    <div v-if="field.field_type === 'Select'" class="mt-2">
      <textarea
        :value="field.options"
        @input="$emit('update:field', { ...field, options: $event.target.value })"
        rows="2"
        class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
        placeholder="Options (one per line)"
      ></textarea>
    </div>

    <div class="mt-2">
      <input
        :value="field.validation"
        @input="$emit('update:field', { ...field, validation: $event.target.value })"
        type="text"
        class="w-full px-2 py-1 border border-gray-300 rounded text-xs"
        placeholder="Validation: email, phone, eval:value >= 18"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
	field: {
		type: Object,
		required: true,
	},
})

defineEmits(["update:field", "delete"])
</script>

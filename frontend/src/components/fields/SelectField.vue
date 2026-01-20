<template>
  <div class="form-group">
    <FieldLabel
      :field-name="field.field_name"
      :label="field.field_label"
      :required="Boolean(field.is_required)"
      :help-text="field.help_text || field.description"
    />
    <div class="relative">
      <select
        :id="field.field_name"
        :name="field.field_name"
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('validate')"
        :required="field.is_required"
        class="block w-full pl-4 pr-10 py-3 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg transition-all appearance-none bg-white"
        :class="{
          'border-blue-500 ring-2 ring-blue-100': modelValue && !validationError,
          'border-red-500 ring-2 ring-red-100': validationError
        }"
      >
        <option value="">Select {{ field.field_label }}</option>
        <option
          v-for="option in options"
          :key="option"
          :value="option"
        >
          {{ option }}
        </option>
      </select>
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </div>
    <FieldError :error="validationError" :description="field.description" />
  </div>
</template>

<script setup>
import FieldError from "./FieldError.vue"
import FieldLabel from "./FieldLabel.vue"

defineProps({
	field: {
		type: Object,
		required: true,
	},
	modelValue: {
		type: [String, Number],
		default: "",
	},
	validationError: {
		type: String,
		default: "",
	},
	options: {
		type: Array,
		default: () => [],
	},
})

defineEmits(["update:modelValue", "validate"])
</script>

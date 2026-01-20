<template>
  <div class="form-group">
    <FieldLabel
      :field-name="field.field_name"
      :label="field.field_label"
      :required="Boolean(field.is_required)"
      :help-text="field.help_text || field.description"
    />
    <textarea
      :id="field.field_name"
      :name="field.field_name"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('validate')"
      :required="field.is_required"
      rows="4"
      class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all resize-y"
      :class="{
        'border-blue-500 ring-2 ring-blue-100': modelValue && !validationError,
        'border-red-500 ring-2 ring-red-100': validationError
      }"
      :placeholder="placeholder"
    ></textarea>
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
		type: String,
		default: "",
	},
	validationError: {
		type: String,
		default: "",
	},
	placeholder: {
		type: String,
		default: "",
	},
})

defineEmits(["update:modelValue", "validate"])
</script>

<template>
  <div class="form-group">
    <FieldLabel
      :field-name="field.field_name"
      :label="field.field_label"
      :required="Boolean(field.is_required)"
      :help-text="field.help_text || field.description"
    />
    <div class="relative">
      <input
        :id="field.field_name"
        :name="field.field_name"
        type="date"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('validate')"
        :required="field.is_required"
        class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
        :class="{
          'border-blue-500 ring-2 ring-blue-100': modelValue && !validationError,
          'border-red-500 ring-2 ring-red-100': validationError
        }"
      />
      <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </div>
    </div>
    <FieldError :error="validationError" :description="field.description" />
  </div>
</template>

<script setup>
import FieldLabel from "./FieldLabel.vue"
import FieldError from "./FieldError.vue"

defineProps({
  field: {
    type: Object,
    required: true
  },
  modelValue: {
    type: String,
    default: ""
  },
  validationError: {
    type: String,
    default: ""
  }
})

defineEmits(["update:modelValue", "validate"])
</script>

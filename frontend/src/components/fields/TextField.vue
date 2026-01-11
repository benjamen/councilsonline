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
        type="text"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('validate')"
        :required="field.is_required"
        class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
        :class="{
          'border-blue-500 ring-2 ring-blue-100': modelValue && !validationError,
          'border-red-500 ring-2 ring-red-100': validationError
        }"
        :placeholder="placeholder"
      />
      <div v-if="icon" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <span v-html="icon" class="text-gray-400"></span>
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
    type: [String, Number],
    default: ""
  },
  validationError: {
    type: String,
    default: ""
  },
  placeholder: {
    type: String,
    default: ""
  },
  icon: {
    type: String,
    default: ""
  }
})

defineEmits(["update:modelValue", "validate"])
</script>

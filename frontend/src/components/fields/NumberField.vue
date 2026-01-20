<template>
  <div class="form-group">
    <FieldLabel
      :field-name="field.field_name"
      :label="field.field_label"
      :required="Boolean(field.is_required)"
      :help-text="field.help_text || field.description"
    />
    <div class="relative">
      <div v-if="variant === 'currency'" class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <span class="text-gray-500 text-base font-medium">₱</span>
      </div>
      <input
        :id="field.field_name"
        :name="field.field_name"
        type="number"
        :value="modelValue"
        @input="$emit('update:modelValue', parseFloat($event.target.value) || 0)"
        @blur="$emit('validate')"
        :required="field.is_required"
        :step="variant === 'int' ? '1' : '0.01'"
        class="block w-full px-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
        :class="{
          'pl-10': variant === 'currency',
          'border-blue-500 ring-2 ring-blue-100': modelValue && !validationError,
          'border-red-500 ring-2 ring-red-100': validationError
        }"
        :placeholder="variant === 'currency' ? '0.00' : placeholder"
      />
      <div v-if="variant !== 'currency'" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
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
		type: Number,
		default: 0,
	},
	validationError: {
		type: String,
		default: "",
	},
	placeholder: {
		type: String,
		default: "",
	},
	variant: {
		type: String,
		default: "int", // "int", "float", or "currency"
		validator: (value) => ["int", "float", "currency"].includes(value),
	},
})

defineEmits(["update:modelValue", "validate"])
</script>

<template>
  <div class="form-group">
    <div class="flex items-start p-4 border rounded-lg hover:border-blue-300 transition-colors"
      :class="{
        'border-gray-200': !validationError,
        'border-red-500 bg-red-50': validationError
      }">
      <div class="flex items-center h-5">
        <input
          :id="field.field_name"
          :name="field.field_name"
          type="checkbox"
          :checked="modelValue"
          @change="$emit('update:modelValue', $event.target.checked)"
          @blur="$emit('validate')"
          :required="field.is_required"
          class="focus:ring-blue-500 h-5 w-5 text-blue-600 border-gray-300 rounded cursor-pointer"
        />
      </div>
      <div class="ml-3 text-sm">
        <label :for="field.field_name" class="font-medium text-gray-700 cursor-pointer">
          {{ field.field_label }}
          <span v-if="field.is_required" class="text-red-500 ml-1">*</span>
        </label>
        <FieldError :error="validationError" :description="field.description" />
      </div>
    </div>
  </div>
</template>

<script setup>
import FieldError from "./FieldError.vue"

defineProps({
  field: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: false
  },
  validationError: {
    type: String,
    default: ""
  }
})

defineEmits(["update:modelValue", "validate"])
</script>

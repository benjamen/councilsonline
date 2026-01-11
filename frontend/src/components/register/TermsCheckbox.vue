<template>
  <div class="flex items-start">
    <input
      id="terms"
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked)"
      type="checkbox"
      required
      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
    />
    <label for="terms" class="ml-2 block text-sm text-gray-700">
      I agree to the
      <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Terms of Service</a>
      and
      <a href="#" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
    </label>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div class="grid md:grid-cols-2 gap-4">
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
        Password <span class="text-red-500">*</span>
      </label>
      <Input
        id="password"
        :modelValue="password"
        @update:modelValue="$emit('update:password', $event)"
        type="password"
        required
        placeholder="Min. 8 characters"
        class="w-full"
        @input="$emit('validate-password')"
      />
      <p v-if="passwordError" class="mt-1 text-xs text-red-600">{{ passwordError }}</p>
      <p v-else-if="passwordStrength" class="mt-1 text-xs" :class="passwordStrengthClass">
        Password strength: {{ passwordStrength }}
      </p>
    </div>
    <div>
      <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">
        Confirm Password <span class="text-red-500">*</span>
      </label>
      <Input
        id="confirm_password"
        :modelValue="confirmPassword"
        @update:modelValue="$emit('update:confirmPassword', $event)"
        type="password"
        required
        placeholder="Repeat password"
        class="w-full"
        @blur="$emit('validate-password-match')"
      />
      <p v-if="confirmPasswordError" class="mt-1 text-xs text-red-600">{{ confirmPasswordError }}</p>
    </div>
  </div>
</template>

<script setup>
import { Input } from "frappe-ui"
import { computed } from "vue"

const props = defineProps({
	password: {
		type: String,
		default: "",
	},
	confirmPassword: {
		type: String,
		default: "",
	},
	passwordError: {
		type: String,
		default: "",
	},
	confirmPasswordError: {
		type: String,
		default: "",
	},
	passwordStrength: {
		type: String,
		default: "",
	},
})

defineEmits([
	"update:password",
	"update:confirmPassword",
	"validate-password",
	"validate-password-match",
])

const passwordStrengthClass = computed(() => {
	if (props.passwordStrength === "strong") return "text-green-600"
	if (props.passwordStrength === "medium") return "text-yellow-600"
	return "text-red-600"
})
</script>

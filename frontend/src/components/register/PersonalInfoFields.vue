<template>
  <div class="space-y-4">
    <!-- Personal Information -->
    <div class="grid md:grid-cols-2 gap-4">
      <div>
        <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
          First Name <span class="text-red-500">*</span>
        </label>
        <Input
          id="first_name"
          :modelValue="firstName"
          @update:modelValue="$emit('update:firstName', $event)"
          type="text"
          required
          placeholder="John"
          class="w-full"
        />
      </div>
      <div>
        <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
          Last Name <span class="text-red-500">*</span>
        </label>
        <Input
          id="last_name"
          :modelValue="lastName"
          @update:modelValue="$emit('update:lastName', $event)"
          type="text"
          required
          placeholder="Doe"
          class="w-full"
        />
      </div>
    </div>

    <!-- Contact Information -->
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
        Email Address <span class="text-red-500">*</span>
      </label>
      <Input
        id="email"
        :modelValue="email"
        @update:modelValue="$emit('update:email', $event)"
        type="email"
        required
        placeholder="you@example.com"
        class="w-full"
        @blur="$emit('validate-email')"
      />
      <p v-if="emailError" class="mt-1 text-xs text-red-600">{{ emailError }}</p>
    </div>

    <div>
      <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
        Phone Number <span class="text-red-500">*</span>
      </label>
      <input
        id="phone"
        :value="phone"
        @input="$emit('update:phone', $event.target.value)"
        type="tel"
        required
        placeholder="021 234 5678 or 09 123 4567"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        @blur="$emit('validate-phone')"
      />
      <p v-if="phoneError" class="mt-1 text-xs text-red-600">{{ phoneError }}</p>
      <p v-else class="mt-1 text-xs text-gray-500">NZ mobile (02x) or landline (03-09)</p>
    </div>
  </div>
</template>

<script setup>
import { Input } from "frappe-ui"

defineProps({
  firstName: {
    type: String,
    default: ""
  },
  lastName: {
    type: String,
    default: ""
  },
  email: {
    type: String,
    default: ""
  },
  phone: {
    type: String,
    default: ""
  },
  emailError: {
    type: String,
    default: ""
  },
  phoneError: {
    type: String,
    default: ""
  }
})

defineEmits([
  'update:firstName',
  'update:lastName',
  'update:email',
  'update:phone',
  'validate-email',
  'validate-phone'
])
</script>

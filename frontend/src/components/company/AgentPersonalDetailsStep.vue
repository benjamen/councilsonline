<template>
  <div class="space-y-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">Agent Type & Your Details</h2>

    <!-- Agent Business Type -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-3">
        Agent Type <span class="text-red-500">*</span>
      </label>
      <div class="grid grid-cols-2 gap-4">
        <button
          type="button"
          @click="$emit('update:agentType', 'Sole Trader')"
          :class="[
            'p-4 border-2 rounded-lg text-center transition',
            agentType === 'Sole Trader'
              ? 'border-blue-600 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <svg class="w-8 h-8 mx-auto mb-2" :class="agentType === 'Sole Trader' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <div class="text-sm font-medium" :class="agentType === 'Sole Trader' ? 'text-blue-900' : 'text-gray-700'">
            Sole Trader
          </div>
          <div class="text-xs text-gray-500 mt-1">Individual consultant</div>
        </button>
        <button
          type="button"
          @click="$emit('update:agentType', 'Company')"
          :class="[
            'p-4 border-2 rounded-lg text-center transition',
            agentType === 'Company'
              ? 'border-blue-600 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <svg class="w-8 h-8 mx-auto mb-2" :class="agentType === 'Company' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <div class="text-sm font-medium" :class="agentType === 'Company' ? 'text-blue-900' : 'text-gray-700'">
            Company
          </div>
          <div class="text-xs text-gray-500 mt-1">Consulting firm</div>
        </button>
      </div>
    </div>

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
    <div class="grid md:grid-cols-2 gap-4">
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
          placeholder="021 234 5678"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          @blur="$emit('validate-phone')"
        />
        <p v-if="phoneError" class="mt-1 text-xs text-red-600">{{ phoneError }}</p>
        <p v-else class="mt-1 text-xs text-gray-500">NZ mobile (02x) or landline (03-09)</p>
      </div>
    </div>

    <!-- Password -->
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
  </div>
</template>

<script setup>
import { Input } from "frappe-ui"
import { computed } from "vue"

const props = defineProps({
  agentType: {
    type: String,
    default: "Sole Trader"
  },
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
  password: {
    type: String,
    default: ""
  },
  confirmPassword: {
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
  },
  passwordError: {
    type: String,
    default: ""
  },
  confirmPasswordError: {
    type: String,
    default: ""
  },
  passwordStrength: {
    type: String,
    default: ""
  }
})

defineEmits([
  'update:agentType',
  'update:firstName',
  'update:lastName',
  'update:email',
  'update:phone',
  'update:password',
  'update:confirmPassword',
  'validate-email',
  'validate-phone',
  'validate-password',
  'validate-password-match'
])

const passwordStrengthClass = computed(() => {
  if (props.passwordStrength === "strong") return "text-green-600"
  if (props.passwordStrength === "medium") return "text-yellow-600"
  return "text-red-600"
})
</script>

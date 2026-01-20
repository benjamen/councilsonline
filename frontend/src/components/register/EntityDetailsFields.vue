<template>
  <div class="space-y-4">
    <!-- Company/Organisation Details -->
    <div v-if="requesterType === 'Company' || requesterType === 'Organisation'">
      <div class="space-y-4">
        <div>
          <label for="organization_name" class="block text-sm font-medium text-gray-700 mb-2">
            {{ requesterType === 'Company' ? 'Company Name' : 'Organisation Name' }} <span class="text-red-500">*</span>
          </label>
          <Input
            id="organization_name"
            :modelValue="organizationName"
            @update:modelValue="$emit('update:organizationName', $event)"
            type="text"
            required
            :placeholder="requesterType === 'Company' ? 'ABC Construction Ltd' : 'Community Trust'"
            class="w-full"
          />
        </div>
        <div v-if="requesterType === 'Company'">
          <label for="company_number" class="block text-sm font-medium text-gray-700 mb-2">
            Company Number (Optional)
          </label>
          <Input
            id="company_number"
            :modelValue="companyNumber"
            @update:modelValue="$emit('update:companyNumber', $event)"
            type="text"
            placeholder="1234567"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- Trust Details -->
    <div v-if="requesterType === 'Trust'">
      <label for="trust_name" class="block text-sm font-medium text-gray-700 mb-2">
        Trust Name <span class="text-red-500">*</span>
      </label>
      <Input
        id="trust_name"
        :modelValue="trustName"
        @update:modelValue="$emit('update:trustName', $event)"
        type="text"
        required
        placeholder="Smith Family Trust"
        class="w-full"
      />
    </div>
  </div>
</template>

<script setup>
import { Input } from "frappe-ui"

defineProps({
	requesterType: {
		type: String,
		required: true,
	},
	organizationName: {
		type: String,
		default: "",
	},
	companyNumber: {
		type: String,
		default: "",
	},
	trustName: {
		type: String,
		default: "",
	},
})

defineEmits([
	"update:organizationName",
	"update:companyNumber",
	"update:trustName",
])
</script>

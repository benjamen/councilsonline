<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Who is this application for?</h2>
    <p class="text-gray-600 mb-8">Provide applicant and property owner information</p>

    <div class="space-y-6">
      <div v-if="userCompanyAccount">
        <div class="mb-6">
          <h3 class="text-sm font-semibold text-gray-900 mb-3">Submitting As</h3>
          <div class="space-y-3">
            <label class="flex items-start space-x-3 cursor-pointer p-4 border-2 rounded-lg transition-colors" :class="localData.submitted_on_behalf_of === 'Myself' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
              <input
                type="radio"
                value="Myself"
                v-model="localData.submitted_on_behalf_of"
                class="mt-1"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Individual - Submit for Myself</div>
                <div class="text-sm text-gray-500">This application is submitted as an individual</div>
              </div>
            </label>
            <label class="flex items-start space-x-3 cursor-pointer p-4 border-2 rounded-lg transition-colors" :class="localData.submitted_on_behalf_of === 'Company' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
              <input
                type="radio"
                value="Company"
                v-model="localData.submitted_on_behalf_of"
                class="mt-1"
              />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Company - {{ userCompanyAccount.company_name }}</div>
                <div class="text-sm text-gray-500">Submit on behalf of your company account</div>
                <div class="text-xs text-blue-600 mt-1">You are logged in as: {{ userCompanyAccount.user_role }}</div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div class="border-t border-gray-200 pt-6 mt-6">
        <div class="mb-6">
          <h3 class="text-sm font-semibold text-gray-900 mb-3">Who is this application for?</h3>
          <div class="space-y-3">
            <label class="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                :value="false"
                v-model="localData.acting_on_behalf"
                class="mt-1"
              />
              <div>
                <div class="font-medium text-gray-900">This application is for myself</div>
                <div class="text-sm text-gray-500">I am the applicant submitting this request</div>
              </div>
            </label>
            <label class="flex items-start space-x-3 cursor-pointer">
              <input
                type="radio"
                :value="true"
                v-model="localData.acting_on_behalf"
                class="mt-1"
              />
              <div>
                <div class="font-medium text-gray-900">I am acting on behalf of a client</div>
                <div class="text-sm text-gray-500">I am an agent submitting this request for someone else</div>
              </div>
            </label>
          </div>
        </div>

        <div>
          <h3 class="text-sm font-semibold text-gray-900 mb-4">
            {{ localData.acting_on_behalf ? 'Client Information *' : 'Applicant Contact Information *' }}
          </h3>

          <div class="space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                <input
                  v-model="localData.applicant_name"
                  type="text"
                  placeholder="John Smith"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  :disabled="!localData.acting_on_behalf && userProfile"
                  required
                />
                <p v-if="!localData.acting_on_behalf" class="mt-1 text-xs text-gray-500">Auto-populated from your profile</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email Address *</label>
                <input
                  v-model="localData.applicant_email"
                  type="email"
                  placeholder="john@example.com"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  :disabled="!localData.acting_on_behalf && userProfile"
                  required
                />
                <p v-if="!localData.acting_on_behalf" class="mt-1 text-xs text-gray-500">Auto-populated from your profile</p>
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Contact Phone *</label>
                <input
                  v-model="localData.applicant_phone"
                  type="tel"
                  placeholder="021 123 4567"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">
                  {{ localData.acting_on_behalf ? 'Required for application processing' : 'Will be saved to your profile for future applications' }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Applicant Type *</label>
                <select
                  v-model="localData.applicant_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select applicant type</option>
                  <option value="Individual">Individual</option>
                  <option value="Company">Company</option>
                  <option value="Trust">Trust</option>
                  <option value="Partnership">Partnership</option>
                  <option value="Other">Other</option>
                </select>
                <p class="mt-1 text-xs text-gray-500">Type of entity making this application</p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 border-t border-gray-200 pt-6">
          <div class="flex items-start mb-4">
            <input
              type="checkbox"
              v-model="localData.applicant_is_not_owner"
              class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label class="ml-3 text-sm font-medium text-gray-700">
              I am not the property owner
            </label>
          </div>

          <div v-if="localData.applicant_is_not_owner" class="space-y-4 pl-7">
            <p class="text-xs text-gray-600 mb-4">
              Under Section 88 of the RMA, you must provide the property owner's contact details.
            </p>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Owner Name *</label>
                <input
                  v-model="localData.owner_name"
                  type="text"
                  placeholder="Property owner's full name"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  :required="localData.applicant_is_not_owner"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Owner Email</label>
                <input
                  v-model="localData.owner_email"
                  type="email"
                  placeholder="owner@example.com"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Owner Phone</label>
                <input
                  v-model="localData.owner_phone"
                  type="tel"
                  placeholder="021 123 4567"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Owner Address</label>
                <textarea
                  v-model="localData.owner_address"
                  rows="3"
                  placeholder="Owner's postal address"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  userProfile: {
    type: Object,
    default: null
  },
  userCompanyAccount: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

// Local data
const localData = ref({
  submitted_on_behalf_of: props.modelValue.submitted_on_behalf_of || 'Myself',
  acting_on_behalf: props.modelValue.acting_on_behalf || false,
  applicant_name: props.modelValue.applicant_name || '',
  applicant_email: props.modelValue.applicant_email || '',
  applicant_phone: props.modelValue.applicant_phone || '',
  applicant_type: props.modelValue.applicant_type || '',
  applicant_is_not_owner: props.modelValue.applicant_is_not_owner || false,
  owner_name: props.modelValue.owner_name || '',
  owner_email: props.modelValue.owner_email || '',
  owner_phone: props.modelValue.owner_phone || '',
  owner_address: props.modelValue.owner_address || ''
})

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  localData.value.submitted_on_behalf_of = newVal.submitted_on_behalf_of || 'Myself'
  localData.value.acting_on_behalf = newVal.acting_on_behalf || false
  localData.value.applicant_name = newVal.applicant_name || ''
  localData.value.applicant_email = newVal.applicant_email || ''
  localData.value.applicant_phone = newVal.applicant_phone || ''
  localData.value.applicant_type = newVal.applicant_type || ''
  localData.value.applicant_is_not_owner = newVal.applicant_is_not_owner || false
  localData.value.owner_name = newVal.owner_name || ''
  localData.value.owner_email = newVal.owner_email || ''
  localData.value.owner_phone = newVal.owner_phone || ''
  localData.value.owner_address = newVal.owner_address || ''
}, { deep: true })

// Watch local changes and emit
watch(localData, (newVal) => {
  emit('update:modelValue', {
    ...props.modelValue,
    submitted_on_behalf_of: newVal.submitted_on_behalf_of,
    acting_on_behalf: newVal.acting_on_behalf,
    applicant_name: newVal.applicant_name,
    applicant_email: newVal.applicant_email,
    applicant_phone: newVal.applicant_phone,
    applicant_type: newVal.applicant_type,
    applicant_is_not_owner: newVal.applicant_is_not_owner,
    owner_name: newVal.owner_name,
    owner_email: newVal.owner_email,
    owner_phone: newVal.owner_phone,
    owner_address: newVal.owner_address
  })
}, { deep: true })
</script>

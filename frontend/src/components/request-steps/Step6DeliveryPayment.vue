<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Delivery & Payment</h2>
    <p class="text-gray-600 mb-8">Choose how you'd like to receive documents and specify payment details</p>

    <div class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Delivery Preference *
        </label>
        <select
          v-model="localData.delivery_preference"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        >
          <option value="">Select preference</option>
          <option value="Email">Email</option>
          <option value="Post">Post</option>
          <option value="Portal">Portal (online account)</option>
        </select>
        <p class="mt-1 text-xs text-gray-500">How you'd like to receive council correspondence and decision documents</p>
      </div>

      <div class="border-t border-gray-200 pt-6">
        <div class="flex items-start mb-4">
          <input
            type="checkbox"
            v-model="localData.transfer_deposit_required"
            class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label class="ml-3 text-sm font-medium text-gray-700">
            Transfer deposit from existing consent
          </label>
        </div>

        <div v-if="localData.transfer_deposit_required" class="pl-7">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Existing Consent Number *
          </label>
          <input
            v-model="localData.transfer_deposit_consent_number"
            type="text"
            placeholder="e.g., RC123456"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :required="localData.transfer_deposit_required"
          />
          <p class="mt-1 text-xs text-gray-500">
            Enter the consent number from which the deposit should be transferred
          </p>
        </div>
      </div>

      <div class="border-t border-gray-200 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Invoice Details</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Invoice To *
            </label>
            <select
              v-model="localData.invoice_to"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select who should receive the invoice</option>
              <option value="Applicant">Applicant</option>
              <option value="Other">Other (specify below)</option>
            </select>
          </div>

          <div v-if="localData.invoice_to === 'Other'" class="space-y-4 pl-4 border-l-4 border-blue-200">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Invoice Recipient Name *
              </label>
              <input
                v-model="localData.invoice_name"
                type="text"
                placeholder="Full name or company name"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :required="localData.invoice_to === 'Other'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Invoice Recipient Email *
              </label>
              <input
                v-model="localData.invoice_email"
                type="email"
                placeholder="invoice@example.com"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :required="localData.invoice_to === 'Other'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Invoice Recipient Address
              </label>
              <textarea
                v-model="localData.invoice_address"
                rows="3"
                placeholder="Recipient postal address"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Invoice Recipient GST/VAT Number
              </label>
              <input
                v-model="localData.invoice_tax_id"
                type="text"
                placeholder="e.g., 123-456-789"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p class="mt-1 text-xs text-gray-500">Provide if applicable</p>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps, ref, watch } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

// Local data
const localData = ref({
	delivery_preference: props.modelValue.delivery_preference || "",
	transfer_deposit_required:
		props.modelValue.transfer_deposit_required || false,
	transfer_deposit_consent_number:
		props.modelValue.transfer_deposit_consent_number || "",
	invoice_to: props.modelValue.invoice_to || "",
	invoice_name: props.modelValue.invoice_name || "",
	invoice_email: props.modelValue.invoice_email || "",
	invoice_address: props.modelValue.invoice_address || "",
	invoice_tax_id: props.modelValue.invoice_tax_id || "",
})

// Watch for external changes
watch(
	() => props.modelValue,
	(newVal) => {
		localData.value.delivery_preference = newVal.delivery_preference || ""
		localData.value.transfer_deposit_required =
			newVal.transfer_deposit_required || false
		localData.value.transfer_deposit_consent_number =
			newVal.transfer_deposit_consent_number || ""
		localData.value.invoice_to = newVal.invoice_to || ""
		localData.value.invoice_name = newVal.invoice_name || ""
		localData.value.invoice_email = newVal.invoice_email || ""
		localData.value.invoice_address = newVal.invoice_address || ""
		localData.value.invoice_tax_id = newVal.invoice_tax_id || ""
	},
	{ deep: true },
)

// Watch local changes and emit
watch(
	localData,
	(newVal) => {
		emit("update:modelValue", {
			...props.modelValue,
			delivery_preference: newVal.delivery_preference,
			transfer_deposit_required: newVal.transfer_deposit_required,
			transfer_deposit_consent_number: newVal.transfer_deposit_consent_number,
			invoice_to: newVal.invoice_to,
			invoice_name: newVal.invoice_name,
			invoice_email: newVal.invoice_email,
			invoice_address: newVal.invoice_address,
			invoice_tax_id: newVal.invoice_tax_id,
		})
	},
	{ deep: true },
)
</script>

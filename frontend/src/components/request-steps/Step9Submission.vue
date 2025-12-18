<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Declaration & Submission</h2>
    <p class="text-gray-600 mb-8">Payment of fees, statutory declarations, and application submission</p>

    <div class="space-y-8">
      <!-- Payment of Lodgement Fees (FRD 11.1) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Lodgement Fees</h3>
        </div>

        <div class="p-6 space-y-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h5 class="font-semibold text-blue-900 text-sm">About Lodgement Fees</h5>
                <p class="text-blue-800 text-sm mt-1">
                  Under s.36 RMA, councils can charge fees for processing resource consent applications.
                  Lodgement fees typically cover the initial administrative costs. Additional charges may be invoiced as the application is processed.
                </p>
              </div>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Have lodgement fees been paid?
            </label>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input
                  v-model="localData.lodgement_fees_paid"
                  type="radio"
                  :value="true"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">Yes</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="localData.lodgement_fees_paid"
                  type="radio"
                  :value="false"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm text-gray-700">No - will pay upon submission</span>
              </label>
            </div>
          </div>

          <!-- Payment Details (if fees paid) -->
          <div v-if="localData.lodgement_fees_paid" class="border-t border-gray-200 pt-4 space-y-4">
            <div class="flex justify-between items-center">
              <label class="block text-sm font-medium text-gray-700">
                Payment Records
              </label>
              <button
                @click="openPaymentModal"
                type="button"
                class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Payment
              </button>
            </div>

            <!-- Payment List -->
            <div v-if="localData.lodgement_payments && localData.lodgement_payments.length > 0" class="space-y-2">
              <div
                v-for="(payment, index) in localData.lodgement_payments"
                :key="index"
                class="border border-gray-200 rounded-lg p-3 bg-gray-50"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">{{ payment.payment_type }}</div>
                    <div class="text-sm text-gray-600 mt-1">
                      Amount: ${{ payment.amount_excluding_gst }} (excl GST)
                      <span v-if="payment.reference_number"> • Ref: {{ payment.reference_number }}</span>
                      <span v-if="payment.payment_date"> • Date: {{ formatDate(payment.payment_date) }}</span>
                    </div>
                  </div>
                  <button
                    @click="removePayment(index)"
                    type="button"
                    class="text-red-600 hover:text-red-800 p-1"
                    title="Remove"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Total -->
              <div class="border-t-2 border-gray-300 pt-3 mt-3">
                <div class="flex justify-between items-center font-semibold text-gray-900">
                  <span>Total Paid (excl GST):</span>
                  <span>${{ calculateTotalPayments() }}</span>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
              <p class="text-sm text-gray-500">No payments recorded yet</p>
            </div>
          </div>

          <!-- Payment Information (if not paid) -->
          <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-sm text-yellow-800">
              Lodgement fees will be calculated and invoiced by the council upon receipt of your application.
              You will be notified of the amount due and payment methods available.
            </p>
          </div>
        </div>
      </div>

      <!-- Statutory Declarations (FRD 11.2) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Statutory Declarations</h3>
        </div>

        <div class="p-6 space-y-6">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h5 class="font-semibold text-blue-900 text-sm">Declarations Required</h5>
                <p class="text-blue-800 text-sm mt-1">
                  Under the Resource Management Act 1991, you must confirm the following declarations before submitting your application.
                  All three declarations are mandatory.
                </p>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <div class="border-2 rounded-lg p-4" :class="localData.declaration_rma_compliance ? 'border-green-600 bg-green-50' : 'border-gray-200'">
              <label class="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  v-model="localData.declaration_rma_compliance"
                  required
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3 flex-1">
                  <span class="font-medium text-gray-900">RMA Compliance Declaration *</span>
                  <p class="text-sm text-gray-600 mt-1">
                    I confirm that this application complies with the requirements of Schedule 4 of the Resource Management Act 1991 and contains all required information for the council to process this application.
                  </p>
                </div>
              </label>
            </div>

            <div class="border-2 rounded-lg p-4" :class="localData.declaration_public_information ? 'border-green-600 bg-green-50' : 'border-gray-200'">
              <label class="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  v-model="localData.declaration_public_information"
                  required
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3 flex-1">
                  <span class="font-medium text-gray-900">Public Information Declaration *</span>
                  <p class="text-sm text-gray-600 mt-1">
                    I understand that this application and supporting documents will become public information and may be made available to any person upon request under the Local Government Official Information and Meetings Act 1987.
                  </p>
                </div>
              </label>
            </div>

            <div class="border-2 rounded-lg p-4" :class="localData.declaration_authorized ? 'border-green-600 bg-green-50' : 'border-gray-200'">
              <label class="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  v-model="localData.declaration_authorized"
                  required
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div class="ml-3 flex-1">
                  <span class="font-medium text-gray-900">Authorization Declaration *</span>
                  <p class="text-sm text-gray-600 mt-1">
                    I confirm that I am authorized to make this application on behalf of the applicant and that all information provided is true and correct to the best of my knowledge.
                  </p>
                </div>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Applicant Signatures (FRD 11.3) -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Applicant Signature(s)</h3>
        </div>

        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">
            If the application is being made by multiple applicants (e.g., multiple property owners), each applicant must provide their signature details.
          </p>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
              <input
                v-model="localData.requester_signature_first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
              <input
                v-model="localData.requester_signature_last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date *</label>
            <input
              v-model="localData.requester_signature_date"
              type="date"
              required
              :max="today"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div class="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <p class="text-xs text-gray-600">
              <strong>Note:</strong> By providing your name and date above, you are electronically signing this application.
              This has the same legal effect as a handwritten signature.
            </p>
          </div>
        </div>
      </div>

      <!-- Agent Signature (if applicable) (FRD 11.4) -->
      <div v-if="localData.agent_required" class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <h3 class="font-semibold text-gray-900">Agent Signature</h3>
        </div>

        <div class="p-6 space-y-4">
          <p class="text-sm text-gray-600">
            If an agent is acting on behalf of the applicant, the agent must also sign the application.
          </p>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
              <input
                v-model="localData.agent_signature_first_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
              <input
                v-model="localData.agent_signature_last_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date *</label>
            <input
              v-model="localData.agent_signature_date"
              type="date"
              required
              :max="today"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      <!-- Submission Ready Notice -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h5 class="font-semibold text-green-900 text-sm">Ready to Submit</h5>
            <p class="text-green-800 text-sm mt-1">
              Once you have completed all declarations and signatures, click "Submit Application" to lodge your resource consent application with the council.
              You will receive a confirmation email with your application reference number.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <Teleport to="body">
      <div
        v-if="showPaymentModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closePaymentModal"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
          <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">Add Payment Record</h3>
            <button @click="closePaymentModal" type="button" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Payment Type *</label>
              <select v-model="paymentForm.payment_type" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option value="">Select type</option>
                <option value="Lodgement Fee">Lodgement Fee</option>
                <option value="Deposit">Deposit</option>
                <option value="Processing Fee">Processing Fee</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Reference Number</label>
              <input v-model="paymentForm.reference_number" type="text" placeholder="e.g., Invoice #, Transaction ID" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Payment Date</label>
              <input v-model="paymentForm.payment_date" type="date" :max="today" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Amount (excl GST) *</label>
              <div class="relative">
                <span class="absolute left-3 top-2 text-gray-500">$</span>
                <input v-model.number="paymentForm.amount_excluding_gst" type="number" step="0.01" min="0" required placeholder="0.00" class="w-full pl-7 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
          </div>

          <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
            <button @click="closePaymentModal" type="button" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100">
              Cancel
            </button>
            <button @click="savePayment" type="button" :disabled="!paymentForm.payment_type || !paymentForm.amount_excluding_gst" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              Add Payment
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, ref } from "vue"

const props = defineProps({
	modelValue: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(["update:modelValue"])

const localData = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
})

// Today's date for max date validation
const today = new Date().toISOString().split("T")[0]

// Payment Modal Management
const showPaymentModal = ref(false)
const paymentForm = ref({
	payment_type: "",
	reference_number: "",
	payment_date: today,
	amount_excluding_gst: 0,
})

const openPaymentModal = () => {
	paymentForm.value = {
		payment_type: "",
		reference_number: "",
		payment_date: today,
		amount_excluding_gst: 0,
	}
	showPaymentModal.value = true
}

const closePaymentModal = () => {
	showPaymentModal.value = false
}

const savePayment = () => {
	if (
		!paymentForm.value.payment_type ||
		!paymentForm.value.amount_excluding_gst
	)
		return

	const updatedData = { ...props.modelValue }
	if (!updatedData.lodgement_payments) updatedData.lodgement_payments = []

	updatedData.lodgement_payments.push({ ...paymentForm.value })
	emit("update:modelValue", updatedData)
	closePaymentModal()
}

const removePayment = (index) => {
	if (confirm("Remove this payment record?")) {
		const updatedData = { ...props.modelValue }
		updatedData.lodgement_payments.splice(index, 1)
		emit("update:modelValue", updatedData)
	}
}

const calculateTotalPayments = () => {
	if (!localData.value.lodgement_payments) return 0
	return localData.value.lodgement_payments
		.reduce((total, payment) => total + (payment.amount_excluding_gst || 0), 0)
		.toFixed(2)
}

const formatDate = (dateString) => {
	if (!dateString) return ""
	const date = new Date(dateString)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
}
</script>

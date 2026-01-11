<template>
	<Dialog v-model="isOpen" :options="{ title: 'Payment Options', size: 'md' }">
		<template #body-content>
			<div class="space-y-6">
				<!-- Payment Summary -->
				<div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
					<div class="flex justify-between items-center mb-2">
						<span class="text-gray-700 font-medium">Total Amount (incl. GST)</span>
						<span class="text-2xl font-bold text-gray-900">
							${{ formatCurrency(totalAmount) }}
						</span>
					</div>
					<div class="text-sm text-gray-600 flex justify-between">
						<span>Fees: ${{ formatCurrency(feesExclGst) }} + GST ${{ formatCurrency(gst) }}</span>
					</div>
				</div>

				<!-- Payment Method: Invoice -->
				<div
					class="border-2 rounded-lg p-4 cursor-pointer transition-all"
					:class="{
						'border-blue-500 bg-blue-50': selectedMethod === 'invoice',
						'border-gray-200 hover:border-blue-300': selectedMethod !== 'invoice'
					}"
					@click="selectedMethod = 'invoice'"
				>
					<div class="flex items-start gap-3">
						<input
							type="radio"
							v-model="selectedMethod"
							value="invoice"
							class="mt-1"
						/>
						<div class="flex-1">
							<h3 class="font-medium text-gray-900 mb-1">Request Invoice</h3>
							<p class="text-sm text-gray-600">
								An invoice will be sent to your email. Pay via bank transfer or at council office.
							</p>
						</div>
					</div>
				</div>

				<!-- Payment Method: Online (Future - Stripe) -->
				<div
					v-if="stripeEnabled"
					class="border-2 rounded-lg p-4 cursor-pointer transition-all"
					:class="{
						'border-blue-500 bg-blue-50': selectedMethod === 'card',
						'border-gray-200 hover:border-blue-300': selectedMethod !== 'card'
					}"
					@click="selectedMethod = 'card'"
				>
					<div class="flex items-start gap-3">
						<input
							type="radio"
							v-model="selectedMethod"
							value="card"
							class="mt-1"
						/>
						<div class="flex-1">
							<h3 class="font-medium text-gray-900 mb-1">Pay Now (Credit/Debit Card)</h3>
							<p class="text-sm text-gray-600 mb-2">
								Pay securely online with Stripe. Instant confirmation.
							</p>
							<div class="text-xs text-gray-500">Visa, Mastercard, Amex accepted</div>
						</div>
					</div>
				</div>

				<!-- Error Message -->
				<div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-3">
					<div class="flex gap-2">
						<svg class="h-5 w-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<p class="text-sm text-red-800">{{ error }}</p>
					</div>
				</div>
			</div>
		</template>

		<template #actions>
			<Button variant="subtle" @click="isOpen = false" :disabled="processing">
				Cancel
			</Button>
			<Button
				variant="solid"
				@click="handleProceed"
				:loading="processing"
				:disabled="!selectedMethod"
			>
				{{ selectedMethod === 'card' ? 'Proceed to Payment' : 'Request Invoice' }}
			</Button>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, Button, createResource } from 'frappe-ui'

const props = defineProps({
	show: Boolean,
	requestId: String,
	totalAmount: Number,
	feesExclGst: Number,
	gst: Number,
	stripeEnabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:show', 'invoice-requested', 'payment-initiated'])

const selectedMethod = ref('invoice')
const processing = ref(false)
const error = ref(null)

// Computed property for v-model on Dialog
const isOpen = computed({
	get() {
		return props.show
	},
	set(value) {
		emit('update:show', value)
	}
})

// Create resource for invoice request
const invoiceResource = createResource({
	url: 'lodgeick.api.request_invoice',
	makeParams(values) {
		return {
			request_id: values.requestId
		}
	},
	onSuccess(data) {
		if (data.success) {
			emit('invoice-requested', data)
			emit('update:show', false)
		} else {
			error.value = data.error || 'Failed to request invoice'
		}
		processing.value = false
	},
	onError(err) {
		error.value = err.message || 'An error occurred while requesting invoice'
		processing.value = false
	}
})

const handleProceed = async () => {
	error.value = null
	processing.value = true

	try {
		if (selectedMethod.value === 'invoice') {
			await requestInvoice()
		} else if (selectedMethod.value === 'card') {
			await initiateStripePayment()
		}
	} catch (err) {
		error.value = err.message || 'An unexpected error occurred'
		processing.value = false
	}
}

const requestInvoice = async () => {
	invoiceResource.submit({ requestId: props.requestId })
}

const initiateStripePayment = async () => {
	// Phase 2: Stripe integration
	emit('payment-initiated')
	processing.value = false
	alert('Stripe integration coming soon!')
}

const formatCurrency = (amount) => {
	if (!amount) return '0.00'
	return new Intl.NumberFormat('en-NZ', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2
	}).format(amount)
}
</script>

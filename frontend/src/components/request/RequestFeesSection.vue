<template>
	<div>
		<!-- Fees & Payments (Council collects from user) -->
		<div v-if="collectPayment" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<div class="flex justify-between items-center mb-4">
				<h2 class="text-lg font-semibold text-gray-900">Fees & Payments</h2>
				<span class="text-sm font-medium" :class="paymentStatus === 'Paid' ? 'text-green-600' : 'text-orange-600'">
					{{ paymentStatus || 'Unpaid' }}
				</span>
			</div>

			<div class="space-y-3">
				<div class="flex justify-between items-center py-2 border-b border-gray-100">
					<span class="text-sm text-gray-600">Total Fees</span>
					<span class="text-sm font-semibold text-gray-900">${{ totalFees.toFixed(2) }}</span>
				</div>
				<div class="flex justify-between items-center py-2 border-b border-gray-100">
					<span class="text-sm text-gray-600">Total Paid</span>
					<span class="text-sm font-semibold text-green-600">${{ totalPaid.toFixed(2) }}</span>
				</div>
				<div class="flex justify-between items-center py-2">
					<span class="text-sm font-medium text-gray-900">Outstanding</span>
					<span class="text-sm font-bold text-orange-600">${{ (totalFees - totalPaid).toFixed(2) }}</span>
				</div>
			</div>

			<Button
				v-if="totalFees > totalPaid"
				@click="$emit('make-payment')"
				variant="solid"
				theme="blue"
				class="w-full mt-4"
			>
				Make Payment
			</Button>
		</div>

		<!-- Payment to be Received (Council pays user - benefits) -->
		<div v-if="makePayment" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<div class="flex justify-between items-center mb-4">
				<h2 class="text-lg font-semibold text-gray-900">Payment to be Received</h2>
				<span class="text-sm font-medium" :class="paymentStatus === 'Paid' ? 'text-green-600' : 'text-orange-600'">
					{{ paymentStatus || 'Pending' }}
				</span>
			</div>

			<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
				<div class="flex items-start">
					<svg class="h-5 w-5 text-blue-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<div class="flex-1">
						<p class="text-sm font-medium text-blue-900">Benefit Payment Information</p>
						<p class="text-sm text-blue-700 mt-1">
							Once your application is approved, you will receive payment from the council.
							Please ensure your bank details are up to date.
						</p>
					</div>
				</div>
			</div>

			<div class="space-y-3">
				<div class="flex justify-between items-center py-2 border-b border-gray-100">
					<span class="text-sm text-gray-600">Benefit Amount</span>
					<span class="text-sm font-semibold text-gray-900">
						${{ benefitAmount.toFixed(2) }}
					</span>
				</div>
				<div class="flex justify-between items-center py-2 border-b border-gray-100">
					<span class="text-sm text-gray-600">Payment Status</span>
					<span class="text-sm font-semibold" :class="paymentStatus === 'Paid' ? 'text-green-600' : 'text-orange-600'">
						{{ paymentStatus || 'Pending Approval' }}
					</span>
				</div>
				<div v-if="selectedBankAccount" class="flex justify-between items-center py-2">
					<span class="text-sm text-gray-600">Payment Method</span>
					<span class="text-sm font-medium text-gray-900">Bank Transfer</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui"

const props = defineProps({
	// Show collect payment section
	collectPayment: {
		type: Boolean,
		default: false
	},
	// Show make payment section (benefits)
	makePayment: {
		type: Boolean,
		default: false
	},
	// Payment status
	paymentStatus: {
		type: String,
		default: null
	},
	// For collect payment section
	totalFees: {
		type: Number,
		default: 0
	},
	totalPaid: {
		type: Number,
		default: 0
	},
	// For make payment section (benefits)
	benefitAmount: {
		type: Number,
		default: 0
	},
	selectedBankAccount: {
		type: String,
		default: null
	}
})

defineEmits(['make-payment'])
</script>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
	// Title and description
	title: {
		type: String,
		required: true
	},
	subtitle: {
		type: String,
		default: null
	},

	// Navigation
	showBackButton: {
		type: Boolean,
		default: true
	},
	backRoute: {
		type: String,
		default: null // If null, uses router.back()
	},

	// Loading state
	loading: {
		type: Boolean,
		default: false
	}
})

const emit = defineEmits(['back'])
const router = useRouter()

const handleBack = () => {
	emit('back')
	if (props.backRoute) {
		router.push(props.backRoute)
	} else {
		router.back()
	}
}
</script>

<template>
	<header class="bg-white shadow-sm border-b border-gray-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between py-4">
				<!-- Left: Back button + Title -->
				<div class="flex items-center space-x-3">
					<button
						v-if="showBackButton"
						@click="handleBack"
						class="text-gray-500 hover:text-gray-700 transition-colors"
						aria-label="Go back"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
						</svg>
					</button>

					<div v-if="!loading">
						<h1 class="text-xl font-bold text-gray-900">{{ title }}</h1>
						<p v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</p>
					</div>

					<div v-else class="flex items-center space-x-2">
						<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
						<span class="text-sm text-gray-500">Loading...</span>
					</div>
				</div>

				<!-- Right: Actions slot -->
				<div class="flex items-center space-x-3">
					<slot name="actions"></slot>
				</div>
			</div>
		</div>
	</header>
</template>

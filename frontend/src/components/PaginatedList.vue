<script setup>
import { ref, computed, watch } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
	// Total number of items (from API)
	total: {
		type: Number,
		required: true
	},
	// Items per page
	pageSize: {
		type: Number,
		default: 20
	},
	// Current page (1-indexed)
	currentPage: {
		type: Number,
		default: 1
	},
	// Loading state
	loading: {
		type: Boolean,
		default: false
	}
})

const emit = defineEmits(['page-change', 'page-size-change'])

// Computed
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

const pageNumbers = computed(() => {
	const pages = []
	const maxVisible = 7 // Show max 7 page numbers

	if (totalPages.value <= maxVisible) {
		// Show all pages if total is small
		for (let i = 1; i <= totalPages.value; i++) {
			pages.push(i)
		}
	} else {
		// Show first, last, current, and nearby pages
		const current = props.currentPage
		const start = Math.max(2, current - 1)
		const end = Math.min(totalPages.value - 1, current + 1)

		pages.push(1) // Always show first page

		if (start > 2) {
			pages.push('...')
		}

		for (let i = start; i <= end; i++) {
			pages.push(i)
		}

		if (end < totalPages.value - 1) {
			pages.push('...')
		}

		if (totalPages.value > 1) {
			pages.push(totalPages.value) // Always show last page
		}
	}

	return pages
})

const canGoPrevious = computed(() => props.currentPage > 1)
const canGoNext = computed(() => props.currentPage < totalPages.value)

// Methods
const goToPage = (page) => {
	if (page === '...' || page === props.currentPage || props.loading) return
	if (page < 1 || page > totalPages.value) return
	emit('page-change', page)
}

const previousPage = () => {
	if (canGoPrevious.value) {
		goToPage(props.currentPage - 1)
	}
}

const nextPage = () => {
	if (canGoNext.value) {
		goToPage(props.currentPage + 1)
	}
}

const changePageSize = (event) => {
	const newSize = parseInt(event.target.value)
	emit('page-size-change', newSize)
}

// Info text
const itemRangeText = computed(() => {
	if (props.total === 0) return '0 items'

	const start = (props.currentPage - 1) * props.pageSize + 1
	const end = Math.min(props.currentPage * props.pageSize, props.total)

	return `${start}-${end} of ${props.total} items`
})
</script>

<template>
	<div class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
		<!-- Left: Page size selector and info -->
		<div class="flex items-center space-x-4">
			<div class="flex items-center space-x-2">
				<label for="page-size" class="text-sm text-gray-700">Show:</label>
				<select
					id="page-size"
					:value="pageSize"
					@change="changePageSize"
					:disabled="loading"
					class="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
				>
					<option :value="10">10</option>
					<option :value="20">20</option>
					<option :value="50">50</option>
					<option :value="100">100</option>
				</select>
			</div>

			<div class="text-sm text-gray-700">
				{{ itemRangeText }}
			</div>
		</div>

		<!-- Right: Pagination controls -->
		<div class="flex items-center space-x-2">
			<!-- Previous button -->
			<Button
				@click="previousPage"
				:disabled="!canGoPrevious || loading"
				variant="outline"
				size="sm"
			>
				Previous
			</Button>

			<!-- Page numbers -->
			<div class="hidden sm:flex space-x-1">
				<button
					v-for="(page, index) in pageNumbers"
					:key="index"
					@click="goToPage(page)"
					:disabled="loading || page === '...'"
					:class="[
						'px-3 py-1 text-sm rounded',
						page === currentPage
							? 'bg-blue-600 text-white font-medium'
							: page === '...'
							? 'cursor-default text-gray-400'
							: 'text-gray-700 hover:bg-gray-100 transition-colors'
					]"
				>
					{{ page }}
				</button>
			</div>

			<!-- Next button -->
			<Button
				@click="nextPage"
				:disabled="!canGoNext || loading"
				variant="outline"
				size="sm"
			>
				Next
			</Button>
		</div>
	</div>
</template>

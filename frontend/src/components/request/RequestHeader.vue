<script setup>
defineProps({
	title: {
		type: String,
		required: true
	},
	description: {
		type: String,
		default: null
	},
	category: {
		type: String,
		default: null
	}
})
</script>

<template>
	<div class="mb-8">
		<div class="flex items-start justify-between">
			<div>
				<div v-if="category" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mb-2">
					{{ category }}
				</div>
				<h1 class="text-3xl font-bold text-gray-900">{{ title }}</h1>
				<p v-if="description" class="mt-2 text-gray-600">{{ description }}</p>
			</div>
		</div>
	</div>
</template>

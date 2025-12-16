<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
	items: {
		type: Array,
		required: true
	},
	itemHeight: {
		type: Number,
		default: 60 // Default row height in pixels
	},
	buffer: {
		type: Number,
		default: 5 // Number of items to render above/below visible area
	},
	containerHeight: {
		type: Number,
		default: 600 // Container height in pixels
	}
})

const emit = defineEmits(['item-click'])

// Refs
const scrollContainer = ref(null)
const scrollTop = ref(0)

// Computed properties
const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleStart = computed(() => {
	const start = Math.floor(scrollTop.value / props.itemHeight) - props.buffer
	return Math.max(0, start)
})

const visibleEnd = computed(() => {
	const end = Math.ceil((scrollTop.value + props.containerHeight) / props.itemHeight) + props.buffer
	return Math.min(props.items.length, end)
})

const visibleItems = computed(() => {
	return props.items.slice(visibleStart.value, visibleEnd.value).map((item, index) => ({
		...item,
		virtualIndex: visibleStart.value + index
	}))
})

const offsetY = computed(() => visibleStart.value * props.itemHeight)

// Methods
const handleScroll = (event) => {
	scrollTop.value = event.target.scrollTop
}

const handleItemClick = (item) => {
	emit('item-click', item)
}

// Lifecycle
onMounted(() => {
	if (scrollContainer.value) {
		scrollContainer.value.addEventListener('scroll', handleScroll, { passive: true })
	}
})

onUnmounted(() => {
	if (scrollContainer.value) {
		scrollContainer.value.removeEventListener('scroll', handleScroll)
	}
})

// Reset scroll when items change significantly
watch(() => props.items.length, () => {
	if (scrollContainer.value) {
		scrollContainer.value.scrollTop = 0
		scrollTop.value = 0
	}
})
</script>

<template>
	<div
		ref="scrollContainer"
		class="virtual-scroll-container overflow-y-auto"
		:style="{ height: `${containerHeight}px` }"
	>
		<div
			class="virtual-scroll-spacer"
			:style="{ height: `${totalHeight}px`, position: 'relative' }"
		>
			<div
				class="virtual-scroll-content"
				:style="{ transform: `translateY(${offsetY}px)` }"
			>
				<slot
					name="item"
					v-for="item in visibleItems"
					:key="item.name || item.virtualIndex"
					:item="item"
					:index="item.virtualIndex"
					:on-click="() => handleItemClick(item)"
				/>
			</div>
		</div>

		<!-- Empty state -->
		<div v-if="items.length === 0" class="flex items-center justify-center h-full text-gray-500">
			<slot name="empty">
				<p>No items to display</p>
			</slot>
		</div>
	</div>
</template>

<style scoped>
.virtual-scroll-container {
	position: relative;
	overflow-x: hidden;
}

.virtual-scroll-content {
	will-change: transform;
}
</style>

<template>
  <div class="inline-block relative group">
    <slot name="trigger">
      <button
        type="button"
        class="inline-flex items-center justify-center w-5 h-5 ml-1 text-gray-400 hover:text-blue-600 rounded-full hover:bg-blue-50 transition-colors cursor-help"
        @mouseenter="showTooltip = true"
        @mouseleave="showTooltip = false"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
        </svg>
      </button>
    </slot>

    <Transition name="tooltip">
      <div
        v-if="showTooltip"
        class="absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg pointer-events-none"
        :class="tooltipPositionClass"
        style="max-width: 300px; white-space: normal;"
      >
        <slot>{{ text }}</slot>
        <div class="tooltip-arrow" :class="arrowPositionClass"></div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"

const props = defineProps({
	text: {
		type: String,
		default: "",
	},
	position: {
		type: String,
		default: "top",
		validator: (value) => ["top", "bottom", "left", "right"].includes(value),
	},
})

const showTooltip = ref(false)

const tooltipPositionClass = computed(() => {
	switch (props.position) {
		case "top":
			return "bottom-full left-1/2 -translate-x-1/2 mb-2"
		case "bottom":
			return "top-full left-1/2 -translate-x-1/2 mt-2"
		case "left":
			return "right-full top-1/2 -translate-y-1/2 mr-2"
		case "right":
			return "left-full top-1/2 -translate-y-1/2 ml-2"
		default:
			return "bottom-full left-1/2 -translate-x-1/2 mb-2"
	}
})

const arrowPositionClass = computed(() => {
	switch (props.position) {
		case "top":
			return "tooltip-arrow-bottom"
		case "bottom":
			return "tooltip-arrow-top"
		case "left":
			return "tooltip-arrow-right"
		case "right":
			return "tooltip-arrow-left"
		default:
			return "tooltip-arrow-bottom"
	}
})
</script>

<style scoped>
.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
}

.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border-style: solid;
}

.tooltip-arrow-bottom {
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px 4px 0 4px;
  border-color: #1f2937 transparent transparent transparent;
}

.tooltip-arrow-top {
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 0 4px 4px 4px;
  border-color: transparent transparent #1f2937 transparent;
}

.tooltip-arrow-right {
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 4px 0 4px 4px;
  border-color: transparent transparent transparent #1f2937;
}

.tooltip-arrow-left {
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  border-width: 4px 4px 4px 0;
  border-color: transparent #1f2937 transparent transparent;
}
</style>

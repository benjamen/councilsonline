<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-3">
      Account Type <span class="text-red-500">*</span>
    </label>
    <p class="text-xs text-gray-500 mb-3">Select the entity type you're registering as</p>
    <div class="grid grid-cols-2 gap-3">
      <button
        type="button"
        @click="$emit('update:modelValue', 'Individual')"
        :class="[
          'p-4 border-2 rounded-lg text-center transition',
          modelValue === 'Individual'
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        <svg class="w-8 h-8 mx-auto mb-2" :class="modelValue === 'Individual' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <div class="text-sm font-medium" :class="modelValue === 'Individual' ? 'text-blue-900' : 'text-gray-700'">
          Individual
        </div>
        <div class="text-xs text-gray-500 mt-1">Person/Civilian</div>
      </button>
      <button
        type="button"
        @click="$emit('update:modelValue', 'Company')"
        :class="[
          'p-4 border-2 rounded-lg text-center transition',
          modelValue === 'Company'
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        <svg class="w-8 h-8 mx-auto mb-2" :class="modelValue === 'Company' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <div class="text-sm font-medium" :class="modelValue === 'Company' ? 'text-blue-900' : 'text-gray-700'">
          Company
        </div>
        <div class="text-xs text-gray-500 mt-1">NZ Registered</div>
      </button>
      <button
        type="button"
        @click="$emit('update:modelValue', 'Trust')"
        :class="[
          'p-4 border-2 rounded-lg text-center transition',
          modelValue === 'Trust'
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        <svg class="w-8 h-8 mx-auto mb-2" :class="modelValue === 'Trust' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <div class="text-sm font-medium" :class="modelValue === 'Trust' ? 'text-blue-900' : 'text-gray-700'">
          Trust
        </div>
        <div class="text-xs text-gray-500 mt-1">Trust Entity</div>
      </button>
      <button
        type="button"
        @click="$emit('update:modelValue', 'Organisation')"
        :class="[
          'p-4 border-2 rounded-lg text-center transition',
          modelValue === 'Organisation'
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        ]"
      >
        <svg class="w-8 h-8 mx-auto mb-2" :class="modelValue === 'Organisation' ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <div class="text-sm font-medium" :class="modelValue === 'Organisation' ? 'text-blue-900' : 'text-gray-700'">
          Organisation
        </div>
        <div class="text-xs text-gray-500 mt-1">Charity/NPO</div>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: "Individual"
  }
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="contact-selector-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeModal"></div>

      <!-- Center modal -->
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <!-- Header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-900" id="contact-selector-title">
              Select or Add Contact
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Tab Navigation -->
          <div class="border-b border-gray-200 mb-6">
            <nav class="-mb-px flex space-x-8">
              <button
                @click="activeTab = 'existing'"
                :class="[
                  'py-2 px-1 border-b-2 font-medium text-sm',
                  activeTab === 'existing'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Existing Contacts
              </button>
              <button
                @click="activeTab = 'new'"
                :class="[
                  'py-2 px-1 border-b-2 font-medium text-sm',
                  activeTab === 'new'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                Add New Contact
              </button>
            </nav>
          </div>

          <!-- Existing Contacts Tab -->
          <div v-if="activeTab === 'existing'" class="space-y-4">
            <!-- Search -->
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search contacts by name or email..."
                class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            <!-- Contact List -->
            <div class="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
              <div v-if="filteredContacts.length === 0" class="p-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <p class="mt-2">No contacts found</p>
              </div>

              <div v-for="contact in filteredContacts" :key="contact.name || contact.email"
                @click="selectContact(contact)"
                class="p-4 border-b border-gray-200 hover:bg-blue-50 cursor-pointer transition-colors">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="font-medium text-gray-900">{{ contact.name }}</p>
                    <p class="text-sm text-gray-600">{{ contact.email }}</p>
                    <p v-if="contact.phone" class="text-sm text-gray-500">{{ contact.phone }}</p>
                    <p v-if="contact.organization" class="text-xs text-gray-500 mt-1">{{ contact.organization }}</p>
                  </div>
                  <svg class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- New Contact Tab -->
          <div v-if="activeTab === 'new'" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                <input
                  v-model="newContact.name"
                  type="text"
                  required
                  placeholder="e.g., John Smith"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <input
                  v-model="newContact.email"
                  type="email"
                  required
                  placeholder="john@example.com"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <input
                  v-model="newContact.phone"
                  type="tel"
                  placeholder="+64 21 123 4567"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Organization</label>
                <input
                  v-model="newContact.organization"
                  type="text"
                  placeholder="e.g., Planning Consultants Ltd"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
                <input
                  v-model="newContact.role"
                  type="text"
                  placeholder="e.g., Project Manager, Architect"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div class="flex items-start">
              <input
                v-model="saveToContacts"
                type="checkbox"
                id="save-contact"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
              />
              <label for="save-contact" class="ml-2 text-sm text-gray-700">
                Save this contact for future use
              </label>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-3">
          <button
            v-if="activeTab === 'new'"
            @click="addNewContact"
            :disabled="!newContact.name || !newContact.email"
            class="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add Contact
          </button>

          <button
            @click="closeModal"
            class="mt-3 sm:mt-0 w-full sm:w-auto inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  existingContacts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'select'])

const activeTab = ref('existing')
const searchQuery = ref('')
const saveToContacts = ref(true)

const newContact = ref({
  name: '',
  email: '',
  phone: '',
  organization: '',
  role: ''
})

// Filter contacts based on search query
const filteredContacts = computed(() => {
  if (!searchQuery.value) {
    return props.existingContacts
  }

  const query = searchQuery.value.toLowerCase()
  return props.existingContacts.filter(contact => {
    return (
      contact.name?.toLowerCase().includes(query) ||
      contact.email?.toLowerCase().includes(query) ||
      contact.organization?.toLowerCase().includes(query)
    )
  })
})

// Watch for modal open/close to reset state
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    activeTab.value = 'existing'
    searchQuery.value = ''
    resetNewContact()
  }
})

const closeModal = () => {
  emit('close')
}

const selectContact = (contact) => {
  emit('select', contact)
  closeModal()
}

const addNewContact = () => {
  if (!newContact.value.name || !newContact.value.email) {
    return
  }

  emit('select', {
    ...newContact.value,
    isNew: true,
    saveToContacts: saveToContacts.value
  })

  resetNewContact()
  closeModal()
}

const resetNewContact = () => {
  newContact.value = {
    name: '',
    email: '',
    phone: '',
    organization: '',
    role: ''
  }
  saveToContacts.value = true
}
</script>

<style scoped>
/* Modal animations */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>

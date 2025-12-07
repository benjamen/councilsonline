<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Council-branded Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-3">
            <button @click="goBack" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <!-- Council Logo -->
            <div v-if="councilSettings?.logo" class="h-8">
              <img :src="councilSettings.logo" :alt="councilSettings.council_name" class="h-full object-contain" />
            </div>
            <div v-else class="w-8 h-8 rounded flex items-center justify-center" :style="{ backgroundColor: primaryColor }">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">My Account</h1>
              <p class="text-xs text-gray-500">{{ councilSettings?.council_name || councilCode }}</p>
            </div>
          </div>

          <div v-if="councilSettings?.allow_system_wide_dashboard" class="text-sm">
            <router-link :to="{ name: 'Settings' }" class="text-gray-600 hover:text-gray-900">
              View All Councils →
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2" :style="{ borderColor: primaryColor }"></div>
        <p class="mt-4 text-gray-500">Loading account information...</p>
      </div>

      <div v-else class="space-y-6">
        <!-- Profile Card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Profile Information</h2>

          <!-- Profile Image -->
          <div class="flex items-center space-x-6 mb-8">
            <div class="w-24 h-24 rounded-full flex items-center justify-center" :style="{ backgroundColor: `${primaryColor}20`, color: primaryColor }">
              <span v-if="!profile.user_image" class="text-3xl font-bold">
                {{ userInitials }}
              </span>
              <img v-else :src="profile.user_image" alt="Profile" class="w-full h-full rounded-full object-cover" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ profile.full_name }}</h3>
              <p class="text-sm text-gray-500">{{ profile.email }}</p>
              <p class="text-xs text-gray-400 mt-1">Member since {{ formatDate(profile.creation) }}</p>
            </div>
          </div>

          <form @submit.prevent="updateProfile" class="space-y-6">
            <!-- Personal Information -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                <Input v-model="profileForm.first_name" type="text" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                <Input v-model="profileForm.last_name" type="text" required />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Mobile Phone</label>
                <Input v-model="profileForm.mobile_no" type="tel" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <Input v-model="profileForm.phone" type="tel" />
              </div>
            </div>

            <div class="flex justify-end space-x-4">
              <Button @click="resetProfileForm" variant="outline" theme="gray">
                Cancel
              </Button>
              <Button type="submit" variant="solid" :loading="saving" :style="{ backgroundColor: primaryColor, borderColor: primaryColor }">
                Save Changes
              </Button>
            </div>
          </form>
        </div>

        <!-- Council Information Card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Council Information</h2>
          <p class="text-gray-600 mb-6">You are registered with {{ councilSettings?.council_name || councilCode }}</p>

          <div class="p-6 rounded-lg" :style="{ backgroundColor: `${primaryColor}10`, borderLeft: `4px solid ${primaryColor}` }">
            <div class="flex items-start space-x-4">
              <div v-if="councilSettings?.logo" class="h-16 flex-shrink-0">
                <img :src="councilSettings.logo" :alt="councilSettings.council_name" class="h-full object-contain" />
              </div>
              <div v-else class="w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0" :style="{ backgroundColor: primaryColor }">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 text-lg mb-2">{{ councilSettings?.council_name }}</h3>
                <p v-if="councilSettings?.official_name" class="text-sm text-gray-600 mb-3">{{ councilSettings.official_name }}</p>

                <div class="space-y-2 text-sm">
                  <div v-if="councilSettings?.contact_email" class="flex items-center text-gray-700">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {{ councilSettings.contact_email }}
                  </div>
                  <div v-if="councilSettings?.contact_phone" class="flex items-center text-gray-700">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    {{ councilSettings.contact_phone }}
                  </div>
                  <div v-if="councilSettings?.website" class="flex items-center text-gray-700">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    <a :href="councilSettings.website" target="_blank" class="hover:underline" :style="{ color: primaryColor }">
                      {{ councilSettings.website }}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <router-link
              :to="{ name: 'CouncilDashboard', params: { councilCode } }"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5" :style="{ color: primaryColor }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span class="font-medium text-gray-900">My Requests</span>
              </div>
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </router-link>

            <router-link
              :to="{ name: 'NewRequest', query: { council: councilCode, locked: 'true' } }"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5" :style="{ color: primaryColor }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span class="font-medium text-gray-900">New Application</span>
              </div>
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </router-link>
          </div>
        </div>

        <!-- Security Card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Security</h2>
          <p class="text-gray-600 mb-6">Manage your password and security settings</p>

          <button
            @click="changePasswordModal = true"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            Change Password
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Input, Button, call } from 'frappe-ui'
import { useCouncilStore } from '../stores/councilStore'
import { userResource } from '../data/user'

const router = useRouter()
const route = useRoute()
const councilStore = useCouncilStore()

const councilCode = computed(() => route.params.councilCode?.toUpperCase())
const councilSettings = ref(null)
const isLoading = ref(true)
const saving = ref(false)
const changePasswordModal = ref(false)

// Profile data
const profile = ref({})
const profileForm = ref({
  first_name: '',
  last_name: '',
  mobile_no: '',
  phone: '',
})

// Computed
const primaryColor = computed(() => councilSettings.value?.primary_color || '#2563eb')

const userInitials = computed(() => {
  const name = profile.value.full_name || ''
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
})

// Load data
onMounted(async () => {
  try {
    // Load council settings
    councilSettings.value = await councilStore.getCouncilSettings(councilCode.value)

    // Load user profile from userResource
    await userResource.promise
    profile.value = userResource.data || {}

    // Initialize form
    profileForm.value = {
      first_name: profile.value.first_name || '',
      last_name: profile.value.last_name || '',
      mobile_no: profile.value.mobile_no || '',
      phone: profile.value.phone || '',
    }
  } catch (error) {
    console.error('Failed to load account data:', error)
  } finally {
    isLoading.value = false
  }
})

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-NZ', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Update profile
const updateProfile = async () => {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'User',
      name: profile.value.name,
      fieldname: profileForm.value
    })

    // Reload user resource
    await userResource.reload()
    profile.value = userResource.data || {}

    alert('Profile updated successfully!')
  } catch (error) {
    console.error('Failed to update profile:', error)
    alert('Failed to update profile. Please try again.')
  } finally {
    saving.value = false
  }
}

const resetProfileForm = () => {
  profileForm.value = {
    first_name: profile.value.first_name || '',
    last_name: profile.value.last_name || '',
    mobile_no: profile.value.mobile_no || '',
    phone: profile.value.phone || '',
  }
}

const goBack = () => {
  router.push({ name: 'CouncilDashboard', params: { councilCode: councilCode.value } })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-3">
            <button @click="goBack" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Settings</h1>
              <p class="text-xs text-gray-500">Manage your profile and preferences</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar Navigation -->
        <div class="lg:col-span-1">
          <nav class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="currentTab = tab.key"
              class="w-full text-left px-4 py-3 rounded-lg transition-colors mb-2"
              :class="currentTab === tab.key ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'"
            >
              <div class="flex items-center space-x-3">
                <component :is="tab.icon" class="w-5 h-5" />
                <span>{{ tab.label }}</span>
              </div>
            </button>
          </nav>
        </div>

        <!-- Content Area -->
        <div class="lg:col-span-3">
          <!-- Loading State -->
          <div v-if="profileLoading" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-500">Loading settings...</p>
          </div>

          <!-- Profile Tab -->
          <div v-else-if="currentTab === 'profile'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Profile Information</h2>

            <form @submit.prevent="updateProfile" class="space-y-6">
              <!-- Profile Image -->
              <div class="flex items-center space-x-6">
                <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center">
                  <span v-if="!profile.user_image" class="text-3xl font-bold text-blue-600">
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

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Location</label>
                <Input v-model="profileForm.location" type="text" placeholder="City, Country" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                <textarea
                  v-model="profileForm.bio"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Tell us about yourself..."
                ></textarea>
              </div>

              <div class="flex justify-end space-x-4">
                <Button @click="resetProfileForm" variant="outline" theme="gray">
                  Cancel
                </Button>
                <Button type="submit" variant="solid" theme="blue" :loading="saving">
                  Save Changes
                </Button>
              </div>
            </form>
          </div>

          <!-- Organization Tab (for suppliers) -->
          <div v-else-if="currentTab === 'organization'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Organization Details</h2>
            <p class="text-gray-600 mb-6">Manage your organization information</p>

            <div v-if="!profile.organization_data" class="text-center py-12">
              <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">No Organization Linked</h3>
              <p class="text-gray-500">Contact an administrator to link your account to an organization</p>
            </div>

            <form v-else @submit.prevent="updateOrganization" class="space-y-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Organization Name</label>
                <Input v-model="orgForm.organization_name" type="text" required />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                  <Input v-model="orgForm.contact_email" type="email" required />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Contact Phone</label>
                  <Input v-model="orgForm.contact_phone" type="tel" required />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
                <Input v-model="orgForm.address" type="text" />
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">City</label>
                  <Input v-model="orgForm.city" type="text" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Postal Code</label>
                  <Input v-model="orgForm.postal_code" type="text" />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Website</label>
                <Input v-model="orgForm.website" type="url" placeholder="https://example.com" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  v-model="orgForm.description"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe your organization..."
                ></textarea>
              </div>

              <div class="flex justify-end space-x-4">
                <Button @click="resetOrgForm" variant="outline" theme="gray">
                  Cancel
                </Button>
                <Button type="submit" variant="solid" theme="blue" :loading="saving">
                  Save Changes
                </Button>
              </div>
            </form>
          </div>

          <!-- Security Tab -->
          <div v-else-if="currentTab === 'security'" class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Security Settings</h2>
            <p class="text-gray-600 mb-6">Update your password and security preferences</p>

            <form @submit.prevent="changePassword" class="space-y-6 max-w-md">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                <Input v-model="passwordForm.old_password" type="password" required />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                <Input v-model="passwordForm.new_password" type="password" required />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                <Input v-model="passwordForm.confirm_password" type="password" required />
              </div>

              <div v-if="passwordError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p class="text-sm text-red-600">{{ passwordError }}</p>
              </div>

              <div v-if="passwordSuccess" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <p class="text-sm text-green-600">{{ passwordSuccess }}</p>
              </div>

              <div class="flex justify-end space-x-4">
                <Button @click="resetPasswordForm" variant="outline" theme="gray">
                  Cancel
                </Button>
                <Button type="submit" variant="solid" theme="blue" :loading="changingPassword">
                  Change Password
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { Button, Input, call } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

// Tab state
const currentTab = ref("profile")
const tabs = [
	{ key: "profile", label: "Profile", icon: "user-icon" },
	{ key: "organization", label: "Organization", icon: "office-icon" },
	{ key: "security", label: "Security", icon: "lock-icon" },
]

// Profile state
const profile = ref({})
const profileLoading = ref(true)
const saving = ref(false)
const changingPassword = ref(false)
const passwordError = ref("")
const passwordSuccess = ref("")

// Forms
const profileForm = ref({
	first_name: "",
	last_name: "",
	mobile_no: "",
	phone: "",
	bio: "",
	location: "",
	default_council: "",
})

const orgForm = ref({
	organization_name: "",
	contact_email: "",
	contact_phone: "",
	address: "",
	city: "",
	postal_code: "",
	website: "",
	description: "",
})

const passwordForm = ref({
	old_password: "",
	new_password: "",
	confirm_password: "",
})

// Computed
const userInitials = computed(() => {
	if (!profile.value.first_name) return "??"
	const firstInitial = profile.value.first_name[0] || ""
	const lastInitial = profile.value.last_name?.[0] || ""
	return (firstInitial + lastInitial).toUpperCase()
})

// Methods
const loadProfile = async () => {
	profileLoading.value = true
	try {
		const data = await call("lodgeick.api.get_user_profile")
		profile.value = data

		// Populate forms
		profileForm.value = {
			first_name: data.first_name || "",
			last_name: data.last_name || "",
			mobile_no: data.mobile_no || "",
			phone: data.phone || "",
			bio: data.bio || "",
			location: data.location || "",
			default_council: data.default_council || "",
		}

		if (data.organization_data) {
			orgForm.value = {
				organization_name: data.organization_data.organization_name || "",
				contact_email: data.organization_data.contact_email || "",
				contact_phone: data.organization_data.contact_phone || "",
				address: data.organization_data.address || "",
				city: data.organization_data.city || "",
				postal_code: data.organization_data.postal_code || "",
				website: data.organization_data.website || "",
				description: data.organization_data.description || "",
			}
		}
	} catch (error) {
		console.error("Error loading profile:", error)
	} finally {
		profileLoading.value = false
	}
}

const updateProfile = async () => {
	saving.value = true
	try {
		const result = await call(
			"lodgeick.api.update_user_profile",
			profileForm.value,
		)
		profile.value = result.user
		alert("Profile updated successfully")
	} catch (error) {
		console.error("Error updating profile:", error)
		alert("Failed to update profile")
	} finally {
		saving.value = false
	}
}

const updateCouncil = async () => {
	saving.value = true
	try {
		const result = await call("lodgeick.api.update_user_profile", {
			default_council: profileForm.value.default_council,
		})
		profile.value = result.user
		alert("Council preference updated successfully")
	} catch (error) {
		console.error("Error updating council:", error)
		alert("Failed to update council preference")
	} finally {
		saving.value = false
	}
}

const updateOrganization = async () => {
	saving.value = true
	try {
		const result = await call(
			"lodgeick.api.update_user_organization",
			orgForm.value,
		)
		profile.value.organization_data = result.organization
		alert("Organization updated successfully")
	} catch (error) {
		console.error("Error updating organization:", error)
		alert("Failed to update organization")
	} finally {
		saving.value = false
	}
}

const changePassword = async () => {
	passwordError.value = ""
	passwordSuccess.value = ""

	if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
		passwordError.value = "New passwords do not match"
		return
	}

	if (passwordForm.value.new_password.length < 6) {
		passwordError.value = "Password must be at least 6 characters"
		return
	}

	changingPassword.value = true
	try {
		await call("lodgeick.api.change_password", {
			old_password: passwordForm.value.old_password,
			new_password: passwordForm.value.new_password,
		})
		passwordSuccess.value = "Password changed successfully"
		resetPasswordForm()
	} catch (error) {
		console.error("Error changing password:", error)
		passwordError.value = error.message || "Failed to change password"
	} finally {
		changingPassword.value = false
	}
}

const resetProfileForm = () => {
	profileForm.value = {
		first_name: profile.value.first_name || "",
		last_name: profile.value.last_name || "",
		mobile_no: profile.value.mobile_no || "",
		phone: profile.value.phone || "",
		bio: profile.value.bio || "",
		location: profile.value.location || "",
		default_council: profile.value.default_council || "",
	}
}

const resetCouncilForm = () => {
	profileForm.value.default_council = profile.value.default_council || ""
}

const resetOrgForm = () => {
	if (profile.value.organization_data) {
		orgForm.value = {
			organization_name:
				profile.value.organization_data.organization_name || "",
			contact_email: profile.value.organization_data.contact_email || "",
			contact_phone: profile.value.organization_data.contact_phone || "",
			address: profile.value.organization_data.address || "",
			city: profile.value.organization_data.city || "",
			postal_code: profile.value.organization_data.postal_code || "",
			website: profile.value.organization_data.website || "",
			description: profile.value.organization_data.description || "",
		}
	}
}

const resetPasswordForm = () => {
	passwordForm.value = {
		old_password: "",
		new_password: "",
		confirm_password: "",
	}
}

const formatDate = (dateStr) => {
	if (!dateStr) return "N/A"
	const date = new Date(dateStr)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "long",
		day: "numeric",
	})
}

const goBack = () => {
	router.back()
}

onMounted(() => {
	loadProfile()
})
</script>

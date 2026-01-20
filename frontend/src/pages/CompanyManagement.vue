<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Company Account Management</h1>
            <p class="text-gray-600 mt-2">Manage your company profile, users, and permissions</p>
          </div>
          <router-link
            :to="{ name: 'Dashboard' }"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </router-link>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="text-gray-600 mt-4">Loading company account...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="flex items-start">
          <svg class="w-6 h-6 text-red-600 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-lg font-semibold text-red-900">Error Loading Company Account</h3>
            <p class="text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div v-else-if="companyAccount" class="space-y-6">
        <!-- Company Profile Card -->
        <div class="bg-white rounded-lg shadow border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-semibold text-gray-900">Company Profile</h2>
              <Button
                v-if="isAdmin"
                @click="editMode = !editMode"
                variant="outline"
                class="text-sm"
              >
                {{ editMode ? 'Cancel' : 'Edit Profile' }}
              </Button>
            </div>
          </div>
          <div class="p-6">
            <form v-if="editMode" @submit.prevent="updateCompanyProfile" class="space-y-6">
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                  <Input v-model="editForm.company_name" type="text" required class="w-full" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Legal Name</label>
                  <Input v-model="editForm.legal_name" type="text" required class="w-full" />
                </div>
              </div>
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Primary Email</label>
                  <Input v-model="editForm.primary_email" type="email" required class="w-full" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Primary Phone</label>
                  <Input v-model="editForm.primary_phone" type="tel" required class="w-full" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Registered Office Address</label>
                <textarea v-model="editForm.registered_office_address" required rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div class="flex items-center justify-end space-x-3">
                <Button type="button" @click="cancelEdit" variant="outline">Cancel</Button>
                <Button type="submit" :loading="updating" variant="solid" class="bg-blue-600 hover:bg-blue-700 text-white">
                  Save Changes
                </Button>
              </div>
            </form>
            <div v-else class="space-y-4">
              <div class="grid md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-500">Company Name</label>
                  <p class="text-gray-900 font-medium mt-1">{{ companyAccount.company_name }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-500">Legal Name</label>
                  <p class="text-gray-900 mt-1">{{ companyAccount.legal_name }}</p>
                </div>
                <div v-if="companyAccount.nzbn">
                  <label class="block text-sm font-medium text-gray-500">NZBN</label>
                  <p class="text-gray-900 mt-1">{{ companyAccount.nzbn }}</p>
                </div>
                <div v-if="companyAccount.company_type">
                  <label class="block text-sm font-medium text-gray-500">Company Type</label>
                  <p class="text-gray-900 mt-1">{{ companyAccount.company_type }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-500">Primary Email</label>
                  <p class="text-gray-900 mt-1">{{ companyAccount.primary_email }}</p>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-500">Primary Phone</label>
                  <p class="text-gray-900 mt-1">{{ companyAccount.primary_phone }}</p>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-500">Registered Office Address</label>
                <p class="text-gray-900 mt-1">{{ companyAccount.registered_office_address }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- User Management Card -->
        <div class="bg-white rounded-lg shadow border border-gray-200">
          <div class="p-6 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">Team Members</h2>
                <p class="text-sm text-gray-600 mt-1">Manage users and their permissions</p>
              </div>
              <Button
                v-if="isAdmin"
                @click="showInviteModal = true"
                variant="solid"
                class="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Invite User
              </Button>
            </div>
          </div>
          <div class="p-6">
            <!-- Admin Users -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Administrators</h3>
              <div class="space-y-3">
                <div
                  v-for="admin in adminUsers"
                  :key="admin.name"
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div class="flex items-center space-x-4">
                    <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                      {{ getInitials(admin.user) }}
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">{{ admin.user }}</p>
                      <p class="text-sm text-gray-600">{{ admin.designation }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-3">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Admin
                    </span>
                    <Button
                      v-if="isAdmin && admin.user !== currentUser"
                      @click="confirmRemoveUser(admin.user, 'Admin')"
                      variant="outline"
                      class="text-red-600 hover:text-red-700 border-red-300 hover:border-red-400"
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Linked Users -->
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Team Members</h3>
              <div v-if="linkedUsers.length === 0" class="text-center py-8 text-gray-500">
                No team members yet. Invite users to collaborate on applications.
              </div>
              <div v-else class="space-y-3">
                <div
                  v-for="user in linkedUsers"
                  :key="user.name"
                  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div class="flex items-center space-x-4">
                    <div class="w-10 h-10 rounded-full bg-gray-400 flex items-center justify-center text-white font-semibold">
                      {{ getInitials(user.user) }}
                    </div>
                    <div>
                      <p class="font-medium text-gray-900">{{ user.user }}</p>
                      <p class="text-sm text-gray-600">Added {{ formatDate(user.added_date) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-3">
                    <select
                      v-if="isAdmin"
                      :value="user.role"
                      @change="updateUserRole(user.user, $event.target.value)"
                      class="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="Submitter">Submitter</option>
                      <option value="Viewer">Viewer</option>
                    </select>
                    <span
                      v-else
                      :class="[
                        'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                        user.role === 'Submitter' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      ]"
                    >
                      {{ user.role }}
                    </span>
                    <Button
                      v-if="isAdmin"
                      @click="confirmRemoveUser(user.user, user.role)"
                      variant="outline"
                      class="text-red-600 hover:text-red-700 border-red-300 hover:border-red-400"
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">Invite User</h3>
            <button @click="closeInviteModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <form @submit.prevent="sendInvitation" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <Input v-model="inviteForm.email" type="email" required placeholder="user@example.com" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <select v-model="inviteForm.role" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <option value="Admin">Admin - Full access, can manage users and billing</option>
              <option value="Submitter">Submitter - Can create and submit applications</option>
              <option value="Viewer">Viewer - Can only view applications</option>
            </select>
          </div>
          <div v-if="inviteForm.role === 'Admin'">
            <label class="block text-sm font-medium text-gray-700 mb-2">Designation</label>
            <Input v-model="inviteForm.designation" type="text" placeholder="Manager, Director, etc." class="w-full" />
          </div>
          <div v-if="inviteError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-700">{{ inviteError }}</p>
          </div>
          <div class="flex items-center justify-end space-x-3 pt-4">
            <Button type="button" @click="closeInviteModal" variant="outline">Cancel</Button>
            <Button type="submit" :loading="inviting" variant="solid" class="bg-blue-600 hover:bg-blue-700 text-white">
              Send Invitation
            </Button>
          </div>
        </form>
      </div>
    </div>

    <!-- Remove User Confirmation Modal -->
    <div v-if="showRemoveModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Remove User</h3>
        <p class="text-gray-700 mb-6">
          Are you sure you want to remove <strong>{{ userToRemove?.email }}</strong> from the company account?
        </p>
        <div class="flex items-center justify-end space-x-3">
          <Button @click="showRemoveModal = false" variant="outline">Cancel</Button>
          <Button @click="removeUser" :loading="removing" variant="solid" class="bg-red-600 hover:bg-red-700 text-white">
            Remove User
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, Input } from "frappe-ui"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const loading = ref(true)
const error = ref(null)
const companyAccount = ref(null)
const currentUser = ref(null)
const userRole = ref(null)

const editMode = ref(false)
const editForm = ref({})
const updating = ref(false)

const showInviteModal = ref(false)
const inviteForm = ref({ email: "", role: "Submitter", designation: "" })
const inviting = ref(false)
const inviteError = ref(null)

const showRemoveModal = ref(false)
const userToRemove = ref(null)
const removing = ref(false)

const adminUsers = ref([])
const linkedUsers = ref([])

const isAdmin = computed(() => userRole.value === "Admin")

onMounted(async () => {
	await loadCompanyAccount()
	await loadUsers()
})

async function loadCompanyAccount() {
	loading.value = true
	error.value = null

	try {
		const response = await fetch(
			"/api/method/councilsonline.api.get_user_company_account",
			{
				method: "GET",
				headers: {
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
			},
		)
		const data = await response.json()

		if (data.message) {
			companyAccount.value = data.message
			userRole.value = data.message.user_role
			currentUser.value = data.message.current_user

			// Initialize edit form
			editForm.value = { ...data.message }
		} else {
			error.value = "No company account found for this user"
		}
	} catch (err) {
		error.value = "Failed to load company account"
		console.error("Error loading company account:", err)
	} finally {
		loading.value = false
	}
}

async function loadUsers() {
	try {
		const response = await fetch("/api/method/councilsonline.api.get_company_users", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": window.csrf_token,
			},
			body: JSON.stringify({ company_name: companyAccount.value.name }),
		})
		const data = await response.json()

		if (data.message) {
			adminUsers.value = data.message.admin_users || []
			linkedUsers.value = data.message.linked_users || []
		}
	} catch (err) {
		console.error("Error loading users:", err)
	}
}

function cancelEdit() {
	editMode.value = false
	editForm.value = { ...companyAccount.value }
}

async function updateCompanyProfile() {
	updating.value = true

	try {
		const response = await fetch(
			"/api/method/councilsonline.api.update_company_account",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					company_name: companyAccount.value.name,
					updates: editForm.value,
				}),
			},
		)
		const data = await response.json()

		if (data.message && data.message.success) {
			companyAccount.value = { ...companyAccount.value, ...editForm.value }
			editMode.value = false
		} else {
			alert("Failed to update company profile")
		}
	} catch (err) {
		console.error("Error updating company:", err)
		alert("Failed to update company profile")
	} finally {
		updating.value = false
	}
}

function closeInviteModal() {
	showInviteModal.value = false
	inviteForm.value = { email: "", role: "Submitter", designation: "" }
	inviteError.value = null
}

async function sendInvitation() {
	inviting.value = true
	inviteError.value = null

	try {
		const response = await fetch(
			"/api/method/councilsonline.api.send_company_invitation",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					company_name: companyAccount.value.name,
					email: inviteForm.value.email,
					role: inviteForm.value.role,
					designation: inviteForm.value.designation,
				}),
			},
		)
		const data = await response.json()

		if (data.message && data.message.success) {
			closeInviteModal()
			await loadUsers()
		} else {
			inviteError.value = data.message?.message || "Failed to send invitation"
		}
	} catch (err) {
		console.error("Error sending invitation:", err)
		inviteError.value = "Failed to send invitation"
	} finally {
		inviting.value = false
	}
}

function confirmRemoveUser(email, role) {
	userToRemove.value = { email, role }
	showRemoveModal.value = true
}

async function removeUser() {
	removing.value = true

	try {
		const response = await fetch(
			"/api/method/councilsonline.api.remove_user_from_company",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					company_name: companyAccount.value.name,
					user_email: userToRemove.value.email,
				}),
			},
		)
		const data = await response.json()

		if (data.message && data.message.success) {
			showRemoveModal.value = false
			userToRemove.value = null
			await loadUsers()
		} else {
			alert(data.message?.message || "Failed to remove user")
		}
	} catch (err) {
		console.error("Error removing user:", err)
		alert("Failed to remove user")
	} finally {
		removing.value = false
	}
}

async function updateUserRole(email, newRole) {
	try {
		const response = await fetch(
			"/api/method/councilsonline.api.update_user_company_role",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": window.csrf_token,
				},
				body: JSON.stringify({
					company_name: companyAccount.value.name,
					user_email: email,
					new_role: newRole,
				}),
			},
		)
		const data = await response.json()

		if (data.message && data.message.success) {
			await loadUsers()
		} else {
			alert("Failed to update user role")
		}
	} catch (err) {
		console.error("Error updating user role:", err)
		alert("Failed to update user role")
	}
}

function getInitials(email) {
	if (!email) return "?"
	const parts = email.split("@")[0].split(".")
	if (parts.length >= 2) {
		return (parts[0][0] + parts[1][0]).toUpperCase()
	}
	return email.substring(0, 2).toUpperCase()
}

function formatDate(dateStr) {
	if (!dateStr) return "N/A"
	const date = new Date(dateStr)
	return date.toLocaleDateString("en-NZ", {
		year: "numeric",
		month: "short",
		day: "numeric",
	})
}
</script>

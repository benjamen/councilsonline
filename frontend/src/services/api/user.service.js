import { apiClient } from "./base"

/**
 * User Service
 * Handles user authentication, profile, and preferences
 */
export class UserService {
	/**
	 * Get current user info
	 * @returns {Object} Frappe resource
	 */
	getCurrentUser() {
		return apiClient.createResource({
			url: "frappe.auth.get_logged_user",
			auto: true,
			cache: ["current-user"],
		})
	}

	/**
	 * Get user profile
	 * @param {string} email - User email (optional, defaults to current user)
	 * @returns {Object} Frappe resource
	 */
	getUserProfile(email = null) {
		return apiClient.createResource({
			url: "frappe.client.get",
			params: {
				doctype: "User",
				name: email || frappe.session.user,
			},
			auto: true,
		})
	}

	/**
	 * Update user profile
	 * @param {Object} fields - Fields to update
	 * @returns {Promise<void>}
	 */
	async updateProfile(fields) {
		return apiClient.call("frappe.client.set_value", {
			doctype: "User",
			name: frappe.session.user,
			fieldname: fields,
		})
	}

	/**
	 * Login user
	 * @param {string} email - User email
	 * @param {string} password - User password
	 * @returns {Promise<Object>} Login result
	 */
	async login(email, password) {
		return apiClient.call("login", {
			usr: email,
			pwd: password,
		})
	}

	/**
	 * Logout current user
	 * @returns {Promise<void>}
	 */
	async logout() {
		return apiClient.call("logout")
	}

	/**
	 * Register new user
	 * @param {Object} userData - User registration data
	 * @returns {Promise<Object>} Registration result
	 */
	async register(userData) {
		return apiClient.call("lodgeick.api.register_user", userData)
	}

	/**
	 * Request password reset
	 * @param {string} email - User email
	 * @returns {Promise<void>}
	 */
	async requestPasswordReset(email) {
		return apiClient.call("frappe.core.doctype.user.user.reset_password", {
			user: email,
		})
	}

	/**
	 * Update password
	 * @param {string} oldPassword - Current password
	 * @param {string} newPassword - New password
	 * @returns {Promise<void>}
	 */
	async updatePassword(oldPassword, newPassword) {
		return apiClient.call("frappe.core.doctype.user.user.update_password", {
			old_password: oldPassword,
			new_password: newPassword,
		})
	}

	/**
	 * Get user permissions
	 * @returns {Promise<Object>} User permissions
	 */
	async getUserPermissions() {
		return apiClient.call(
			"frappe.core.page.permission_manager.permission_manager.get_permissions",
		)
	}

	/**
	 * Check if user has role
	 * @param {string} role - Role name
	 * @returns {Promise<boolean>} True if user has role
	 */
	async hasRole(role) {
		const result = await apiClient.call(
			"frappe.core.doctype.user.user.has_role",
			{
				role,
			},
		)
		return result
	}

	/**
	 * Get user preferences
	 * @returns {Promise<Object>} User preferences
	 */
	async getUserPreferences() {
		return apiClient.call("lodgeick.api.get_user_preferences")
	}

	/**
	 * Update user preferences
	 * @param {Object} preferences - Preferences to update
	 * @returns {Promise<void>}
	 */
	async updateUserPreferences(preferences) {
		return apiClient.call("lodgeick.api.update_user_preferences", {
			preferences,
		})
	}

	/**
	 * Get user's organizations (if applicant is linked to organizations)
	 * @returns {Promise<Array>} User organizations
	 */
	async getUserOrganizations() {
		return apiClient.call("lodgeick.api.get_user_organizations")
	}
}

export const userService = new UserService()

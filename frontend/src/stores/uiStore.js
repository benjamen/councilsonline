import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
	state: () => ({
		// Modal states
		modals: {},

		// Loading states
		loadingStates: {},

		// Toast notifications
		toasts: [],

		// Sidebar state
		sidebarOpen: true,

		// Mobile menu state
		mobileMenuOpen: false
	}),

	getters: {
		isModalOpen: (state) => (modalName) => {
			return state.modals[modalName] === true
		},

		isLoading: (state) => (key) => {
			return state.loadingStates[key] === true
		},

		hasActiveToasts: (state) => state.toasts.length > 0
	},

	actions: {
		/**
		 * Open modal
		 * @param {String} modalName - Modal identifier
		 */
		openModal(modalName) {
			this.modals[modalName] = true
		},

		/**
		 * Close modal
		 * @param {String} modalName - Modal identifier
		 */
		closeModal(modalName) {
			this.modals[modalName] = false
		},

		/**
		 * Toggle modal
		 * @param {String} modalName - Modal identifier
		 */
		toggleModal(modalName) {
			this.modals[modalName] = !this.modals[modalName]
		},

		/**
		 * Set loading state
		 * @param {String} key - Loading state key
		 * @param {Boolean} isLoading - Loading state
		 */
		setLoading(key, isLoading) {
			this.loadingStates[key] = isLoading
		},

		/**
		 * Show toast notification
		 * @param {Object} toast - Toast configuration
		 */
		showToast(toast) {
			const toastObj = {
				id: Date.now() + Math.random(),
				message: toast.message,
				type: toast.type || 'info', // info, success, warning, error
				duration: toast.duration || 3000,
				action: toast.action || null,
				timestamp: new Date()
			}

			this.toasts.push(toastObj)

			// Auto-remove toast
			if (toastObj.duration > 0) {
				setTimeout(() => {
					this.removeToast(toastObj.id)
				}, toastObj.duration)
			}
		},

		/**
		 * Remove toast by ID
		 * @param {Number} toastId - Toast ID
		 */
		removeToast(toastId) {
			this.toasts = this.toasts.filter(t => t.id !== toastId)
		},

		/**
		 * Clear all toasts
		 */
		clearToasts() {
			this.toasts = []
		},

		/**
		 * Toggle sidebar
		 */
		toggleSidebar() {
			this.sidebarOpen = !this.sidebarOpen
		},

		/**
		 * Set sidebar state
		 * @param {Boolean} isOpen - Sidebar open state
		 */
		setSidebar(isOpen) {
			this.sidebarOpen = isOpen
		},

		/**
		 * Toggle mobile menu
		 */
		toggleMobileMenu() {
			this.mobileMenuOpen = !this.mobileMenuOpen
		},

		/**
		 * Set mobile menu state
		 * @param {Boolean} isOpen - Mobile menu open state
		 */
		setMobileMenu(isOpen) {
			this.mobileMenuOpen = isOpen
		}
	}
})

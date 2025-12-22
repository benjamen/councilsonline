import { ref, onMounted, onUnmounted } from 'vue'
import { useSocket } from '../socket'

/**
 * Composable for listening to real-time request updates
 * @param {string} requestId - The request ID to listen for updates
 * @param {Object} callbacks - Optional callbacks for different event types
 * @returns {Object} - Reactive state and helper functions
 */
export function useRequestUpdates(requestId, callbacks = {}) {
	const socket = useSocket()
	const lastUpdate = ref(null)
	const isConnected = ref(false)
	const updates = ref([])

	// Event handlers
	const handleStatusChange = (message) => {
		console.log('[Request Updates] Status changed:', message)
		lastUpdate.value = message
		updates.value.unshift(message)

		// Call custom callback if provided
		if (callbacks.onStatusChange) {
			callbacks.onStatusChange(message.data)
		}

		// Show notification
		if (window.frappe && window.frappe.show_alert) {
			window.frappe.show_alert({
				message: `Request status updated to: ${message.data.new_status}`,
				indicator: 'blue'
			}, 5)
		}
	}

	const handleWorkflowStateChange = (message) => {
		console.log('[Request Updates] Workflow state changed:', message)
		lastUpdate.value = message
		updates.value.unshift(message)

		// Call custom callback if provided
		if (callbacks.onWorkflowStateChange) {
			callbacks.onWorkflowStateChange(message.data)
		}

		// Show notification
		if (window.frappe && window.frappe.show_alert) {
			window.frappe.show_alert({
				message: `Workflow updated to: ${message.data.new_state}`,
				indicator: 'green'
			}, 5)
		}
	}

	const handleGenericUpdate = (message) => {
		console.log('[Request Updates] Generic update:', message)
		lastUpdate.value = message
		updates.value.unshift(message)

		// Call custom callback if provided
		if (callbacks.onUpdate) {
			callbacks.onUpdate(message)
		}
	}

	// Subscribe to request-specific updates
	const subscribe = () => {
		if (!socket || !requestId) {
			console.warn('[Request Updates] Socket not available or no request ID provided')
			return
		}

		try {
			isConnected.value = socket.connected

			// Listen for connection status
			socket.on('connect', () => {
				console.log('[Request Updates] Socket connected')
				isConnected.value = true
			})

			socket.on('disconnect', () => {
				console.log('[Request Updates] Socket disconnected')
				isConnected.value = false
			})

			// Subscribe to request-specific channel
			const requestChannel = `request_update:${requestId}`
			socket.on(requestChannel, (message) => {
				switch (message.event_type) {
					case 'status_changed':
						handleStatusChange(message)
						break
					case 'workflow_state_changed':
						handleWorkflowStateChange(message)
						break
					default:
						handleGenericUpdate(message)
				}
			})

			// Also listen to personal channel for all request updates
			socket.on('request_update', (message) => {
				// Only process if it's for this request
				if (message.request === requestId) {
					handleGenericUpdate(message)
				}
			})

			console.log(`[Request Updates] Subscribed to updates for request: ${requestId}`)
		} catch (error) {
			console.error('[Request Updates] Error subscribing:', error)
		}
	}

	// Unsubscribe from updates
	const unsubscribe = () => {
		if (!socket || !requestId) return

		try {
			const requestChannel = `request_update:${requestId}`
			socket.off(requestChannel)
			socket.off('request_update')
			socket.off('connect')
			socket.off('disconnect')

			console.log(`[Request Updates] Unsubscribed from updates for request: ${requestId}`)
		} catch (error) {
			console.error('[Request Updates] Error unsubscribing:', error)
		}
	}

	// Auto-subscribe on mount, unsubscribe on unmount
	onMounted(() => {
		if (requestId) {
			subscribe()
		}
	})

	onUnmounted(() => {
		unsubscribe()
	})

	return {
		lastUpdate,
		updates,
		isConnected,
		subscribe,
		unsubscribe
	}
}

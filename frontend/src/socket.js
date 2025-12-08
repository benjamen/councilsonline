import { io } from "socket.io-client"
import { socketio_port } from "../../../../sites/common_site_config.json"

let socket = null
let socketInitializationFailed = false

export function initSocket() {
	// Don't retry if initialization already failed
	if (socketInitializationFailed) {
		console.warn('[Socket.io] Skipping initialization - socketio server not available')
		return null
	}

	try {
		const host = window.location.hostname
		const siteName = window.site_name
		const port = window.location.port ? `:${socketio_port}` : ""
		const protocol = port ? "http" : "https"
		const url = `${protocol}://${host}${port}/${siteName}`

		socket = io(url, {
			withCredentials: true,
			reconnectionAttempts: 3,
			reconnectionDelay: 2000,
			timeout: 5000,
		})

		// Handle connection errors gracefully
		socket.on('connect_error', (error) => {
			console.warn('[Socket.io] Connection failed - real-time features disabled:', error.message)
			socketInitializationFailed = true
			if (socket) {
				socket.close()
				socket = null
			}
		})

		socket.on('connect', () => {
			console.log('[Socket.io] Connected successfully')
			socketInitializationFailed = false
		})

		return socket
	} catch (error) {
		console.warn('[Socket.io] Initialization error:', error)
		socketInitializationFailed = true
		return null
	}
}

export function useSocket() {
	return socket
}

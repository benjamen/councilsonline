import { createPinia } from "pinia"
import { createApp } from "vue"

import App from "./App.vue"
import router from "./router"
import { initSocket } from "./socket"

import {
	Alert,
	Badge,
	Button,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"

const globalComponents = {
	Button,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
}

const app = createApp(App)
const pinia = createPinia()

// Add Pinia persistence plugin
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
pinia.use(piniaPluginPersistedstate)

setConfig("resourceFetcher", frappeRequest)

app.use(pinia)
app.use(router)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

// Initialize CSRF token before mounting
async function initApp() {
	// Fetch CSRF token from session
	try {
		console.log('[main.js] Fetching CSRF token from API...')
		const response = await fetch('/api/method/frappe.auth.get_logged_user', {
			credentials: 'include'
		})
		console.log('[main.js] CSRF fetch response status:', response.status, response.ok)

		if (response.ok) {
			const data = await response.json()
			console.log('[main.js] API response:', data)

			// CSRF token should be in cookies
			const csrfFromCookie = document.cookie.split('; ').find(row => row.startsWith('csrf_token='))
			console.log('[main.js] Current cookies:', document.cookie)
			console.log('[main.js] CSRF cookie found:', csrfFromCookie)

			if (csrfFromCookie) {
				window.csrf_token = csrfFromCookie.split('=')[1]
				console.log('[main.js] ✅ CSRF token set successfully:', window.csrf_token)
			} else {
				console.warn('[main.js] ⚠️ No CSRF token found in cookies!')
				console.warn('[main.js] You are accessing from:', window.location.href)
				console.warn('[main.js] Development should use http://localhost:8080 (Vite dev server)')
			}
		} else {
			console.error('[main.js] Failed to fetch CSRF token - response not OK')
		}
	} catch (error) {
		console.error('[main.js] ❌ Could not fetch CSRF token:', error)
	}

	const socket = initSocket()
	app.config.globalProperties.$socket = socket

	for (const key in globalComponents) {
		app.component(key, globalComponents[key])
	}

	app.mount("#app")
}

initApp()

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
import "./styles/theme.css"

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
import piniaPluginPersistedstate from "pinia-plugin-persistedstate"
pinia.use(piniaPluginPersistedstate)

setConfig("resourceFetcher", frappeRequest)

app.use(pinia)
app.use(router)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

// Initialize CSRF token before mounting
async function initApp() {
	// Check if CSRF token is already in boot data (injected by backend)
	if (window.csrf_token) {
		console.log("[main.js] ✅ CSRF token loaded from boot data")
	} else {
		// Fallback: try to get from cookies
		console.log("[main.js] No boot CSRF token, trying cookies...")
		const csrfFromCookie = document.cookie
			.split("; ")
			.find((row) => row.startsWith("csrf_token="))

		if (csrfFromCookie) {
			window.csrf_token = csrfFromCookie.split("=")[1]
			console.log("[main.js] ✅ CSRF token found in cookies")
		} else {
			// Final fallback: fetch from API
			try {
				console.log("[main.js] Fetching CSRF token from API...")
				const response = await fetch(
					"/api/method/frappe.auth.get_logged_user",
					{
						credentials: "include",
					},
				)

				if (response.ok) {
					// Check cookies again after API call
					const csrfAfterFetch = document.cookie
						.split("; ")
						.find((row) => row.startsWith("csrf_token="))
					if (csrfAfterFetch) {
						window.csrf_token = csrfAfterFetch.split("=")[1]
						console.log("[main.js] ✅ CSRF token set after API fetch")
					} else {
						console.warn("[main.js] ⚠️ No CSRF token available")
					}
				}
			} catch (error) {
				console.error("[main.js] ❌ Could not fetch CSRF token:", error)
			}
		}
	}

	const socket = initSocket()
	app.config.globalProperties.$socket = socket

	for (const key in globalComponents) {
		app.component(key, globalComponents[key])
	}

	app.mount("#app")
}

initApp()

import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { userResource } from "./user"
import { useCouncilStore } from "@/stores/councilStore"

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			}
		},
		async onSuccess() {
			userResource.reload()
			session.user = sessionUser()
			session.login.reset()

			// Check if coming from council-specific login page
			const councilStore = useCouncilStore()
			if (councilStore.lockedCouncil) {
				router.replace({
					name: "CouncilDashboard",
					params: { councilCode: councilStore.lockedCouncil }
				})
			} else {
				router.replace({ name: "Dashboard" })
			}
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			router.replace({ name: "Login" })
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})

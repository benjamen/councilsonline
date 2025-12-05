import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"
import { useCouncilStore } from "./stores/councilStore"

const routes = [
	{
		path: "/",
		name: "Landing",
		component: () => import("@/pages/Landing.vue"),
		meta: { public: true }
	},
	{
		path: "/dashboard",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		path: "/home",
		name: "Home",
		component: () => import("@/pages/Home.vue"),
	},
	{
		path: "/request/new",
		name: "NewRequest",
		component: () => import("@/pages/NewRequest.vue"),
		meta: { public: true }
	},
	{
		path: "/request/:id",
		name: "RequestDetail",
		component: () => import("@/pages/RequestDetail.vue"),
	},
	{
		path: "/internal",
		name: "InternalRequestManagement",
		component: () => import("@/pages/InternalRequestManagement.vue"),
	},
	{
		path: "/internal/request/:id",
		name: "InternalRequestDetail",
		component: () => import("@/pages/InternalRequestDetail.vue"),
	},
	{
		path: "/settings",
		name: "Settings",
		component: () => import("@/pages/Settings.vue"),
	},
	{
		path: "/company",
		name: "CompanyManagement",
		component: () => import("@/pages/CompanyManagement.vue"),
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
		meta: { public: true }
	},
	{
		name: "Register",
		path: "/account/register",
		component: () => import("@/pages/Register.vue"),
		meta: { public: true }
	},
	{
		name: "CompanyRegistration",
		path: "/account/register-company",
		component: () => import("@/pages/CompanyRegistration.vue"),
		meta: { public: true }
	},
	// Council-specific landing page
	{
		path: "/council/:councilCode",
		name: "CouncilLanding",
		component: () => import("@/pages/CouncilLandingPage.vue"),
		meta: { public: true },
		beforeEnter: async (to, from, next) => {
			const councilStore = useCouncilStore()
			const success = await councilStore.setLockedCouncil(to.params.councilCode.toUpperCase())
			if (success) {
				next()
			} else {
				// Invalid council code - redirect to home
				next({ name: "Landing" })
			}
		}
	},
	// Deep linking - council + request type
	{
		path: "/council/:councilCode/request-type/:requestType",
		name: "CouncilRequestType",
		component: () => import("@/pages/NewRequest.vue"),
		meta: { public: true },
		beforeEnter: async (to, from, next) => {
			const councilStore = useCouncilStore()
			await councilStore.setLockedCouncil(to.params.councilCode.toUpperCase())
			next({
				name: "NewRequest",
				query: {
					council: to.params.councilCode.toUpperCase(),
					type: to.params.requestType,
					locked: "true"
				}
			})
		}
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const councilStore = useCouncilStore()

	// Load locked council state on first navigation
	if (!councilStore.isCouncilLocked && !to.meta.skipCouncilCheck) {
		await councilStore.loadLockedCouncil()
	}

	// Handle council URL parameter
	if (to.query.council) {
		councilStore.setPreselectedFromUrl(to.query.council)

		// Optionally load council data immediately
		await councilStore.loadCouncilByCode(to.query.council)
	}

	// Allow public pages without authentication
	if (to.meta.public) {
		next()
		return
	}

	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Dashboard" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router

import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Landing",
		component: () => import("@/pages/Landing.vue"),
		meta: { public: true },
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
		meta: { public: true },
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
		path: "/admin/request-type-builder",
		name: "RequestTypeBuilder",
		component: () => import("@/pages/RequestTypeBuilder.vue"),
		meta: { requiresAdmin: true },
	},
	{
		path: "/admin/assessment-template-builder",
		name: "AssessmentTemplateBuilder",
		component: () => import("@/pages/AssessmentTemplateBuilder.vue"),
		meta: { requiresAdmin: true },
	},
	{
		path: "/admin/assessment-template-builder/:id",
		name: "AssessmentTemplateBuilderEdit",
		component: () => import("@/pages/AssessmentTemplateBuilder.vue"),
		meta: { requiresAdmin: true },
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
		meta: { public: true },
	},
	{
		name: "ForgotPassword",
		path: "/account/forgot-password",
		component: () => import("@/pages/ForgotPassword.vue"),
		meta: { public: true },
	},
	{
		name: "Register",
		path: "/account/register",
		component: () => import("@/pages/Register.vue"),
		meta: { public: true },
	},
	{
		name: "CompanyRegistration",
		path: "/account/register-company",
		component: () => import("@/pages/CompanyRegistration.vue"),
		meta: { public: true },
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
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

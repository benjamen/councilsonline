import { mount } from "@vue/test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { nextTick } from "vue"

// Mock vue-router
const mockPush = vi.fn()
vi.mock("vue-router", () => ({
	useRouter: () => ({
		push: mockPush,
	}),
}))

// Mock frappe-ui
vi.mock("frappe-ui", () => ({
	Button: {
		name: "Button",
		template: "<button><slot /></button>",
		props: ["variant", "theme"],
	},
	Dropdown: {
		name: "Dropdown",
		template: '<div class="dropdown"><slot :open="false" /></div>',
		props: ["options"],
	},
	Input: {
		name: "Input",
		template:
			'<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
		props: ["modelValue", "placeholder", "type"],
		emits: ["update:modelValue"],
	},
}))

// Mock session
vi.mock("../../data/session", () => ({
	session: {
		user: "test@example.com",
		user_info: {
			full_name: "John Doe",
		},
		logout: {
			submit: vi.fn(),
		},
	},
}))

// Mock requestService with mutable data
let mockRequestsData = [
	{
		name: "REQ-001",
		request_number: "REQ-001",
		request_type: "Building Consent",
		workflow_state: "Submitted",
		status: "Under Review",
		creation: "2026-01-01",
		working_days_elapsed: 5,
		property_address: "123 Main St",
	},
	{
		name: "REQ-002",
		request_number: "REQ-002",
		request_type: "Resource Consent",
		workflow_state: "Approved",
		status: "Approved",
		creation: "2026-01-05",
		working_days_elapsed: 3,
	},
	{
		name: "REQ-003",
		request_number: "REQ-003",
		request_type: "Building Consent",
		workflow_state: "Draft",
		status: "Draft",
		creation: "2026-01-10",
		working_days_elapsed: 0,
	},
]

let mockLoadingState = false

vi.mock("../../services", () => ({
	requestService: {
		getUserRequests: () => ({
			get loading() {
				return mockLoadingState
			},
			set loading(val) {
				mockLoadingState = val
			},
			get data() {
				return mockRequestsData
			},
			set data(val) {
				mockRequestsData = val
			},
		}),
	},
}))

// Mock StatCard component
vi.mock("../../components/StatCard.vue", () => ({
	default: {
		name: "StatCard",
		props: ["title", "value", "icon", "color"],
		template:
			'<div class="stat-card" :data-title="title" :data-value="value"></div>',
	},
}))

// Mock StatusBadge component
vi.mock("../../components/StatusBadge.vue", () => ({
	default: {
		name: "StatusBadge",
		props: ["status"],
		template: '<span class="status-badge" :data-status="status"></span>',
	},
}))

import Dashboard from "../Dashboard.vue"

describe("Dashboard", () => {
	beforeEach(() => {
		mockPush.mockClear()
		mockLoadingState = false
		// Reset data to default
		mockRequestsData = [
			{
				name: "REQ-001",
				request_number: "REQ-001",
				request_type: "Building Consent",
				workflow_state: "Submitted",
				status: "Under Review",
				creation: "2026-01-01",
				working_days_elapsed: 5,
				property_address: "123 Main St",
			},
			{
				name: "REQ-002",
				request_number: "REQ-002",
				request_type: "Resource Consent",
				workflow_state: "Approved",
				status: "Approved",
				creation: "2026-01-05",
				working_days_elapsed: 3,
			},
			{
				name: "REQ-003",
				request_number: "REQ-003",
				request_type: "Building Consent",
				workflow_state: "Draft",
				status: "Draft",
				creation: "2026-01-10",
				working_days_elapsed: 0,
			},
		]
	})

	it("renders dashboard header with title", () => {
		const wrapper = mount(Dashboard)

		expect(wrapper.find("h1").text()).toBe("Councils Online")
		expect(wrapper.find("h1 + p").text()).toBe("Council Request Management")
	})

	it("displays welcome message with user name", () => {
		const wrapper = mount(Dashboard)

		const welcomeHeading = wrapper.find("h2")
		expect(welcomeHeading.text()).toContain("Welcome back")
		expect(welcomeHeading.text()).toContain("John Doe")
	})

	it("displays user initials in avatar", () => {
		const wrapper = mount(Dashboard)

		const avatar = wrapper.find(".text-blue-600")
		expect(avatar.text()).toBe("JD")
	})

	it("renders new request button", () => {
		const wrapper = mount(Dashboard)

		const newRequestBtn = wrapper
			.findAll("button")
			.find((btn) => btn.text().includes("New Request"))
		expect(newRequestBtn).toBeTruthy()
	})

	it("navigates to new request page when button clicked", async () => {
		const wrapper = mount(Dashboard)

		const newRequestBtn = wrapper
			.findAll("button")
			.find((btn) => btn.text().includes("New Request"))
		await newRequestBtn.trigger("click")

		expect(mockPush).toHaveBeenCalledWith({ name: "NewRequest" })
	})

	describe("Stats Cards", () => {
		it("renders all four stat cards", () => {
			const wrapper = mount(Dashboard)

			const statCards = wrapper.findAllComponents({ name: "StatCard" })
			expect(statCards).toHaveLength(4)
		})

		it("displays correct total requests count", () => {
			const wrapper = mount(Dashboard)

			const totalCard = wrapper
				.findAllComponents({ name: "StatCard" })
				.find((card) => card.props("title") === "Total Requests")

			expect(totalCard.props("value")).toBe(3)
			expect(totalCard.props("icon")).toBe("file-text")
			expect(totalCard.props("color")).toBe("blue")
		})

		it("displays correct under review count", () => {
			const wrapper = mount(Dashboard)

			const underReviewCard = wrapper
				.findAllComponents({ name: "StatCard" })
				.find((card) => card.props("title") === "Under Review")

			expect(underReviewCard.props("value")).toBe(1)
			expect(underReviewCard.props("color")).toBe("yellow")
		})

		it("displays correct approved count", () => {
			const wrapper = mount(Dashboard)

			const approvedCard = wrapper
				.findAllComponents({ name: "StatCard" })
				.find((card) => card.props("title") === "Approved")

			expect(approvedCard.props("value")).toBe(1)
			expect(approvedCard.props("color")).toBe("green")
		})

		it("displays correct RFI pending count", () => {
			const wrapper = mount(Dashboard)

			const rfiCard = wrapper
				.findAllComponents({ name: "StatCard" })
				.find((card) => card.props("title") === "Info Requested")

			expect(rfiCard.props("value")).toBe(0)
			expect(rfiCard.props("color")).toBe("orange")
		})
	})

	describe("Filters", () => {
		it("renders search input", () => {
			const wrapper = mount(Dashboard)

			const searchInput = wrapper.findComponent({ name: "Input" })
			expect(searchInput.exists()).toBe(true)
			expect(searchInput.props("placeholder")).toContain("Search")
		})

		it("renders type filter dropdown", () => {
			const wrapper = mount(Dashboard)

			const typeSelect = wrapper.find("select")
			expect(typeSelect.exists()).toBe(true)

			const options = typeSelect.findAll("option")
			expect(options).toHaveLength(3) // All Types, Resource Consent, Building Consent
		})

		it("filters requests by search query", async () => {
			const wrapper = mount(Dashboard)

			const searchInput = wrapper.findComponent({ name: "Input" })
			await searchInput.setValue("REQ-001")
			await nextTick()

			const rows = wrapper.findAll("tbody tr")
			expect(rows).toHaveLength(1)
			expect(rows[0].text()).toContain("REQ-001")
		})

		it("filters requests by type", async () => {
			const wrapper = mount(Dashboard)

			const typeSelect = wrapper.find("select")
			await typeSelect.setValue("Building Consent")
			await nextTick()

			const rows = wrapper.findAll("tbody tr")
			expect(rows).toHaveLength(2) // REQ-001 and REQ-003
		})

		it("shows empty state when no results match filters", async () => {
			const wrapper = mount(Dashboard)

			const searchInput = wrapper.findComponent({ name: "Input" })
			await searchInput.setValue("NONEXISTENT")
			await nextTick()

			expect(wrapper.text()).toContain("No applications found")
			expect(wrapper.text()).toContain("Try adjusting your search or filters")
		})
	})

	describe("Requests Table", () => {
		it("renders table with correct headers", () => {
			const wrapper = mount(Dashboard)

			const headers = wrapper.findAll("thead th")
			expect(headers).toHaveLength(6)
			expect(headers[0].text()).toContain("Request #")
			expect(headers[1].text()).toContain("Type")
			expect(headers[2].text()).toContain("State")
			expect(headers[3].text()).toContain("Submitted")
			expect(headers[4].text()).toContain("Days Elapsed")
			expect(headers[5].text()).toContain("Actions")
		})

		it("renders all requests in table", () => {
			const wrapper = mount(Dashboard)

			const rows = wrapper.findAll("tbody tr")
			expect(rows).toHaveLength(3)
		})

		it("displays request information correctly", () => {
			const wrapper = mount(Dashboard)

			const firstRow = wrapper.find("tbody tr")
			expect(firstRow.text()).toContain("REQ-001")
			expect(firstRow.text()).toContain("Building Consent")
			expect(firstRow.text()).toContain("Submitted")
			expect(firstRow.text()).toContain("5 days")
		})

		it("navigates to request detail when row clicked", async () => {
			const wrapper = mount(Dashboard)

			const firstRow = wrapper.find("tbody tr")
			await firstRow.trigger("click")

			expect(mockPush).toHaveBeenCalledWith({
				name: "RequestDetail",
				params: { id: "REQ-001" },
			})
		})

		it("displays View button for all requests", () => {
			const wrapper = mount(Dashboard)

			const viewButtons = wrapper
				.findAll("tbody button")
				.filter((btn) => btn.text() === "View")
			expect(viewButtons).toHaveLength(3)
		})

		it("displays Edit button only for Draft requests", () => {
			const wrapper = mount(Dashboard)

			const editButtons = wrapper
				.findAll("tbody button")
				.filter((btn) => btn.text() === "Edit")
			expect(editButtons).toHaveLength(1)
		})

		it("navigates to request detail when View button clicked", async () => {
			const wrapper = mount(Dashboard)

			const viewButton = wrapper
				.findAll("tbody button")
				.find((btn) => btn.text() === "View")
			await viewButton.trigger("click")

			expect(mockPush).toHaveBeenCalled()
		})
	})

	describe("Loading State", () => {
		it("shows loading spinner when loading", () => {
			mockLoadingState = true
			const wrapper = mount(Dashboard)

			expect(wrapper.find(".animate-spin").exists()).toBe(true)
			expect(wrapper.text()).toContain("Loading applications")
		})

		it("hides table when loading", () => {
			mockLoadingState = true
			const wrapper = mount(Dashboard)

			expect(wrapper.find("table").exists()).toBe(false)
		})
	})

	describe("Empty State", () => {
		it("shows empty state when no requests", () => {
			mockRequestsData = []
			const wrapper = mount(Dashboard)

			expect(wrapper.text()).toContain("No applications found")
			expect(wrapper.text()).toContain(
				"Get started by creating your first application",
			)
		})

		it("shows create button in empty state", () => {
			mockRequestsData = []
			const wrapper = mount(Dashboard)

			const createButton = wrapper
				.findAll("button")
				.find((btn) => btn.text().includes("Create New Application"))
			expect(createButton).toBeTruthy()
		})
	})

	describe("Date Formatting", () => {
		it("formats dates in NZ locale", () => {
			const wrapper = mount(Dashboard)

			const firstRow = wrapper.find("tbody tr")
			const dateCell = firstRow.findAll("td")[3]

			// Date should be formatted like "1 Jan 2026"
			expect(dateCell.text()).toMatch(/\d{1,2}\s\w{3}\s\d{4}/)
		})
	})

	describe("User Menu", () => {
		it("renders user menu dropdown", () => {
			const wrapper = mount(Dashboard)

			const dropdown = wrapper.findComponent({ name: "Dropdown" })
			expect(dropdown.exists()).toBe(true)
		})

		it("displays user name in menu trigger", () => {
			const wrapper = mount(Dashboard)

			expect(wrapper.text()).toContain("John Doe")
		})
	})
})

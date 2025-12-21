import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
	testDir: "./tests",
	timeout: 60 * 1000,
	fullyParallel: false,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: 1,
	reporter: [
		["html", { outputFolder: "playwright-report" }],
		["list"],
		["json", { outputFile: "playwright-report/results.json" }],
	],

	use: {
		baseURL: "http://localhost:8090",
		trace: "on-first-retry",
		screenshot: "only-on-failure",
		video: "retain-on-failure",
		actionTimeout: 10 * 1000,
		navigationTimeout: 30 * 1000,

		// Headed mode support for visual debugging
		...(process.env.HEADED && {
			headless: false,
			slowMo: 500, // Slow down actions by 500ms for visual debugging
			video: "on", // Always record video in headed mode
		}),
	},

	projects: [
		{
			name: "chromium-desktop",
			use: {
				...devices["Desktop Chrome"],
				viewport: { width: 1280, height: 720 },
			},
		},
		{
			name: "chromium-mobile",
			use: {
				...devices["iPhone 12"],
				viewport: { width: 390, height: 844 },
			},
		},
	],

	webServer: {
		command: "bench start",
		url: "http://localhost:8090",
		reuseExistingServer: true,
		timeout: 120000,
	},
})

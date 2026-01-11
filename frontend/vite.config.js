import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: true,
			buildConfig: {
				indexHtmlPath: "../lodgeick/www/frontend.html",
				emptyOutDir: true,
				sourcemap: true,
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../lodgeick/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: true,
		// Production optimizations
		minify: "esbuild",
		rollupOptions: {
			output: {
				manualChunks: {
					// Split vendor chunks for better caching
					'frappe-ui': ['frappe-ui'],
					'vue-vendor': ['vue', 'vue-router', 'pinia'],
					'ui-components': ['@headlessui/vue']
				}
			}
		},
		// Remove console.log in production builds (keep error and warn)
		esbuild: {
			drop: ['console'],
			pure: ['console.log', 'console.debug', 'console.trace']
		}
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	optimizeDeps: {
		include: [
			"feather-icons",
			"showdown",
			"highlight.js/lib/core",
			"interactjs",
		],
	},
	server: {
		host: "0.0.0.0",
		allowedHosts: true,
		port: 8080,
		proxy: {
			"^/(app|api|assets|files)": {
				target: "http://127.0.0.1:8090",
				ws: true,
				changeOrigin: true,
				secure: false,
				configure: (proxy, options) => {
					proxy.on("proxyReq", (proxyReq, req, res) => {
						// Set the Host header to lodgeick.localhost for Frappe site routing
						proxyReq.setHeader("Host", "lodgeick.localhost")
						// Forward cookies properly
						proxyReq.setHeader("X-Frappe-Site-Name", "lodgeick.localhost")
					})
				},
			},
		},
	},
})

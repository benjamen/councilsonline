frappe.pages['test-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test Dashboard',
		single_column: true
	});

	page.main.addClass('frappe-card');

	// Add buttons
	page.add_inner_button('Run Frontend Unit Tests', () => {
		run_tests('Frontend Unit Tests');
	});

	page.add_inner_button('Run Frontend E2E Tests', () => {
		run_tests('Frontend E2E Tests');
	});

	page.add_inner_button('Run Backend Unit Tests', () => {
		run_tests('Backend Unit Tests');
	});

	page.add_inner_button('Refresh', () => {
		load_dashboard();
	});

	// Load dashboard content
	load_dashboard();

	function load_dashboard() {
		frappe.call({
			method: 'councilsonline.councilsonline.doctype.test_runner.test_runner.get_test_statistics',
			callback: function(r) {
				if (r.message) {
					render_dashboard(page.main, r.message);
				}
			}
		});
	}

	function run_tests(test_suite) {
		frappe.call({
			method: 'councilsonline.councilsonline.doctype.test_runner.test_runner.run_tests',
			args: {
				test_suite: test_suite,
				test_type: 'All'
			},
			callback: function(r) {
				if (r.message) {
					frappe.show_alert({
						message: `Test started: ${r.message.name}`,
						indicator: 'blue'
					});

					// Refresh dashboard after 2 seconds
					setTimeout(() => load_dashboard(), 2000);

					// Open the test runner document
					frappe.set_route('Form', 'Test Runner', r.message.name);
				}
			}
		});
	}

	function render_dashboard(container, data) {
		container.empty();

		// Overall Statistics Card
		let stats_html = `
			<div class="row">
				<div class="col-md-12">
					<h4>Overall Test Statistics (Last 30 Days)</h4>
					<div class="row">
						<div class="col-md-3">
							<div class="frappe-card" style="padding: 20px; text-align: center;">
								<h1 style="color: #5e64ff;">${data.total_runs}</h1>
								<p>Total Test Runs</p>
							</div>
						</div>
						<div class="col-md-3">
							<div class="frappe-card" style="padding: 20px; text-align: center;">
								<h1 style="color: #2e7d32;">${data.successful_runs}</h1>
								<p>Successful</p>
							</div>
						</div>
						<div class="col-md-3">
							<div class="frappe-card" style="padding: 20px; text-align: center;">
								<h1 style="color: #c62828;">${data.failed_runs}</h1>
								<p>Failed</p>
							</div>
						</div>
						<div class="col-md-3">
							<div class="frappe-card" style="padding: 20px; text-align: center;">
								<h1 style="color: #5e64ff;">${data.success_rate.toFixed(1)}%</h1>
								<p>Success Rate</p>
							</div>
						</div>
					</div>
				</div>
			</div>
			<br>
		`;

		container.append(stats_html);

		// Test Suites Table
		let suites_html = '<h4>Test Suites</h4><table class="table table-bordered"><thead><tr>';
		suites_html += '<th>Suite</th><th>Total Runs</th><th>Successful</th><th>Failed</th><th>Total Tests</th><th>Passed</th><th>Failed</th>';
		suites_html += '</tr></thead><tbody>';

		for (let suite in data.by_suite) {
			let suite_data = data.by_suite[suite];
			let success_rate = suite_data.total_runs > 0 ?
				(suite_data.successful / suite_data.total_runs * 100).toFixed(1) : 0;

			suites_html += '<tr>';
			suites_html += `<td><strong>${suite}</strong></td>`;
			suites_html += `<td>${suite_data.total_runs}</td>`;
			suites_html += `<td style="color: #2e7d32;">${suite_data.successful}</td>`;
			suites_html += `<td style="color: #c62828;">${suite_data.failed}</td>`;
			suites_html += `<td>${suite_data.total_tests}</td>`;
			suites_html += `<td style="color: #2e7d32;">${suite_data.passed_tests}</td>`;
			suites_html += `<td style="color: #c62828;">${suite_data.failed_tests}</td>`;
			suites_html += '</tr>';
		}

		suites_html += '</tbody></table><br>';
		container.append(suites_html);

		// Recent Test Runs
		let recent_html = '<h4>Recent Test Runs</h4><table class="table table-bordered"><thead><tr>';
		recent_html += '<th>Test Run</th><th>Suite</th><th>Status</th><th>Duration (s)</th><th>Tests</th><th>Passed</th><th>Failed</th><th>Created</th>';
		recent_html += '</tr></thead><tbody>';

		data.recent_tests.forEach(test => {
			let status_color = test.status === 'Completed' ? '#2e7d32' :
							   test.status === 'Failed' ? '#c62828' :
							   test.status === 'Running' ? '#1976d2' : '#666';

			recent_html += '<tr>';
			recent_html += `<td><a href="/app/test-runner/${test.name}">${test.name}</a></td>`;
			recent_html += `<td>${test.test_suite}</td>`;
			recent_html += `<td style="color: ${status_color}"><strong>${test.status}</strong></td>`;
			recent_html += `<td>${test.duration ? test.duration.toFixed(2) : '-'}</td>`;
			recent_html += `<td>${test.total_tests || 0}</td>`;
			recent_html += `<td style="color: #2e7d32;">${test.passed_tests || 0}</td>`;
			recent_html += `<td style="color: #c62828;">${test.failed_tests || 0}</td>`;
			recent_html += `<td>${frappe.datetime.comment_when(test.creation)}</td>`;
			recent_html += '</tr>';
		});

		recent_html += '</tbody></table>';
		container.append(recent_html);
	}
};

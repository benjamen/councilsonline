/**
 * CouncilsOnline Setup Wizard Slide
 * Allows users to select which configuration packs to install
 */

frappe.provide("councilsonline.setup");

frappe.setup.on("before_load", function () {
	// Add configuration pack selection slide
	frappe.setup.add_slide({
		name: "config_packs",
		title: __("Configuration Packs"),
		icon: "fa fa-cogs",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "pack_description",
				options: `
					<div class="text-muted" style="margin-bottom: 20px;">
						<p>Select the configuration packs to install. Each pack contains
						request types, assessment templates, and other data specific to a region or use case.</p>
					</div>
				`,
			},
			{
				fieldtype: "Check",
				fieldname: "install_nz_resource_consent",
				label: __("New Zealand Resource Consent"),
				description: __(
					"10 request types for NZ councils (Land Use, Building, Subdivision, etc.), 3 assessment templates, and consent condition templates"
				),
				default: 0,
			},
			{
				fieldtype: "Check",
				fieldname: "install_ph_social_services",
				label: __("Philippines Social Services"),
				description: __(
					"SPISC (Social Pension for Indigent Senior Citizens), Senior Assistance programs, Taytay Council configuration, and demo users"
				),
				default: 0,
			},
			{
				fieldtype: "Section Break",
			},
			{
				fieldtype: "HTML",
				fieldname: "pack_note",
				options: `
					<div class="alert alert-info" style="margin-top: 10px;">
						<i class="fa fa-info-circle"></i>
						You can install additional packs later using:<br>
						<code>bench --site {site} install-config-packs</code>
					</div>
				`,
			},
		],

		onload: function (slide) {
			// Pre-select packs based on locale or other hints
			const locale = frappe.boot.sysdefaults?.country || "";

			if (locale === "New Zealand") {
				slide.get_field("install_nz_resource_consent").set_value(1);
			} else if (locale === "Philippines") {
				slide.get_field("install_ph_social_services").set_value(1);
			}
		},

		validate: function () {
			// At least one pack should be selected (optional - remove if not needed)
			return true;
		},
	});
});

// Handle setup wizard completion
councilsonline.setup.on_setup_complete = function (args) {
	const packs_to_install = [];

	if (args.install_nz_resource_consent) {
		packs_to_install.push("nz_resource_consent");
	}
	if (args.install_ph_social_services) {
		packs_to_install.push("ph_social_services");
	}

	if (packs_to_install.length > 0) {
		return frappe.call({
			method: "councilsonline.setup.setup_wizard.install_selected_packs",
			args: {
				packs: packs_to_install,
			},
			freeze: true,
			freeze_message: __("Installing configuration packs..."),
		});
	}

	return Promise.resolve();
};

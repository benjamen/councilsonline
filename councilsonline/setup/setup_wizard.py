"""
Setup Wizard handlers for CouncilsOnline

This module provides the setup wizard stages and completion handlers
for interactive configuration pack selection.
"""
import frappe


def get_setup_stages(args=None):
	"""
	Return setup wizard stages for CouncilsOnline

	This is called by Frappe's setup wizard to get the list of stages
	to execute during setup.
	"""
	return [
		{
			"status": "Installing CouncilsOnline",
			"fail_msg": "Failed to install CouncilsOnline configuration",
			"tasks": [
				{
					"fn": setup_councilsonline,
					"args": args,
					"fail_msg": "Failed to setup CouncilsOnline",
				}
			],
		}
	]


def setup_councilsonline(args):
	"""
	Main setup function called by the wizard

	This installs base infrastructure and any selected packs.
	"""
	from councilsonline.setup.pack_installer import install_config_pack

	# Always install base pack
	frappe.log("Installing base infrastructure...")
	install_config_pack("base", force=False)

	# Install selected packs from wizard
	if args.get("install_nz_resource_consent"):
		frappe.log("Installing NZ Resource Consent pack...")
		install_config_pack("nz_resource_consent", force=False)

	if args.get("install_ph_social_services"):
		frappe.log("Installing PH Social Services pack...")
		install_config_pack("ph_social_services", force=False)


@frappe.whitelist()
def install_selected_packs(packs):
	"""
	API endpoint to install selected packs

	Called from the setup wizard JavaScript after completion.

	Args:
		packs: List of pack names to install
	"""
	from councilsonline.setup.pack_installer import install_config_pack

	if isinstance(packs, str):
		import json
		packs = json.loads(packs)

	results = {}
	for pack_name in packs:
		try:
			success = install_config_pack(pack_name, force=False)
			results[pack_name] = "success" if success else "failed"
		except Exception as e:
			results[pack_name] = f"error: {str(e)}"
			frappe.log_error(f"Failed to install pack {pack_name}: {str(e)}")

	frappe.db.commit()

	return results


def on_setup_complete(args):
	"""
	Called after the setup wizard completes

	This is a hook that runs after all setup wizard stages are done.
	"""
	frappe.log("CouncilsOnline setup wizard completed")

	# Log which packs were installed
	from councilsonline.setup.pack_installer import get_installed_packs
	installed = get_installed_packs()

	if installed:
		frappe.log(f"Installed packs: {', '.join(installed)}")
	else:
		frappe.log("No configuration packs installed. Use 'bench install-config-packs' to add them.")

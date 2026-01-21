"""
Custom bench commands for CouncilsOnline app
"""
import click
import frappe
from frappe.commands import pass_context, get_site
import json
import os
from pathlib import Path


def get_packs_dir():
	"""Get the path to the packs directory"""
	app_path = frappe.get_app_path("councilsonline")
	return Path(app_path) / "councilsonline" / "fixtures" / "packs"


def get_available_packs():
	"""Get list of available configuration packs"""
	packs_dir = get_packs_dir()
	packs = []

	if not packs_dir.exists():
		return packs

	for pack_dir in packs_dir.iterdir():
		if pack_dir.is_dir() and pack_dir.name != "__pycache__":
			pack_info_file = pack_dir / "pack_info.json"
			if pack_info_file.exists():
				with open(pack_info_file) as f:
					pack_info = json.load(f)
					pack_info["path"] = str(pack_dir)
					packs.append(pack_info)

	return packs


def show_available_packs():
	"""Display available packs in a formatted table"""
	packs = get_available_packs()

	if not packs:
		click.echo("No configuration packs found.")
		return

	click.echo("\n" + "=" * 70)
	click.echo("AVAILABLE CONFIGURATION PACKS")
	click.echo("=" * 70)

	for pack in packs:
		if pack.get("name") == "base":
			continue  # Skip base pack in listing

		auto = " (auto-install)" if pack.get("auto_install") else ""
		click.echo(f"\n{pack.get('display_name', pack['name'])}{auto}")
		click.echo(f"  Name: {pack['name']}")
		click.echo(f"  Region: {pack.get('region', 'Global')}")
		click.echo(f"  Description: {pack.get('description', 'No description')}")

		if pack.get("includes"):
			click.echo("  Includes:")
			for item in pack["includes"]:
				click.echo(f"    - {item}")

	click.echo("\n" + "=" * 70)


def show_pack_details(pack_name):
	"""Show detailed information about a specific pack"""
	packs = get_available_packs()
	pack = next((p for p in packs if p["name"] == pack_name), None)

	if not pack:
		click.echo(f"Pack '{pack_name}' not found.")
		return

	click.echo(f"\n{'=' * 70}")
	click.echo(f"PACK: {pack.get('display_name', pack['name'])}")
	click.echo(f"{'=' * 70}")
	click.echo(f"Name: {pack['name']}")
	click.echo(f"Version: {pack.get('version', '1.0.0')}")
	click.echo(f"Region: {pack.get('region', 'Global')}")
	click.echo(f"Description: {pack.get('description', 'No description')}")

	if pack.get("includes"):
		click.echo("\nIncludes:")
		for item in pack["includes"]:
			click.echo(f"  - {item}")

	if pack.get("request_types"):
		click.echo("\nRequest Types:")
		for rt in pack["request_types"]:
			click.echo(f"  - {rt}")

	click.echo(f"{'=' * 70}\n")


def prompt_pack_selection():
	"""Interactive pack selection"""
	packs = [p for p in get_available_packs() if p.get("name") != "base"]

	if not packs:
		click.echo("No configuration packs available.")
		return []

	click.echo("\nSelect configuration packs to install:")
	click.echo("-" * 40)

	for i, pack in enumerate(packs, 1):
		click.echo(f"  {i}. {pack.get('display_name', pack['name'])} [{pack.get('region', 'Global')}]")
		click.echo(f"     {pack.get('description', '')[:60]}...")

	click.echo(f"  {len(packs) + 1}. Install ALL packs")
	click.echo(f"  0. Cancel")
	click.echo("-" * 40)

	while True:
		choice = click.prompt("Enter number(s) separated by comma", default="0")

		if choice == "0":
			click.echo("Cancelled.")
			return []

		try:
			choices = [int(c.strip()) for c in choice.split(",")]

			if len(packs) + 1 in choices:
				return [p["name"] for p in packs]

			selected = []
			for c in choices:
				if 1 <= c <= len(packs):
					selected.append(packs[c - 1]["name"])
				else:
					click.echo(f"Invalid choice: {c}")
					continue

			if selected:
				return selected

		except ValueError:
			click.echo("Please enter valid numbers.")


def install_pack(pack_name, force=False):
	"""Install a specific configuration pack"""
	from councilsonline.setup.pack_installer import install_config_pack

	click.echo(f"\nInstalling pack: {pack_name}...")
	try:
		result = install_config_pack(pack_name, force=force)
		if result:
			click.echo(f"  ✓ Pack '{pack_name}' installed successfully")
		else:
			click.echo(f"  ✗ Pack '{pack_name}' installation failed")
		return result
	except Exception as e:
		click.echo(f"  ✗ Error installing '{pack_name}': {str(e)}")
		return False


@click.command("install-config-packs")
@click.option("--pack", "-p", multiple=True, help="Pack name(s) to install")
@click.option("--all", "install_all", is_flag=True, help="Install all available packs")
@click.option("--force", "-f", is_flag=True, help="Force reinstall even if already installed")
@pass_context
def install_config_packs(context, pack, install_all, force):
	"""Install configuration packs for CouncilsOnline

	Examples:
	  bench --site mysite install-config-packs --pack nz_resource_consent
	  bench --site mysite install-config-packs --all
	  bench --site mysite install-config-packs  # Interactive mode
	"""
	site = get_site(context)

	frappe.init(site=site)
	frappe.connect()

	try:
		if install_all:
			packs_to_install = [p["name"] for p in get_available_packs() if p.get("name") != "base"]
		elif pack:
			packs_to_install = list(pack)
		else:
			# Interactive mode
			packs_to_install = prompt_pack_selection()

		if not packs_to_install:
			click.echo("No packs selected.")
			return

		click.echo(f"\nInstalling {len(packs_to_install)} pack(s)...")
		click.echo("=" * 50)

		success_count = 0
		for pack_name in packs_to_install:
			if install_pack(pack_name, force=force):
				success_count += 1

		frappe.db.commit()

		click.echo("=" * 50)
		click.echo(f"Completed: {success_count}/{len(packs_to_install)} packs installed")

	finally:
		frappe.destroy()


@click.command("list-config-packs")
@pass_context
def list_config_packs(context):
	"""List available configuration packs for CouncilsOnline"""
	site = get_site(context)

	frappe.init(site=site)
	frappe.connect()

	try:
		show_available_packs()
	finally:
		frappe.destroy()


@click.command("show-config-pack")
@click.argument("pack_name")
@pass_context
def show_config_pack(context, pack_name):
	"""Show details of a specific configuration pack

	Example:
	  bench --site mysite show-config-pack nz_resource_consent
	"""
	site = get_site(context)

	frappe.init(site=site)
	frappe.connect()

	try:
		show_pack_details(pack_name)
	finally:
		frappe.destroy()


# Export commands for registration in hooks.py
commands = [
	install_config_packs,
	list_config_packs,
	show_config_pack,
]

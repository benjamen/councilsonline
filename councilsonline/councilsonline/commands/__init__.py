import click
import frappe
from frappe.commands import pass_context


@click.command('install-default-data')
@click.option('--force', is_flag=True, help='Force reinstall even if data exists')
@pass_context
def install_default_data(context, force=False):
	"""Install default configuration data for CouncilsOnline"""
	from councilsonline.setup.install import install_default_data as do_install

	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()

			click.echo(f"\n{'='*60}")
			click.echo(f"Installing default data for site: {site}")
			click.echo(f"{'='*60}\n")

			do_install(force=force)

			frappe.db.commit()
			click.echo(f"\n✓ Default data installation completed for {site}")

		except Exception as e:
			click.echo(f"\n✗ Error installing data for {site}: {str(e)}", err=True)
			frappe.db.rollback()

		finally:
			frappe.destroy()


commands = [
	install_default_data
]

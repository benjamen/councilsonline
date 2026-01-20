"""
Install Help Articles for CouncilsOnline
Run this script to create help documentation in Frappe
"""

import frappe
from pathlib import Path


def install_help_articles():
    """Create help articles from markdown files"""

    # Read the Resource Consent Guide
    help_dir = Path(frappe.get_app_path("councilsonline")) / "help"
    rc_guide_path = help_dir / "resource_consent_guide.md"

    if not rc_guide_path.exists():
        print(f"Help file not found: {rc_guide_path}")
        return

    with open(rc_guide_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create Web Page (simpler than Help Article)
    print("Creating Web Page for help content...")
    create_web_page(content)


def create_web_page(content):
    """Create a Web Page for the help guide"""

    page_name = "resource-consent-guide"

    if frappe.db.exists("Web Page", page_name):
        print(f"Web Page '{page_name}' already exists. Updating...")
        doc = frappe.get_doc("Web Page", page_name)
    else:
        print(f"Creating Web Page: {page_name}")
        doc = frappe.new_doc("Web Page")
        doc.route = page_name

    doc.title = "Resource Consent Application Guide"
    doc.published = 1

    # Convert markdown to HTML sections
    doc.main_section = f"""
    <div class="container py-5">
        <div class="row">
            <div class="col-md-10 offset-md-1">
                <div class="markdown-content">
                    {frappe.utils.md_to_html(content)}
                </div>
            </div>
        </div>
    </div>
    """

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    print(f"✅ Web Page created/updated: {doc.name}")
    print(f"   URL: /{doc.route}")


def create_help_menu_for_request_form():
    """Add help link to Request form"""

    try:
        # Add custom field to Request DocType for help link
        if not frappe.db.exists("Custom Field", {"dt": "Request", "fieldname": "help_section"}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Request",
                "label": "Need Help?",
                "fieldname": "help_section",
                "fieldtype": "Section Break",
                "insert_after": "request_number",
                "collapsible": 1
            })
            custom_field.insert(ignore_permissions=True)

            help_html = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Request",
                "label": "Application Guide",
                "fieldname": "help_html",
                "fieldtype": "HTML",
                "insert_after": "help_section",
                "options": """
                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #2490ef;">
                    <h4 style="margin-top: 0; color: #2490ef;">
                        <i class="fa fa-question-circle"></i> Need Help with Your Application?
                    </h4>
                    <p>Comprehensive guides are available to help you:</p>
                    <ul>
                        <li><a href="/resource-consent-guide" target="_blank"><strong>Resource Consent Application Guide</strong></a> - Complete step-by-step instructions</li>
                        <li><strong>RMA Activity Status</strong> - Understanding activity classifications</li>
                        <li><strong>AEE Requirements</strong> - What to include in your assessment</li>
                        <li><strong>Statutory Timeframes</strong> - How long processing takes</li>
                    </ul>
                    <p style="margin-bottom: 0;">
                        <a href="mailto:planning@council.govt.nz" style="color: #2490ef;">
                            <i class="fa fa-envelope"></i> Contact Planning Team
                        </a>
                    </p>
                </div>
                """
            })
            help_html.insert(ignore_permissions=True)

            frappe.db.commit()
            print("✅ Help section added to Request form")
        else:
            print("ℹ️  Help section already exists on Request form")

    except Exception as e:
        print(f"❌ Error adding help section to form: {str(e)}")


def execute():
    """Main execution function"""
    print("\n" + "="*60)
    print("Installing CouncilsOnline Help Articles")
    print("="*60 + "\n")

    install_help_articles()
    create_help_menu_for_request_form()

    print("\n" + "="*60)
    print("Installation Complete!")
    print("="*60 + "\n")
    print("Users can now access help at:")
    print("  - /resource-consent-guide")
    print("  - Via 'Need Help?' section in Request forms")
    print()


if __name__ == "__main__":
    execute()

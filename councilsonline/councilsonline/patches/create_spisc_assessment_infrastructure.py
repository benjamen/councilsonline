import frappe

def execute():
	"""
	Create Assessment Template and Task Templates for SPISC applications

	This patch creates:
	1. Assessment Stage Types (if they don't exist)
	2. Assessment Template for SPISC with 4 stages
	3. Task Templates for each stage (11 total tasks)
	"""
	frappe.flags.in_import = True

	# Step 0: Ensure Assessment Stage Types exist
	create_assessment_stage_types()

	# Step 1: Create Assessment Template
	create_assessment_template()

	# Step 2: Create Task Templates
	create_task_templates()

	frappe.db.commit()
	frappe.flags.in_import = False
	print("✅ SPISC Assessment Infrastructure created successfully!")


def create_assessment_stage_types():
	"""Create Assessment Stage Types if they don't exist"""

	stage_types = [
		"Vetting",
		"Technical Assessment",
		"Decision",
		"Implementation"
	]

	for stage_type in stage_types:
		if not frappe.db.exists("Assessment Stage Type", stage_type):
			doc = frappe.get_doc({
				"doctype": "Assessment Stage Type",
				"stage_type": stage_type
			})
			doc.insert(ignore_permissions=True)
			print(f"✅ Created Assessment Stage Type: {stage_type}")
		else:
			print(f"Assessment Stage Type '{stage_type}' already exists")


def create_assessment_template():
	"""Create Assessment Template for SPISC if it doesn't exist"""

	template_name = "Social Pension - Standard Assessment"

	if frappe.db.exists("Assessment Template", template_name):
		print(f"Assessment Template '{template_name}' already exists")
		return

	print(f"Creating Assessment Template: {template_name}")

	template = frappe.get_doc({
		"doctype": "Assessment Template",
		"template_name": template_name,
		"request_type": "Social Pension for Indigent Senior Citizens (SPISC)",
		"is_active": 1,
		"default_budget_hours": 24,
		"description": """
			<p><strong>Standard Assessment Workflow for SPISC Applications</strong></p>
			<p>This template guides the assessment of Social Pension applications through 4 key stages:</p>
			<ol>
				<li><strong>Eligibility Verification</strong> - Initial screening of age, residency, and pension status</li>
				<li><strong>Income & Poverty Assessment</strong> - Detailed financial and household verification</li>
				<li><strong>Approval Decision</strong> - Final eligibility determination and council approval</li>
				<li><strong>Payment Setup</strong> - Arrange pension payment method and beneficiary enrollment</li>
			</ol>
			<p>Total estimated time: 24 hours over 30-day processing period</p>
		""",
		"stages": [
			{
				"stage_number": 1,
				"stage_name": "Eligibility Verification",
				"stage_type": "Vetting",
				"required": 1,
				"estimated_hours": 4
			},
			{
				"stage_number": 2,
				"stage_name": "Income & Poverty Assessment",
				"stage_type": "Technical Assessment",
				"required": 1,
				"estimated_hours": 12
			},
			{
				"stage_number": 3,
				"stage_name": "Approval Decision",
				"stage_type": "Decision",
				"required": 1,
				"estimated_hours": 6
			},
			{
				"stage_number": 4,
				"stage_name": "Payment Setup",
				"stage_type": "Implementation",
				"required": 1,
				"estimated_hours": 2
			}
		]
	})

	template.insert(ignore_permissions=True)
	print(f"✅ Created Assessment Template: {template.name}")


def create_task_templates():
	"""Create Task Templates for SPISC assessment stages"""

	task_templates = [
		# ==================== STAGE 1: ELIGIBILITY VERIFICATION ====================
		{
			"task_template_name": "SPISC-VET-001",
			"stage_type": "Vetting",
			"task_sequence": 1,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Verify Applicant Age Requirement",
			"task_description": """
				<p>Verify that the applicant meets the minimum age requirement for SPISC.</p>
				<p><strong>Requirements:</strong></p>
				<ul>
					<li>Applicant must be 60 years or older</li>
					<li>Age calculated from birth date in application</li>
					<li>Cross-reference with birth certificate if provided</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
				<p><strong>Applicant Age:</strong> {{doc.age}} years</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "Consent Planner",
			"required_team": "Planning Team",
			"estimated_hours": 1.0
		},
		{
			"task_template_name": "SPISC-VET-002",
			"stage_type": "Vetting",
			"task_sequence": 2,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Verify Residency Requirements",
			"task_description": """
				<p>Confirm applicant's residential address and verify local residency.</p>
				<p><strong>Requirements:</strong></p>
				<ul>
					<li>Barangay and municipality fields must be completed</li>
					<li>Address must be within jurisdiction</li>
					<li>Cross-reference with proof of residency if provided</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "Consent Planner",
			"required_team": "Planning Team",
			"estimated_hours": 1.5
		},
		{
			"task_template_name": "SPISC-VET-003",
			"stage_type": "Vetting",
			"task_sequence": 3,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Check for Existing Pension Benefits",
			"task_description": """
				<p>Verify applicant is not receiving SSS/GSIS or other government pension.</p>
				<p><strong>Checks Required:</strong></p>
				<ul>
					<li>Review SSS number field (should be for ID only, not active pension)</li>
					<li>Check income source field for "Pension" indicator</li>
					<li>Verify no duplicate pension benefits</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "Consent Planner",
			"required_team": "Planning Team",
			"estimated_hours": 1.5
		},

		# ==================== STAGE 2: INCOME & POVERTY ASSESSMENT ====================
		{
			"task_template_name": "SPISC-TA-001",
			"stage_type": "Technical Assessment",
			"task_sequence": 1,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Verify Monthly Income Threshold",
			"task_description": """
				<p>Assess applicant's monthly income against poverty threshold.</p>
				<p><strong>Requirements:</strong></p>
				<ul>
					<li>Monthly income must be ≤ PHP 10,000</li>
					<li>Verify income source documentation</li>
					<li>Document any warnings if income exceeds threshold</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline User",
			"required_team": "Planning Team",
			"estimated_hours": 3.0
		},
		{
			"task_template_name": "SPISC-TA-002",
			"stage_type": "Technical Assessment",
			"task_sequence": 2,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Assess Household Composition",
			"task_description": """
				<p>Review household data to assess poverty level and dependency status.</p>
				<p><strong>Review Points:</strong></p>
				<ul>
					<li>Number of household members</li>
					<li>Number of dependents</li>
					<li>Living arrangement (own home, renting, with family)</li>
					<li>Household income sources</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "Medium",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline User",
			"required_team": "Planning Team",
			"estimated_hours": 3.0
		},
		{
			"task_template_name": "SPISC-TA-003",
			"stage_type": "Technical Assessment",
			"task_sequence": 3,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Verify Supporting Documents",
			"task_description": """
				<p>Verify all required documents are submitted and valid.</p>
				<p><strong>Required Documents:</strong></p>
				<ul>
					<li>Birth Certificate or valid ID proving age</li>
					<li>Barangay Certificate of Indigency</li>
					<li>Proof of residency</li>
					<li>Other supporting documents as needed</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline User",
			"required_team": "Planning Team",
			"estimated_hours": 3.0
		},
		{
			"task_template_name": "SPISC-TA-004",
			"stage_type": "Technical Assessment",
			"task_sequence": 4,
			"is_active": 1,
			"is_mandatory": 0,
			"auto_assign": 1,
			"task_title": "Conduct Home Visit (if required)",
			"task_description": """
				<p>Optional home visit for verification in unclear cases.</p>
				<p><strong>When Required:</strong></p>
				<ul>
					<li>Incomplete address information</li>
					<li>Unclear living situation</li>
					<li>Conflicting information in application</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
				<p><em>This task can be skipped if not required.</em></p>
			""",
			"priority": "Low",
			"task_type": "Parallel",
			"required_role": "CouncilsOnline User",
			"required_team": "Planning Team",
			"estimated_hours": 3.0
		},

		# ==================== STAGE 3: APPROVAL DECISION ====================
		{
			"task_template_name": "SPISC-DEC-001",
			"stage_type": "Decision",
			"task_sequence": 1,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Review Complete Assessment",
			"task_description": """
				<p>Review all assessment findings and prepare for decision.</p>
				<p><strong>Review Checklist:</strong></p>
				<ul>
					<li>All eligibility criteria met (age, income, residency)</li>
					<li>No disqualifying factors (existing pension, etc.)</li>
					<li>All required documents verified</li>
					<li>Assessment findings documented</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
				<p><strong>Stage:</strong> {{stage.stage_name}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline Admin",
			"required_team": "Management",
			"estimated_hours": 2.0
		},
		{
			"task_template_name": "SPISC-DEC-002",
			"stage_type": "Decision",
			"task_sequence": 2,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Prepare Decision Memo",
			"task_description": """
				<p>Document the eligibility decision with supporting rationale.</p>
				<p><strong>Decision Memo Must Include:</strong></p>
				<ul>
					<li>Recommendation: Eligible / Ineligible / Pending</li>
					<li>Key findings from assessment</li>
					<li>Rationale for decision</li>
					<li>Any special conditions or notes</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline Admin",
			"required_team": "Management",
			"estimated_hours": 2.0
		},
		{
			"task_template_name": "SPISC-DEC-003",
			"stage_type": "Decision",
			"task_sequence": 3,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Obtain Final Approval",
			"task_description": """
				<p>Get final approval from authorized approver (Council/Manager).</p>
				<p><strong>Approval Requirements:</strong></p>
				<ul>
					<li>Decision memo reviewed</li>
					<li>All assessment stages completed</li>
					<li>Eligibility determination approved</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
				<p><em>Update SPISC Application eligibility_status field after approval.</em></p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline Admin",
			"required_team": "Management",
			"estimated_hours": 2.0
		},

		# ==================== STAGE 4: PAYMENT SETUP ====================
		{
			"task_template_name": "SPISC-IMP-001",
			"stage_type": "Implementation",
			"task_sequence": 1,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Configure Payment Method",
			"task_description": """
				<p>Setup approved applicant's pension payment method.</p>
				<p><strong>Payment Setup Tasks:</strong></p>
				<ul>
					<li>Verify payment method selection (Bank Deposit / Cash Pickup)</li>
					<li>If Bank Deposit: Verify bank account details</li>
					<li>If Cash Pickup: Confirm pickup location</li>
					<li>Create User Bank Account record if applicable</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline Admin",
			"required_team": "Administration",
			"estimated_hours": 1.0
		},
		{
			"task_template_name": "SPISC-IMP-002",
			"stage_type": "Implementation",
			"task_sequence": 2,
			"is_active": 1,
			"is_mandatory": 1,
			"auto_assign": 1,
			"task_title": "Issue Approval Notification",
			"task_description": """
				<p>Send approval notification to applicant with next steps.</p>
				<p><strong>Notification Must Include:</strong></p>
				<ul>
					<li>Approval confirmation</li>
					<li>Pension amount and payment schedule</li>
					<li>Payment method details</li>
					<li>When to expect first payment</li>
					<li>Contact information for questions</li>
				</ul>
				<p><strong>Application:</strong> {{doc.request_number}}</p>
			""",
			"priority": "High",
			"task_type": "Sequential",
			"required_role": "CouncilsOnline Admin",
			"required_team": "Administration",
			"estimated_hours": 1.0
		}
	]

	created_count = 0
	for task_data in task_templates:
		if frappe.db.exists("Task Template", task_data["task_template_name"]):
			print(f"Task Template '{task_data['task_template_name']}' already exists")
			continue

		try:
			task_template = frappe.get_doc({
				"doctype": "Task Template",
				**task_data
			})
			task_template.insert(ignore_permissions=True)
			created_count += 1
			print(f"✅ Created Task Template: {task_data['task_template_name']}")
		except Exception as e:
			frappe.log_error(f"Failed to create task template {task_data['task_template_name']}: {str(e)}")
			print(f"❌ Error creating {task_data['task_template_name']}: {str(e)}")

	print(f"✅ Created {created_count} Task Templates for SPISC assessment")

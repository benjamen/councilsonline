# Full Resource Consent Lifecycle Testing Guide

## Overview

This document provides comprehensive testing scenarios for all consent types (Land Use, Subdivision, Discharge Permit, Water Permit, Coastal Permit) following RMA 1991 requirements and Hutt City Council processing patterns.

## Table of Contents

1. [Pre-application Stage](#0-pre-application-stage)
2. [Lodgement & Completeness Check (s88)](#1-lodgement--completeness-check-s88-rma)
3. [Allocation & Start of Processing](#2-allocation--start-of-processing)
4. [Further Information Request (s92)](#3-further-information-request-s92-rma)
5. [Notification Assessment (ss95-95E)](#4-notification-assessment-ss95-95e)
6. [Notification Processing](#5-notification-processing-if-notified)
7. [Hearing Stage](#6-hearing-stage-if-required)
8. [Decision & Reporting (s104-108)](#7-decision--reporting-s104-108)
9. [Post-decision Processes](#8-post-decision-processes)
10. [Objections & Appeals](#9-objections--appeals)
11. [Close-out](#10-close-out)
12. [Consent Type Specific Testing](#consent-type-specific-variations)
13. [Testing Scenario Packs](#testing-scenario-packs)

---

## 0. Pre-application Stage (Optional but Common)

### Purpose
Early engagement between applicant and council before formal lodgement. Used for complex applications to identify issues early.

### Test Steps

#### TC-PRE-001: Customer Requests Pre-app Meeting
**Objective**: Verify pre-app request creation and assignment

1. Log in as Customer/Applicant
2. Navigate to Requests → New Request
3. Select request type: "Pre-Application Meeting"
4. Fill in:
   - Property address
   - Proposed activity description
   - Upload concept plans (optional)
5. Submit request
6. **Verify**:
   - Request status = "Open"
   - Request appears in planner queue
   - Auto-assignment to duty planner (if configured)

#### TC-PRE-002: Planner Assigns Specialists
**Objective**: Verify specialist allocation for pre-app review

1. Log in as Planner
2. Open pre-app request
3. Click "Assign Specialists"
4. Add specialists:
   - Traffic Engineer
   - 3-Waters Engineer
   - Heritage Advisor (if applicable)
   - Ecology Specialist (if applicable)
5. Set review deadline: 5 working days
6. Save
7. **Verify**:
   - Task created for each specialist
   - Email notifications sent
   - Specialist dashboard shows pending review

#### TC-PRE-003: Pre-app Meeting Conducted
**Objective**: Verify meeting scheduling and notes capture

1. Planner schedules meeting using Frappe Events
2. Add meeting details:
   - Date/time
   - Attendees (applicant, planner, specialists)
   - Location/online meeting link
3. Conduct meeting
4. Capture meeting notes in Request "Internal Notes"
5. Mark meeting as completed
6. **Verify**:
   - Event appears in calendar
   - Notes saved and accessible
   - Meeting history visible in timeline

#### TC-PRE-004: Issue Pre-app Advice
**Objective**: Verify pre-app advice document generation

1. Planner compiles feedback from specialists
2. Draft pre-app advice letter
3. Include:
   - Key issues identified
   - Suggested mitigation
   - Likely consent pathway
   - Further information needed for formal application
4. Manager reviews and approves
5. Send to applicant via Request communication
6. **Verify**:
   - PDF generated correctly
   - Applicant receives email with attachment
   - Request status updates to "Completed"
   - Applicant can view advice in portal

---

## 1. Lodgement & Completeness Check (s88 RMA)

### RMA Reference
Section 88: Duty to check application complete before proceeding

### Test Steps

#### TC-S88-001: Complete Application Lodgement
**Objective**: Verify successful lodgement of complete application

**Prerequisites**: Customer account created, property verified

1. Log in as Customer
2. Navigate to New Request → Resource Consent Application
3. Select consent type: "Land Use"
4. Fill in all required sections:
   - Applicant details
   - Property details
   - Activity description
   - Assessment of Environmental Effects (AEE)
   - Planning assessment
   - Affected parties
   - Specialist reports (upload PDFs)
   - Proposed conditions
5. Upload all required documents:
   - Site plan
   - Floor plans
   - Elevations
   - Specialist reports
6. Pay application fee (if integrated)
7. Submit application
8. **Verify**:
   - Request status = "Submitted"
   - Acknowledgement email received
   - Application number generated
   - Appears in planner queue

#### TC-S88-002: Incomplete Application - Missing Documents
**Objective**: Verify auto-validation detects missing documents

1. Log in as Customer
2. Start new Resource Consent Application
3. Fill in basic details but **omit**:
   - Site plan
   - Assessment of Effects
4. Attempt to submit
5. **Verify**:
   - Validation error displayed
   - Lists missing required fields
   - Cannot submit until complete
   - Draft saved automatically

#### TC-S88-003: Planner Rejects as Incomplete (s88(3))
**Objective**: Verify manual incompleteness workflow

1. Log in as Planner
2. Open newly lodged application
3. Review completeness:
   - Check all sections filled
   - Check documents uploaded
   - Identify missing: Traffic Impact Assessment
4. Click "Request More Information (s88)"
5. Draft s88 letter:
   - List specific information required
   - Set deadline: 10 working days
6. Send to applicant
7. **Verify**:
   - Request status = "Further Information Required (s88)"
   - **Statutory clock does NOT start**
   - `statutory_clock_started` remains empty
   - Email sent to applicant
   - RFI visible in applicant portal

#### TC-S88-004: Applicant Resubmits Information
**Objective**: Verify information resubmission workflow

1. Log in as Customer (received s88 RFI)
2. Open application
3. See "Further Information Required" notice
4. Click "Upload Additional Information"
5. Upload Traffic Impact Assessment PDF
6. Add cover letter explaining submission
7. Submit response
8. **Verify**:
   - Status updates to "Information Received - Pending Review"
   - Planner notified
   - Documents appear in application attachments
   - Response timestamp recorded

#### TC-S88-005: Accept as Complete - Start Clock
**Objective**: Verify clock start on completeness acceptance

1. Log in as Planner
2. Open application with information received
3. Review submitted TIA
4. Determine application now complete
5. Click "Accept as Complete (s88)"
6. Confirm action
7. **Verify**:
   - Status = "Accepted - Processing"
   - **Statutory clock STARTS**
   - `statutory_clock_started` = current datetime
   - `working_days_elapsed` = 0
   - `working_days_remaining` = 20 (or configured SLA)
   - Acknowledgement letter auto-generated
   - Letter includes:
     - Application deemed complete
     - Statutory timeframe started
     - Expected decision date
   - Clock Summary Panel appears at top of form

---

## 2. Allocation & Start of Processing

#### TC-ALLOC-001: Assign Processing Planner
**Objective**: Verify planner assignment workflow

1. Team Leader opens application queue
2. View unassigned applications
3. Select application
4. Click "Assign to Planner"
5. Choose planner from dropdown
6. Add assignment notes
7. Save
8. **Verify**:
   - Application assigned to planner
   - Planner's name appears in "Assigned To" field
   - Task created in planner's task list
   - Planner receives email notification
   - Timeline shows assignment event

#### TC-ALLOC-002: Assign Internal Specialists
**Objective**: Verify specialist review request

1. Processing planner opens assigned application
2. Click "Request Internal Reviews"
3. Select specialists:
   - ☑ Traffic Engineer
   - ☑ 3-Waters Infrastructure
   - ☑ Parks & Reserves
   - ☐ Contaminated Land (not needed)
4. Set review deadline: 10 working days
5. Add review scope notes
6. Send requests
7. **Verify**:
   - Task created for each specialist
   - Email notifications sent with application link
   - Specialist can access read-only view
   - "Internal Reviews" section shows pending reviews
   - Timeline records review requests

#### TC-ALLOC-003: Specialist Submits Review
**Objective**: Verify specialist feedback capture

1. Log in as Traffic Engineer
2. Open task "Review RC-2025-001"
3. Click task link to application
4. Review traffic assessment
5. Navigate to "Internal Reviews" tab
6. Find assigned review
7. Add comments:
   - "Traffic assessment adequate"
   - "Recommend condition: Vehicle crossing approved by roading team"
   - "No objections subject to condition"
8. Set recommendation: "Approve with Conditions"
9. Mark review as Complete
10. **Verify**:
    - Review status = "Completed"
    - Comments saved
    - Planner notified
    - Review visible in application
    - Timeline shows specialist feedback received

#### TC-ALLOC-004: Set Processing Pathway
**Objective**: Verify initial pathway determination

1. Planner reviews application complexity
2. Click "Set Processing Pathway"
3. Options:
   - ○ Non-Notified (default)
   - ○ Limited Notified (affected parties)
   - ○ Fully Notified (public)
4. Select: "Non-Notified" (initial assessment, subject to s95 review)
5. Save
6. **Verify**:
   - `processing_pathway` field set
   - Pathway badge displays on form
   - Drives subsequent workflow steps
   - Can be changed later if notification required

#### TC-ALLOC-005: Conduct Site Visit
**Objective**: Verify site visit using Frappe Events

1. Planner schedules site visit
2. Create new Event:
   - Event type: "Site Visit"
   - Link to: Resource Consent Application
   - Date/time
   - Location: property address
   - Attendees: Planner, applicant (optional)
3. Conduct site visit
4. After visit, add event notes:
   - Observations
   - Photos (upload to application attachments)
   - Issues identified
   - Confirmation of details
5. Mark event as completed
6. **Verify**:
   - Event appears in application timeline
   - Photos attached to application
   - Notes searchable
   - Site visit date recorded

---

## 3. Further Information Request (s92 RMA)

### RMA Reference
Section 92: Power to commission reports and request further information

### Test Steps

#### TC-S92-001: Identify Need for RFI
**Objective**: Verify RFI initiation

1. Planner reviews application
2. Identifies issues:
   - Acoustic assessment missing noise levels
   - Insufficient detail on landscaping plan
3. Click "Request Further Information (s92)"
4. **Verify**:
   - RFI form opens
   - Can draft request letter
   - Can select RFI category (s92(1) or s92(2))

#### TC-S92-002: Draft and Approve s92 Request
**Objective**: Verify RFI approval workflow

1. Planner drafts s92 request:
   - "Provide updated acoustic assessment showing noise levels at boundary"
   - "Provide landscape plan showing plant species and maturity height"
2. Set response deadline: 15 working days
3. Save as draft
4. Send to Team Leader for review
5. Team Leader reviews and approves
6. **Verify**:
   - Draft saved correctly
   - Approval workflow triggered
   - Team Leader can view and edit
   - Cannot send until approved

#### TC-S92-003: Issue s92 - Clock STOPS
**Objective**: Verify clock stops automatically on RFI issue

1. Team Leader approves s92 request
2. Click "Issue RFI"
3. Confirm action
4. **Verify**:
   - Status = "Further Information Required (s92)"
   - **Statutory clock STOPS**
   - `statutory_clock_stopped` = current datetime
   - `working_days_elapsed` frozen (e.g., at 8 days)
   - Clock Summary Panel shows "⏸ Stopped" badge (gray)
   - RFI letter generated and sent to applicant
   - Email notification to applicant
   - RFI appears in applicant portal
   - Timeline records RFI issue event
   - Clock Exclusion Period record created:
     - Type: "RFI Issued"
     - Started date: current date
     - Status: Active

#### TC-S92-004: Applicant Provides Partial Response
**Objective**: Verify partial response rejection workflow

1. Log in as Applicant (received s92 RFI)
2. Open application
3. See RFI notice with requested items:
   - [  ] Updated acoustic assessment
   - [  ] Landscape plan
4. Upload ONLY acoustic assessment
5. Submit response with note: "Landscape plan to follow"
6. **Verify**:
   - Status = "Information Received - Under Review"
   - Clock remains STOPPED (partial response)
   - Planner notified of submission

#### TC-S92-005: Planner Rejects Partial Response
**Objective**: Verify response rejection workflow

1. Planner reviews submitted information
2. Notes only 1 of 2 items provided
3. Click "Reject Response" (within s92 workflow)
4. Add rejection reason: "Landscape plan still outstanding"
5. Send notification to applicant
6. **Verify**:
   - Status reverts to "Further Information Required (s92)"
   - Clock remains STOPPED
   - Applicant notified of rejection
   - Original RFI deadline still applies (or extended if agreed)
   - Timeline shows rejection

#### TC-S92-006: Applicant Provides Complete Response
**Objective**: Verify full response submission

1. Applicant receives rejection notification
2. Prepares landscape plan
3. Uploads both documents:
   - ☑ Updated acoustic assessment (resubmit for completeness)
   - ☑ Landscape plan (new)
4. Submit response
5. **Verify**:
   - Both files attached
   - Response marked as complete by applicant
   - Planner notified

#### TC-S92-007: Accept Response - Clock RESTARTS
**Objective**: Verify clock restart on RFI acceptance

1. Planner reviews complete response
2. Checks both documents adequate
3. Click "Accept Information (s92)"
4. Confirm action
5. **Verify**:
   - Status = "Accepted - Processing"
   - **Statutory clock RESTARTS**
   - `statutory_clock_stopped` = NULL
   - `working_days_elapsed` resumes from 8 (where it left off)
   - Clock Summary Panel shows "▶ Running" badge
   - Acceptance letter sent to applicant
   - Timeline records clock restart
   - Clock Exclusion Period record updated:
     - Ended date: current date
     - Status: Closed
     - Working days excluded: calculated

#### TC-S92-008: Audit Clock Exclusion Period
**Objective**: Verify exclusion period calculation

1. Navigate to Clock Exclusion Periods tab
2. Find RFI exclusion record
3. **Verify** fields:
   - Exclusion type: "RFI Issued"
   - Reference: s92 request document
   - Started date: (date clock stopped)
   - Ended date: (date clock restarted)
   - Working days excluded: (auto-calculated)
   - Calendar days: (total days between start/end)
4. **Verify** calculation excludes:
   - Weekends
   - Public holidays
   - Aligns with `calculate_working_days_between()` function

---

## 4. Notification Assessment (ss95-95E)

### RMA Reference
Section 95-95E: Notification requirements and decision

### Test Steps

#### TC-S95-001: Conduct Notification Test
**Objective**: Verify notification assessment

1. Planner reviews application for notification
2. Click "Assess Notification" (Notification section)
3. Complete s95 checklist:
   - ☐ Rule permits non-notification?
   - ☑ Adverse effects more than minor?
   - ☐ Written approval from all affected persons?
   - ☐ Special circumstances?
4. Answer questions:
   - Adverse effects on environment: Minor to Moderate
   - Affected persons identified: 2 neighbors
   - Written approvals obtained: No
5. System suggests: "Limited Notification recommended"
6. **Verify**:
   - Notification recommendation generated
   - Based on s95A-E criteria
   - Documented reasoning

#### TC-S95-002: Recommend Limited Notification
**Objective**: Verify limited notification recommendation

1. Planner reviews suggestion
2. Agrees with limited notification
3. Identifies affected persons:
   - 10 Smith Street (adjacent property owner)
   - 14 Smith Street (adjacent property owner)
4. Click "Recommend Limited Notification"
5. Add justification:
   - "Activity exceeds permitted standards for building height"
   - "Shading effects on 10 & 14 Smith Street"
   - "Effects on other persons minor"
6. Save recommendation
7. **Verify**:
   - Recommendation status: "Pending Approval"
   - Affected persons list saved
   - Justification recorded

#### TC-S95-003: Manager Approves Notification Decision
**Objective**: Verify approval workflow

1. Log in as Team Leader/Manager
2. Open application
3. Navigate to Notification section
4. Review planner recommendation
5. Review affected persons list
6. Review s95 assessment
7. Click "Approve Notification Decision"
8. **Verify**:
   - `notification_level` = "Limited Notified"
   - `notification_determined_date` = current date
   - Approval recorded
   - Timeline shows decision
   - Next step: Issue notification

#### TC-S95-004: Issue Notification Decision to Applicant
**Objective**: Verify notification decision communication

1. Click "Issue Notification Decision"
2. System generates letter:
   - Decision: Limited Notification
   - Affected persons: listed
   - Reason: per s95E(2)
   - Next steps: Serve notice on affected persons
3. Send letter to applicant
4. **Verify**:
   - Letter generated correctly
   - Emailed to applicant
   - Available in applicant portal
   - Status updates

---

## 5. Notification Processing (if notified)

### Limited Notification Workflow

#### TC-LN-001: Serve Notice on Affected Persons
**Objective**: Verify affected party notification

1. Planner clicks "Serve Limited Notification"
2. System shows affected persons list:
   - 10 Smith Street - John Doe
   - 14 Smith Street - Jane Smith
3. For each affected person:
   - Generate notice letter (per s95B)
   - Includes:
     - Description of proposed activity
     - Effects on affected person
     - Right to make submission (10 working days)
     - Submission form
4. Send notices via:
   - ☑ Email (if available)
   - ☑ Postal mail
5. Record service:
   - Service date
   - Service method
6. **Verify**:
   - Notice letters generated correctly
   - Service recorded for each person
   - Submission deadline calculated (10 working days)
   - Timeline shows service dates
   - Affected party table updated with service status

#### TC-LN-002: Affected Party Submits Opposition
**Objective**: Verify submission receipt and processing

1. Affected person (Jane Smith, 14 Smith St) receives notice
2. Prepares submission opposing application:
   - Objects to building height
   - Concerns about loss of sunlight
   - Privacy concerns
3. Submits via:
   - Option A: Customer portal (if registered)
   - Option B: Email to council
   - Option C: Postal mail
4. Council staff receipts submission
5. **Verify**:
   - Submission recorded in system
   - Linked to application
   - Submitter details captured
   - Submission date recorded
   - Copy provided to applicant (per s96(4))
   - Planner can view submission content

#### TC-LN-003: Written Approval from Affected Party
**Objective**: Verify written approval capture

1. Affected person (John Doe, 10 Smith St) provides written approval
2. Applicant uploads approval document
3. Planner reviews approval:
   - Signed by affected person
   - Clearly states approval
   - No conditions attached
4. Click "Record Written Approval"
5. Link to affected party record
6. **Verify**:
   - Approval document attached
   - Affected party status = "Approved"
   - Count of approvals updates
   - If all affected persons approve → may convert to non-notified

#### TC-LN-004: Late Submission Received
**Objective**: Verify late submission handling

1. Submission received 12 working days after notice
2. System flags as LATE
3. Planner reviews late submission
4. Options:
   - Accept (if minor lateness, good reason)
   - Reject (strict compliance)
5. Planner chooses: Accept (submitted 1 day late, postal delay)
6. **Verify**:
   - Late submission recorded
   - Marked as "Late - Accepted"
   - Justification documented
   - Included in summary of submissions

### Public Notification Workflow

#### TC-PN-001: Publicly Notify Application
**Objective**: Verify public notification process

1. Application with `notification_level` = "Fully Notified"
2. Planner clicks "Publish Public Notice"
3. Generate public notice content:
   - Application details
   - Applicant name
   - Property location
   - Description of proposal
   - Submission period: 20 working days
   - Submission address and form
4. Publish notice:
   - ☑ Council website
   - ☑ Newspaper (if required)
   - ☑ On-site sign (if required)
5. Record publication:
   - Publication date
   - Publication method
   - Closing date for submissions
6. **Verify**:
   - Notice published on public portal
   - Submission form available for download
   - Closing date calculated correctly (20 working days)
   - Public can view application online
   - Timeline shows publication

#### TC-PN-002: Public Submits Online
**Objective**: Verify online submission by public

1. Member of public visits council website
2. Finds notified applications list
3. Views application RC-2025-001
4. Clicks "Make a Submission"
5. Fills out submission form:
   - Name, contact details
   - Support / Oppose / Neutral
   - Reasons
   - Wishes to be heard at hearing: Yes / No
6. Uploads supporting documents (optional)
7. Submits form
8. **Verify**:
   - Submission recorded
   - Submitter receives confirmation email
   - Submission appears in council queue
   - Planner can view submission
   - Counted in total submissions

#### TC-PN-003: Generate Summary of Submissions
**Objective**: Verify submission summary generation

1. Submission period closes (20 working days elapsed)
2. Planner clicks "Generate Submission Summary"
3. System compiles:
   - Total submissions received: 15
   - Support: 2
   - Oppose: 10
   - Neutral: 3
   - Submitters wishing to be heard: 8
   - Key themes: height, traffic, privacy, character
4. Planner reviews and edits summary
5. Save summary document
6. Provide to applicant (s96)
7. **Verify**:
   - Summary generated correctly
   - Statistics accurate
   - Themes identified
   - Provided to applicant
   - Available for hearing if required

---

## 6. Hearing Stage (if required)

#### TC-HEAR-001: Determine Hearing Required
**Objective**: Verify hearing decision

1. Planner reviews submissions
2. Notes: 8 submitters wish to be heard
3. Click "Hearing Required"
4. Set `hearing_required` = Yes
5. **Verify**:
   - Hearing sections appear on form
   - Hearing scheduling options available
   - Notification to applicant

#### TC-HEAR-002: Appoint Hearing Panel
**Objective**: Verify commissioner appointment

1. Team Leader/Manager appoints panel
2. Options:
   - Council Hearings Committee
   - Independent Commissioner
   - Panel of Commissioners
3. Select: "Independent Commissioner - Jane Wilson"
4. Record appointment:
   - Commissioner name
   - Appointment date
   - Terms of reference
5. **Verify**:
   - `hearing_commissioners` field populated
   - Commissioner notified
   - Applicant informed of panel

#### TC-HEAR-003: Schedule Hearing
**Objective**: Verify hearing scheduling

1. Planner/Administrator schedules hearing
2. Create Event:
   - Type: Hearing
   - Date: 15 December 2025, 9:00 AM
   - Venue: Council Chambers / Online
   - Duration: 2 hours
3. Link to Resource Consent Application
4. Add attendees:
   - Commissioner(s)
   - Applicant
   - Submitters (who wish to be heard)
   - Reporting planner
5. Send hearing notice (10 working days before):
   - Hearing date, time, venue
   - Procedure
   - Evidence deadlines
6. **Verify**:
   - Event created
   - Notices sent to all parties
   - Calendar invites sent
   - Hearing date recorded in application

#### TC-HEAR-004: Prepare s42A Report
**Objective**: Verify planner's report

1. Planner drafts s42A report:
   - Description of proposal
   - Summary of submissions
   - Assessment of effects
   - Analysis of RMA provisions
   - Response to submissions
   - Recommendation: Grant / Refuse / Grant with conditions
   - Recommended conditions
2. Review by Team Leader
3. Circulate to commissioner
4. Provide to applicant and submitters (5 working days before hearing)
5. **Verify**:
   - Report saved in system
   - Linked to application
   - Circulated to all parties
   - Available in hearing pack

#### TC-HEAR-005: Applicant Provides Evidence
**Objective**: Verify evidence management

1. Applicant submits evidence (3 working days before hearing)
2. Upload documents:
   - Planning evidence - Expert Planner
   - Acoustic evidence - Acoustic Specialist
   - Rebuttal to submissions
3. Evidence circulated to:
   - Commissioner
   - Submitters
   - Council planner
4. **Verify**:
   - Evidence uploaded to application
   - Distributed to parties
   - Available in hearing portal

#### TC-HEAR-006: Conduct Hearing
**Objective**: Verify hearing execution

1. Hearing commences at scheduled time
2. Commissioner introduces panel and procedure
3. Presentations:
   - Applicant (15 minutes)
   - Submitters in support (5 min each)
   - Submitters in opposition (5 min each)
   - Council reporting planner (s42A report)
   - Applicant right of reply
4. Commissioner questions parties
5. Hearing closes
6. Record hearing:
   - Hearing minutes
   - Attendance register
   - Recording (if made)
7. **Verify**:
   - Hearing minutes saved
   - Attendance recorded
   - Event marked as completed
   - Timeline updated

#### TC-HEAR-007: Commissioner Deliberates
**Objective**: Verify post-hearing process

1. Commissioner reviews:
   - Application
   - Submissions
   - Evidence presented
   - s42A report
   - Hearing presentations
2. May request additional information (s41B)
3. Commissioner reaches decision
4. **Verify**:
   - Deliberation period tracked
   - Additional information requests recorded (if any)
   - Decision ready for drafting

---

## 7. Decision & Reporting (s104-108)

#### TC-DEC-001: Draft Decision
**Objective**: Verify decision document preparation

1. Commissioner/Planner drafts decision:
   - Procedural history
   - Description of proposal
   - Submissions summary
   - Assessment under s104:
     - Actual and potential effects
     - Relevant RMA Part 2 matters
     - District Plan provisions
     - Other matters
   - Conclusion: Grant with conditions
   - Conditions (detailed)
   - Reasons for decision
   - Advisory notes
2. Decision reviewed by legal (if required)
3. Commissioner signs decision
4. **Verify**:
   - Decision document complete
   - Follows RMA requirements
   - Conditions clear and enforceable
   - Signed and dated

#### TC-DEC-002: Issue Decision - Clock STOPS
**Objective**: Verify decision issuance and clock stop

1. Click "Issue Decision"
2. Set decision details:
   - Decision type: Granted with Conditions
   - Decision date: current date
   - Decision maker: Commissioner Jane Wilson
3. Attach signed decision PDF
4. Confirm issuance
5. **Verify**:
   - Status = "Decision Issued"
   - **Statutory clock STOPS permanently**
   - `statutory_clock_stopped` = decision date
   - Final working days recorded
   - Decision letter generated
   - Served on:
     - ☑ Applicant
     - ☑ Submitters (if notified)
   - Timeline shows decision issuance

#### TC-DEC-003: Upload Conditions
**Objective**: Verify condition management

1. Navigate to Conditions tab
2. Click "Import from Decision"
3. System extracts conditions from decision document:
   - Condition 1: General accordance with plans
   - Condition 2: Hours of operation
   - Condition 3: Acoustic compliance
   - etc.
4. For each condition:
   - Category: General / Timing / Monitoring / etc.
   - Compliance status: Not Started
   - Monitoring required: Yes/No
5. Save conditions
6. **Verify**:
   - All conditions imported
   - Categorized correctly
   - Linked to consent
   - Available for monitoring team

#### TC-DEC-004: Applicant Views Decision in Portal
**Objective**: Verify customer access

1. Log in as Applicant
2. Navigate to My Requests
3. Open application
4. See status: "Decision Issued - Granted with Conditions"
5. Download decision PDF
6. Review conditions
7. **Verify**:
   - Decision accessible
   - Status clear
   - Conditions viewable
   - Next steps explained (objection period, commencement)

---

## 8. Post-decision Processes

### For Subdivision Consents

#### TC-SUB-001: s223 Approval (Survey Plan)
**Objective**: Verify survey plan approval workflow

1. Applicant submits survey plan to council
2. Upload PDF of approved survey plan
3. Planner reviews:
   - Compliance with consent conditions
   - Lot sizes correct
   - Easements shown
   - Dimensions accurate
4. Planner approves s223 certificate
5. Click "Approve s223"
6. Generate s223 approval document
7. **Verify**:
   - s223 approval recorded
   - Certificate generated
   - Approval date set
   - Status = "s223 Approved"
   - Next step: s224 process

#### TC-SUB-002: s224(c) Certification
**Objective**: Verify conditions satisfaction certificate

1. Applicant requests s224 certificate
2. Planner reviews consent conditions:
   - ☑ Condition 1: Engineering plans approved
   - ☑ Condition 2: Financial contributions paid
   - ☑ Condition 3: Legal documents registered
   - ☐ Condition 4: Landscaping complete (outstanding)
3. Planner conducts site visit
4. Confirms outstanding landscaping incomplete
5. Informs applicant
6. Applicant completes landscaping
7. Planner reinspects
8. All conditions satisfied
9. Click "Issue s224(c) Certificate"
10. Generate certificate
11. **Verify**:
    - All conditions marked as "Complied"
    - Certificate generated
    - Status = "s224 Certified"
    - Subdivision can proceed
    - Titles can be issued

#### TC-SUB-003: Process Legal Documents
**Objective**: Verify covenant/easement processing

1. Applicant submits legal instruments:
   - Consent Notice (height restriction)
   - Easement (right of way)
   - Covenant (landscape maintenance)
2. Planner reviews:
   - Drafted by solicitor
   - Complies with conditions
   - Legally sound
3. Planner approves for registration
4. Documents sent to LINZ
5. **Verify**:
   - Documents saved in system
   - Approval recorded
   - LINZ reference number captured
   - Consent Notice registered on title

### For Land Use Consents

#### TC-LU-001: Initiate Monitoring
**Objective**: Verify monitoring request creation

1. Decision issued with monitoring conditions
2. Planner creates Monitoring Request
3. Link to Resource Consent Application
4. Specify monitoring requirements:
   - Condition 3: Noise monitoring required annually
   - Condition 7: Landscaping inspection after 1 year
5. Set monitoring schedule
6. Assign to Monitoring Officer
7. **Verify**:
   - Monitoring request created
   - Linked to consent
   - Monitoring officer notified
   - Schedule set

#### TC-LU-002: Conduct Compliance Inspection
**Objective**: Verify inspection workflow

1. Monitoring Officer receives task
2. Schedule inspection
3. Conduct site visit
4. Check compliance:
   - ☑ Hours of operation adhered to
   - ☑ Parking spaces provided as consented
   - ☐ Landscaping not yet mature (acceptable)
5. Take photos
6. Complete inspection report
7. **Verify**:
   - Report saved
   - Photos attached
   - Compliance status updated
   - Non-compliance issues flagged (if any)

#### TC-LU-003: Issue Abatement Notice (Non-compliance)
**Objective**: Verify enforcement action

1. Inspection reveals breach: Operating outside consented hours
2. Monitoring Officer drafts abatement notice
3. Manager approves
4. Issue notice to consent holder
5. Set compliance deadline
6. **Verify**:
   - Abatement notice generated
   - Served on consent holder
   - Deadline set
   - Enforcement action recorded
   - Follow-up inspection scheduled

---

## 9. Objections & Appeals

#### TC-OBJ-001: Applicant Lodges Objection (s357)
**Objective**: Verify objection receipt

1. Applicant disagrees with decision condition
2. Lodges objection within 15 working days
3. Uploads objection document:
   - Condition objected to: Condition 5 (hours of operation)
   - Grounds: Unreasonably restrictive
   - Requests amendment: Extend closing time to 8pm
4. Council receipts objection
5. **Verify**:
   - Objection recorded
   - Linked to application
   - Objection date within timeframe
   - Status = "Objection Received"

#### TC-OBJ-002: Process Objection
**Objective**: Verify internal review

1. Team Leader reviews objection
2. Considers:
   - Merit of objection
   - Effects of proposed amendment
   - Original decision reasoning
3. Options:
   - Uphold objection → amend condition
   - Reject objection → confirm original
   - Propose mediation
4. Team Leader decides: Partially uphold
5. Amend Condition 5: Hours 7am-7pm (compromise from original 7am-6pm)
6. Issue amended decision
7. **Verify**:
   - Objection outcome recorded
   - Amended decision issued
   - Applicant notified
   - Timeline updated

#### TC-APP-001: Environment Court Appeal Lodged
**Objective**: Verify appeal tracking

1. Submitter appeals decision to Environment Court
2. Council receives notice of appeal
3. Create Appeal record:
   - Link to application
   - Appellant: Jane Smith (submitter)
   - Grounds: Effects understated
   - Court reference: ENV-2025-WGTN-000123
4. Assign legal team
5. **Verify**:
   - Appeal recorded
   - Status = "Under Appeal"
   - Legal team notified
   - Court reference captured
   - Consent implementation stayed (if applicable)

---

## 10. Close-out

#### TC-CLOSE-001: Complete Consent Processing
**Objective**: Verify consent closure

1. All conditions satisfied (or monitoring ongoing)
2. No outstanding actions
3. Planner clicks "Close Consent"
4. Confirm closure
5. **Verify**:
   - Status = "Closed"
   - Completion date recorded
   - All tasks completed
   - If monitoring ongoing: Monitoring Request remains active
   - Consent record archived

#### TC-CLOSE-002: Transfer to Monitoring Team
**Objective**: Verify handover workflow

1. Consent with ongoing conditions closed
2. Monitoring Request created (if not already)
3. Link consent to Monitoring Request
4. Handover notes provided to monitoring team
5. **Verify**:
   - Monitoring team has access
   - Conditions clearly identified
   - Monitoring schedule set
   - Planning team can still view (read-only)

#### TC-CLOSE-003: Annual Reporting to MfE
**Objective**: Verify reporting compliance

1. End of financial year
2. Run report: "Consents Processed - Annual"
3. Report shows:
   - Total consents by type
   - Average processing time
   - Notification statistics
   - Decision outcomes
4. Export to Excel
5. Submit to Ministry for the Environment
6. **Verify**:
   - Report accurate
   - Data complete
   - Submission recorded

---

## Consent Type Specific Variations

### Land Use Consent

**Unique Testing Requirements:**
- Site visit essential (every case)
- Specialist inputs: urban design, traffic, parking, noise
- Monitoring typically required
- **Specific tests:**
  - TC-LU-SPEC-001: Noise modelling assessment
  - TC-LU-SPEC-002: Parking calculation verification
  - TC-LU-SPEC-003: Urban design panel review (if applicable)

### Subdivision Consent

**Unique Testing Requirements:**
- Heavy post-decision workflow (s223 + s224)
- Engineering plan approvals
- New lot creation + numbering
- **Specific tests:**
  - TC-SUB-SPEC-001: LINZ cadastral integration
  - TC-SUB-SPEC-002: Bonds & financial contributions
  - TC-SUB-SPEC-003: Title creation workflow
  - TC-SUB-SPEC-004: Infrastructure vesting

### Discharge Permit

**Unique Testing Requirements:**
- Environmental monitoring conditions
- Specialist environmental assessments
- **Specific tests:**
  - TC-DIS-SPEC-001: Regional council referral (if applicable)
  - TC-DIS-SPEC-002: Discharge monitoring plan
  - TC-DIS-SPEC-003: Environmental effects on waterways

### Water Permit

**Unique Testing Requirements:**
- Pump tests
- Hydrology assessments
- Flow allocation modelling
- **Specific tests:**
  - TC-WAT-SPEC-001: Pump test result verification
  - TC-WAT-SPEC-002: Aquifer monitoring conditions
  - TC-WAT-SPEC-003: Take limits and measurement

### Coastal Permit

**Unique Testing Requirements:**
- Coastal hazard assessments
- Cultural impact assessments
- Iwi partner involvement
- **Specific tests:**
  - TC-COAST-SPEC-001: Coastal inundation modelling
  - TC-COAST-SPEC-002: Iwi consultation (Treaty obligations)
  - TC-COAST-SPEC-003: Public access considerations

### Combined Consents

**Unique Testing Requirements:**
- Multiple specialists coordinated
- Single hearing with combined decision
- **Specific tests:**
  - TC-COMB-001: Create combined consent application (Land Use + Subdivision)
  - TC-COMB-002: Coordinate multiple specialist reviews
  - TC-COMB-003: Issue single integrated decision
  - TC-COMB-004: Manage separate post-decision processes (s223/s224 for subdivision component)

---

## Testing Scenario Packs

### Scenario Pack A: Smooth, Non-Notified Land Use
**Duration**: 15 working days
**Complexity**: Simple

**Test Flow:**
1. TC-S88-001: Lodged complete
2. TC-ALLOC-001: Assign planner
3. TC-ALLOC-002: Request specialist review (traffic only)
4. TC-ALLOC-003: Traffic specialist approves
5. TC-ALLOC-004: Set pathway: Non-notified
6. TC-ALLOC-005: Site visit conducted
7. TC-S95-001: Notification test → Non-notified
8. TC-DEC-001: Draft decision (Grant)
9. TC-DEC-002: Issue decision (15 working days elapsed)
10. TC-CLOSE-001: Close consent

**Success Criteria:**
- ✓ Clock runs continuously (no stops)
- ✓ Decision within 20 days
- ✓ No RFIs
- ✓ No notification

---

### Scenario Pack B: Incomplete, s88 Failure
**Duration**: 25 working days (clock starts late)
**Complexity**: Simple

**Test Flow:**
1. TC-S88-002: Lodged incomplete (validation catches missing site plan)
2. Customer corrects and resubmits
3. TC-S88-003: Planner rejects as incomplete s88(3) - missing acoustic report
4. **Clock NOT started**
5. TC-S88-004: Applicant submits acoustic report
6. TC-S88-005: Accept as complete - **Clock STARTS**
7. TC-ALLOC-001: Processing continues
8. (Continue as Scenario Pack A)

**Success Criteria:**
- ✓ Clock doesn't start until s88 acceptance
- ✓ Incompleteness clearly tracked
- ✓ Resubmission workflow smooth

---

### Scenario Pack C: s92 Stop/Start Workflow
**Duration**: 30 working days (20 processing + 10 RFI period excluded)
**Complexity**: Moderate

**Test Flow:**
1. TC-S88-001: Lodged complete
2. TC-ALLOC-001-003: Processing starts
3. TC-S92-001: Planner identifies need for RFI (day 8)
4. TC-S92-002: Draft s92 request
5. TC-S92-003: Issue s92 - **Clock STOPS** (elapsed: 8 days)
6. TC-S92-004: Applicant provides partial response
7. TC-S92-005: Planner rejects partial response - **Clock STILL STOPPED**
8. TC-S92-006: Applicant provides complete response
9. TC-S92-007: Accept response - **Clock RESTARTS** (elapsed: still 8 days)
10. TC-S92-008: Verify exclusion period recorded correctly
11. Processing continues for 12 more working days
12. TC-DEC-002: Decision issued (total: 8 + 12 = 20 working days processing)

**Success Criteria:**
- ✓ Clock stops on RFI issue
- ✓ Partial response doesn't restart clock
- ✓ Clock restarts on full acceptance
- ✓ Exclusion period calculated correctly
- ✓ Total working days = 20 (excluding RFI period)

---

### Scenario Pack D: Limited Notification
**Duration**: 35 working days
**Complexity**: Moderate-High

**Test Flow:**
1. TC-S88-005: Application complete, clock starts
2. TC-ALLOC-001-005: Processing and site visit
3. TC-S95-001: Conduct notification test
4. TC-S95-002: Recommend limited notification
5. TC-S95-003: Manager approves
6. TC-S95-004: Issue decision to applicant
7. TC-LN-001: Serve notice on 2 affected persons
8. TC-LN-002: 1 affected party submits opposition
9. TC-LN-003: 1 affected party provides written approval
10. TC-HEAR-001: Determine hearing NOT required (1 opposition, minor)
11. TC-DEC-001: Planner decision (address submission in decision)
12. TC-DEC-002: Issue decision

**Success Criteria:**
- ✓ Notification correctly determined
- ✓ Affected parties served
- ✓ Submissions managed
- ✓ Written approvals recorded
- ✓ Hearing avoided (minor opposition)

---

### Scenario Pack E: Publicly Notified + Hearing
**Duration**: 70 working days
**Complexity**: High

**Test Flow:**
1. TC-S88-005: Complete application
2. TC-ALLOC-001-005: Processing
3. TC-S95-001: Notification test → Fully notified
4. TC-S95-003: Manager approves public notification
5. TC-PN-001: Publish public notice (20-day submission period)
6. TC-PN-002: 15 public submissions received
7. TC-PN-003: Generate summary of submissions
8. TC-HEAR-001: Determine hearing required (8 wish to be heard)
9. TC-HEAR-002: Appoint independent commissioner
10. TC-HEAR-003: Schedule hearing
11. TC-HEAR-004: Prepare s42A report
12. TC-HEAR-005: Applicant provides evidence
13. TC-HEAR-006: Conduct hearing (2 hours)
14. TC-HEAR-007: Commissioner deliberates
15. TC-DEC-001: Commissioner drafts decision
16. TC-DEC-002: Issue decision

**Success Criteria:**
- ✓ Public notification process complete
- ✓ All submissions captured
- ✓ Hearing properly managed
- ✓ s42A report prepared
- ✓ Commissioner decision issued
- ✓ Decision served on all submitters

---

### Scenario Pack F: Subdivision with s223 + s224
**Duration**: 40 working days (initial) + 90 days (s224 process)
**Complexity**: High

**Test Flow:**
1. TC-S88-005: Subdivision consent lodged
2. TC-ALLOC-002: Assign specialists (engineering, parks, 3-waters)
3. Processing (as Scenario Pack A)
4. TC-DEC-002: Decision issued (Grant with conditions)
5. **Post-decision:**
6. TC-SUB-001: Applicant submits survey plan
7. Planner reviews and approves s223
8. TC-SUB-003: Process legal documents (easements, covenants)
9. TC-SUB-002: Applicant requests s224
10. Planner inspects: Landscaping incomplete
11. Applicant completes landscaping
12. Planner re-inspects and approves
13. Issue s224(c) certificate
14. TC-SUB-SPEC-001: LINZ integration (titles created)
15. TC-CLOSE-001: Close consent

**Success Criteria:**
- ✓ s223 approval workflow complete
- ✓ s224 compliance checking robust
- ✓ Legal documents processed
- ✓ Titles created
- ✓ Subdivision finalised

---

### Scenario Pack G: Objection & Appeal
**Duration**: 25 working days + 180 days (appeal)
**Complexity**: High

**Test Flow:**
1. TC-DEC-002: Decision issued (Grant with conditions)
2. TC-OBJ-001: Applicant lodges objection (condition too restrictive)
3. TC-OBJ-002: Team Leader reviews and partially upholds
4. Amended decision issued
5. TC-APP-001: Submitter appeals to Environment Court
6. Legal team assigned
7. Court hearing scheduled (outside system)
8. Court decision received: Appeal dismissed
9. Update consent record with court decision
10. TC-CLOSE-001: Close consent

**Success Criteria:**
- ✓ Objection processed within timeframe
- ✓ Appeal tracked correctly
- ✓ Legal integration smooth
- ✓ Final court decision recorded

---

## Test Data Requirements

### Users Required
- **Customers/Applicants**: 5-10 test accounts
- **Planners**: 3-5 accounts (varying experience levels)
- **Team Leaders/Managers**: 2 accounts
- **Specialists**: Traffic, 3-Waters, Parks, Heritage, Ecology
- **Commissioners**: 2 accounts (for hearings)
- **Monitoring Officers**: 2 accounts

### Configuration Required
- **Request Types**: Land Use, Subdivision, Discharge, Water, Coastal, Pre-app
- **Processing SLAs**: 20 working days (default), 40 (subdivision)
- **Holiday List**: NZ public holidays configured
- **Condition Templates**: Library of 50+ standard conditions
- **Email Templates**: Acknowledgment, RFI, Decisions, Notifications

### Test Properties
- 10-20 realistic test properties with:
  - Addresses
  - Legal descriptions
  - GIS links
  - Owner details

---

## Automation Opportunities

### High-Value Automation Tests
1. **Clock Calculation**: Verify working days math (excludes weekends/holidays)
2. **Status Transitions**: Ensure status updates correctly at each stage
3. **Notification Triggers**: Email/task creation on key events
4. **Validation Rules**: Required fields, file uploads, date logic
5. **Permission Checks**: Customer vs Planner vs Manager access
6. **Reporting Accuracy**: Consent statistics and KPIs

### Manual Test Focus
- User experience (portal usability)
- Document generation quality
- Complex decision-making workflows
- Hearing management
- Legal document review

---

## Performance Testing

### Load Scenarios
- 100 concurrent users browsing applications
- 50 planners processing applications simultaneously
- Bulk notification to 500+ affected persons
- Report generation with 1000+ consents

### Volume Testing
- System with 10,000+ historical consents
- 500 active applications in processing
- 50 hearings scheduled
- 200 submissions on single application

---

## Acceptance Criteria

### MVP Requirements
- ✅ Complete end-to-end workflow for non-notified land use consent
- ✅ Statutory clock starts, stops, restarts correctly
- ✅ s88 and s92 workflows functional
- ✅ Notification determination workflow
- ✅ Decision issuance
- ✅ Customer portal access
- ✅ Basic reporting

### Full System Requirements
- ✅ All consent types supported
- ✅ Public notification workflow
- ✅ Hearing management
- ✅ Subdivision s223/s224 processes
- ✅ Monitoring handover
- ✅ Objection & appeal tracking
- ✅ Complete audit trail
- ✅ MfE reporting

---

## Appendix: RMA Quick Reference

| Section | Description | System Impact |
|---------|-------------|---------------|
| s88 | Duty to check application complete | Clock cannot start until accepted |
| s92 | Request further information | Clock stops, exclusion period |
| s95-95E | Notification requirements | Determines processing pathway |
| s104 | Matters to consider | Decision framework |
| s108 | Conditions of resource consent | Condition management |
| s223 | Approval of survey plan (subdivision) | Post-decision workflow |
| s224 | Certification of compliance (subdivision) | Completion certificate |
| s357 | Objections to decision | Objection workflow |

---

**Document Version**: 1.0
**Last Updated**: 2025-11-25
**Author**: Claude Code
**Review Cycle**: Quarterly

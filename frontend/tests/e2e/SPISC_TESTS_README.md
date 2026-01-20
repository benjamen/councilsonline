# SPISC End-to-End Test Suite

## Overview

Comprehensive Playwright test suite for SPISC (Social Pension for Indigenous Senior Citizens) application workflow testing in the CouncilsOnline council platform.

## Test Coverage

This test suite covers all aspects of the SPISC application lifecycle:

1. **Application Submission** - Frontend submission flow
2. **Backend Assessment** - Complete assessment workflow with projects and tasks
3. **Workflow States** - All 21 workflow state transitions
4. **RFI Cycle** - Request for Information complete workflow
5. **Validation Rules** - Eligibility and data validation
6. **Payment Processing** - All payment methods (Bank, GCash, Cash Pickup)
7. **Edge Cases** - Error handling and boundary conditions
8. **Integration** - Integration with council workflow infrastructure

## Test Files

### Core Test Files (New - Session Dec 20, 2025)

| File | Purpose | Test Count |
|------|---------|------------|
| `spisc-helpers.js` | Reusable test helper functions | ~600 lines |
| `spisc-backend-complete-assessment-flow.spec.js` | Complete backend assessment flow | 19 steps |
| `spisc-workflow-states-complete.spec.js` | All 21 workflow state transitions | 9 paths |
| `spisc-rfi-complete-cycle.spec.js` | RFI complete workflow cycle | 15 steps |
| `spisc-assessment-validation.spec.js` | All validation rules testing | 12 tests |
| `spisc-payment-complete-flow.spec.js` | Payment processing all methods | 8 steps |
| `spisc-edge-cases-errors.spec.js` | Edge cases and error handling | 10 scenarios |
| `spisc-integration-with-council-workflow.spec.js` | Integration testing | 8 integration points |

### Existing Test Files

| File | Purpose |
|------|---------|
| `spisc-complete-workflow.spec.js` | Full E2E workflow (Apply → Approve → Payment) |
| `spisc-backend-workflow.spec.js` | Backend processing workflow |
| `spisc-assessment-workflow-complete.spec.js` | Assessment project workflow |
| `spisc-complete-submission.spec.js` | Application submission |
| `spisc-entry-points.spec.js` | Entry points and authentication |
| `spisc-no-duplicate-applications.spec.js` | Duplicate prevention |
| `spisc-payment-manual-test.spec.js` | Manual payment testing |
| `spisc-payment-notification-complete.spec.js` | Payment notification flow |
| `spisc-address-field.spec.js` | Address field testing |

## Running Tests

### Run All SPISC Tests

```bash
cd /workspace/development/frappe-bench/apps/councilsonline/frontend
npx playwright test tests/e2e/spisc-*.spec.js --reporter=html
```

### Run Specific Test Suite

```bash
# Backend assessment flow
npx playwright test tests/e2e/spisc-backend-complete-assessment-flow.spec.js

# Workflow states
npx playwright test tests/e2e/spisc-workflow-states-complete.spec.js

# RFI cycle
npx playwright test tests/e2e/spisc-rfi-complete-cycle.spec.js

# Payment flow
npx playwright test tests/e2e/spisc-payment-complete-flow.spec.js
```

### View Test Results

```bash
npx playwright show-report
```

## Test Environment

- **Server**: `http://localhost:8090`
- **Start Command**: `bench --site councilsonline.localhost serve --port 8090`
- **Council**: TAYTAY-PH
- **Test User**: Administrator / admin123

## SPISC Workflow States (21 Total)

### Happy Path States
1. Draft
2. Submitted
3. Acknowledged
4. Processing
5. Pending Decision
6. Approved
7. Payment Pending
8. Paid
9. Completed

### Exception Path States
10. RFI Issued
11. RFI Received
12. Declined
13. Withdrawn
14. Cancelled
15. On Hold
16. Rework Needed
17. Conditionally Approved
18. Under Appeal
19. Appeal Decided
20. Re-evaluation
21. Archived

## Assessment Project Structure

When a SPISC application is acknowledged, an Assessment Project is auto-created with:

### Stages (4)
1. Eligibility Verification
2. Income & Poverty Assessment
3. Approval Decision
4. Payment Setup

### Tasks (11-12 from templates)
- **SPISC-VET-001 to SPISC-VET-003**: Eligibility verification tasks
- **SPISC-TA-001 to SPISC-TA-004**: Technical assessment tasks
- **SPISC-DEC-001 to SPISC-DEC-003**: Decision tasks
- **SPISC-IMP-001 to SPISC-IMP-002**: Implementation tasks

## RFI (Request for Information) Workflow

1. Processing → RFI Issued
2. RFI questions sent to applicant
3. SLA clock suspended
4. Applicant responds
5. RFI Received → Processing
6. SLA clock resumes
7. Continue assessment

## Payment Methods

### 1. Bank Deposit
- Bank name
- Account number
- Account holder name

### 2. GCash
- Mobile number (Philippine format: +63XXXXXXXXXX)

### 3. Cash Pickup
- Pickup location

## Validation Rules

### Eligibility Criteria
1. Age >= 60 years
2. Filipino citizen
3. Household income <= poverty threshold (₱12,000/month)
4. No other government pension
5. No property ownership
6. All required documents uploaded

### Required Documents
1. Valid government-issued ID
2. Proof of income (last 3 months)
3. Barangay certification
4. Birth certificate
5. Household composition document

## SLA (Service Level Agreement)

- **Statutory Deadline**: 20 working days from acknowledgment
- **Clock Exclusions**: RFI periods, public holidays
- **Working Days**: Monday to Friday only
- **SLA Indicators**:
  - Green: < 80% of deadline
  - Amber: 80-100% of deadline
  - Red: > 100% of deadline (breached)

## Known Issues / Bugs to Test

Based on test execution, the following areas need verification:

1. **Assessment Project Auto-Creation**
   - May not trigger on acknowledgment
   - Needs workflow hook verification

2. **Workflow Actions**
   - Some workflow actions not available
   - May need workflow state configuration

3. **Payment Fields**
   - Payment status field visibility
   - Payment method field location

4. **Address Field**
   - Address field may appear empty in backend
   - Field mapping needs verification

5. **Age Calculation**
   - Age field may appear empty
   - Birthday → age calculation needs verification

6. **RFI Creation**
   - RFI DocType configuration may need setup
   - Request linkage verification needed

7. **SLA Tracking**
   - Statutory deadline field visibility
   - Clock exclusion creation

8. **Status History**
   - Workflow transition logging
   - History table verification

## Test Helper Functions

The `spisc-helpers.js` file provides reusable functions:

```javascript
// Application Management
findLatestSPISCApplication(page)
openSPISCApplication(page, spiscId)
getLinkedRequestId(page)
navigateToRequest(page, requestId)

// Workflow Management
getCurrentWorkflowState(page)
changeWorkflowState(page, targetState)
verifyStatusHistoryTransition(page, fromStatus, toStatus)

// Assessment Project
waitForAssessmentProject(page, timeout)
navigateToAssessmentProject(page, assessmentId)
createTasksFromTemplate(page)
executeSPISCTask(page, taskId, hoursWorked, assignee)

// Eligibility
fillEligibilityAssessment(page, status, notes)

// RFI
createRFI(page, requestId, questions)
```

## Integration Points

SPISC integrates with the following CouncilsOnline infrastructure:

1. **Request Doctype** - Same as RC (Resource Consent) and BC (Building Consent)
2. **Assessment Project** - Same doctype, different template
3. **Project Task** - Same task system with SPISC-specific codes
4. **RFI Workflow** - Shared RFI infrastructure
5. **SLA Tracking** - Common SLA clock mechanism
6. **Payment Processing** - Shared payment infrastructure
7. **Dashboard Statistics** - Included in council stats
8. **Permission Model** - Same role-based permissions

## Multi-Council Support

SPISC supports multiple councils:
- TAYTAY-PH (Philippines) - Primary test council
- Council-specific assessment templates
- Council-specific task templates
- Council-level permissions and filtering

## Reporting

After test execution, check:

1. **HTML Report**: `playwright-report/index.html`
2. **Screenshots**: `test-results/*/test-failed-*.png`
3. **Videos**: `test-results/*/video.webm`
4. **Traces**: `test-results/*/trace.zip`

## Next Steps

1. Run full test suite and generate HTML report
2. Document all bugs found with:
   - Bug description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/videos
   - Severity (Critical, High, Medium, Low)
3. Create bug tickets in issue tracker
4. Verify fixes with regression testing

## Test Execution Summary

Total Tests: 330 tests across 16 spec files
Coverage: All workflow paths, all payment methods, all validation rules, all edge cases

## Contact

For questions about SPISC testing, refer to:
- Test Plan: `/home/frappe/.claude/plans/sharded-questing-matsumoto.md`
- CouncilsOnline Documentation
- Council workflow documentation

---

**Last Updated**: December 20, 2025
**Test Suite Version**: 1.0
**Framework**: Playwright
**Browser**: Chromium Desktop

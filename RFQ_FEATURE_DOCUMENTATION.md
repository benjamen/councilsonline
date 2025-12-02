# RFQ Agent Details Feature Documentation

## Overview

The RFQ (Request for Quote) Agent Details feature allows applicants to request quotes from and engage resource consent planning professionals or agents to help prepare and lodge their applications. Once an agent is engaged, the application becomes locked from further edits by the applicant.

## Feature Components

### 1. Backend Components

#### DocType: RFQ Agent Details
**Location**: `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/lodgeick/doctype/rfq_agent_details/`

**Key Fields**:
- `request`: Link to Request document
- `status`: Draft | Sent to Agent | Quote Received | Agent Engaged | Cancelled
- `rfq_message`: Rich text message sent to agents (editable)
- `agent`: Link to User (agent user ID)
- `agent_name`, `agent_email`, `agent_phone`: Agent contact details
- `agent_engaged`: Boolean flag
- `agent_engaged_date`: Date when agent was engaged
- `quote_amount`: Quote provided by agent
- `quote_details`: Additional quote information
- `created_date`, `sent_date`, `quote_received_date`: Tracking dates

**Default RFQ Message**:
```
You may contact Resource Consent Planning Professionals or Agents from the list available
in eRCS to obtain quotes from and engage them to help you prepare and lodge your application
by selecting the Engage Agent button.

Please note: You will not be able to make any more changes or complete this application
once you engage an Agent.
```

#### Python Controller
**File**: `rfq_agent_details.py`

**Key Methods**:
- `before_save()`: Updates timestamps and locks request when agent is engaged
- `_lock_request()`: Sets `locked_for_editing=1` on the Request document

**API Endpoints** (all decorated with `@frappe.whitelist()`):
1. `create_rfq_for_request(request_id, rfq_message=None)`
   - Creates new RFQ document for a request
   - Validates that request exists and no active RFQ already exists
   - Returns: `{success: True, rfq_id: str, rfq_message: str}`

2. `send_rfq_to_agent(rfq_id, agent_id)`
   - Sends RFQ to specified agent
   - Updates status to "Sent to Agent"
   - Sets sent_date timestamp
   - Returns: `{success: True, rfq_id: str}`

3. `engage_agent(rfq_id, quote_amount=None, quote_details=None)`
   - Engages the agent (locks the request)
   - Updates status to "Agent Engaged"
   - Sets agent_engaged flag and date
   - Calls `_lock_request()` to lock the application
   - Returns: `{success: True, rfq_id: str}`

4. `get_available_agents()`
   - Returns list of available agents
   - Currently returns placeholder data
   - Returns: `[{value: str, label: str}, ...]`

### 2. Frontend Components

#### RFQ Modal Component
**Location**: `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/components/modals/RFQModal.vue`

**Features**:
- Display RFQ details with status badge
- Editable RFQ message (when status is Draft or Sent to Agent)
- Agent selection dropdown
- Quote details display (when quote received)
- Engaged agent information display
- Warning messages about application lock
- Action buttons based on RFQ status:
  - Draft: Save Changes, Send to Agent
  - Quote Received: Engage Agent
  - Agent Engaged: Close only (read-only view)

**Props**:
- `isOpen`: Boolean - Controls modal visibility
- `rfq`: Object - RFQ data to display/edit
- `requestId`: String - Associated request ID

**Events**:
- `@close`: Close modal
- `@save`: Save RFQ changes
- `@send-to-agent`: Send RFQ to selected agent
- `@engage-agent`: Engage agent and lock application

#### Step 1 Integration
**Location**: `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/components/request-steps/Step1ApplicantProposal.vue`

**Agent Details Section** (Lines 269-342):
- Radio button group:
  - "No Agent Required" (default, enabled)
  - "Engage Agent (Coming Soon)" (disabled, visible)
- RFQ list display showing all RFQs for current request
- Each RFQ shows:
  - RFQ ID
  - Status badge (color-coded)
  - Agent name (if assigned)
  - "View Details" button to open modal

**State Management**:
- `agentRequired`: ref(false) - Selected option
- `isRFQModalOpen`: ref(false) - Modal visibility
- `currentRFQ`: ref({}) - Currently viewed RFQ
- `currentRFQIndex`: ref(null) - Index in agent_rfqs array
- `localData.agent_rfqs`: Array of RFQ objects

**Functions**:
- `viewRFQ(index)`: Opens modal with selected RFQ
- `closeRFQModal()`: Closes modal and resets state
- `saveRFQ(rfqData)`: Saves RFQ changes via API
- `sendRFQToAgent({rfq, agent})`: Sends RFQ to agent via API
- `engageAgentFromRFQ(rfqData)`: Engages agent and locks application via API

#### API Utilities
**Location**: `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/api/rfq.js`

**Exported Functions**:
- `createRFQ(requestId, rfqMessage)`: Create new RFQ
- `sendRFQToAgent(rfqId, agentId)`: Send RFQ to agent
- `engageAgent(rfqId, quoteAmount, quoteDetails)`: Engage agent
- `getAvailableAgents()`: Get list of available agents
- `updateRFQ(rfqId, data)`: Update RFQ fields
- `getRFQ(rfqId)`: Get RFQ by ID
- `getRFQsForRequest(requestId)`: Get all RFQs for a request

All functions use Frappe's `createResource` or `frappe.call` for API communication.

## User Flow

### Current Implementation (Engage Agent Disabled)

1. **Applicant fills application** in Step 1 (Applicant and Proposal Details)
2. **Agent Details section** shows:
   - Radio button: "No Agent Required" (selected by default)
   - Radio button: "Engage Agent (Coming Soon)" (disabled, grayed out)
3. **If RFQs exist** for this request:
   - List of RFQs displayed with status badges
   - "View Details" button opens modal to view RFQ
4. **Modal view** (read-only currently):
   - Shows RFQ message
   - Shows status
   - Shows agent details if assigned
   - Shows quote details if available

### Future Implementation (When Feature Enabled)

1. **Applicant selects "Engage Agent"**
2. **System creates RFQ** via `create_rfq_for_request()` API
3. **Modal opens** with:
   - Default RFQ message (editable)
   - Agent selection dropdown
4. **Applicant selects agent** and clicks "Send to Agent"
5. **System sends RFQ** via `send_rfq_to_agent()` API
   - Status changes to "Sent to Agent"
   - Notification sent to agent (to be implemented)
6. **Agent receives RFQ** and provides quote
   - Agent updates quote_amount and quote_details
   - Status changes to "Quote Received"
7. **Applicant reviews quote** and clicks "Engage Agent"
8. **System engages agent** via `engage_agent()` API:
   - Status changes to "Agent Engaged"
   - Request is locked (`locked_for_editing=1`)
   - Application becomes read-only for applicant
9. **Agent completes application** and lodges on behalf of applicant

## Application Lock Mechanism

### Backend Lock
**File**: `rfq_agent_details.py`, method `_lock_request()`

```python
def _lock_request(self):
    if self.request:
        request_doc = frappe.get_doc("Request", self.request)
        request_doc.agent_engaged = 1
        request_doc.agent_id = self.agent
        request_doc.locked_for_editing = 1
        request_doc.locked_reason = f"Agent engaged on {self.agent_engaged_date}"
        request_doc.save(ignore_permissions=True)
        frappe.db.commit()
```

### Frontend Lock
**File**: `Step1ApplicantProposal.vue`, method `engageAgentFromRFQ()`

Updates `localData`:
- `locked_for_editing = true`
- `locked_reason = 'Agent engaged'`
- `agent_engaged = true`

## Database Schema

### RFQ Agent Details Table
Created by running `bench migrate` after DocType creation.

**Key Indexes**:
- `request` (for filtering RFQs by request)
- `agent` (for filtering RFQs by agent)
- `status` (for status-based queries)

## Testing

### Manual Testing Steps

1. **Create a test request**:
   ```bash
   bench --site lodgeick.localhost console
   ```
   ```python
   request = frappe.get_doc({
       "doctype": "Request",
       "title": "Test Request for RFQ",
       "status": "Draft"
   })
   request.insert()
   frappe.db.commit()
   print(f"Request created: {request.name}")
   ```

2. **Create an RFQ**:
   ```python
   rfq = frappe.get_doc({
       "doctype": "RFQ Agent Details",
       "request": request.name,
       "status": "Draft"
   })
   rfq.insert()
   frappe.db.commit()
   print(f"RFQ created: {rfq.name}")
   ```

3. **Test send to agent**:
   ```python
   from lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details import send_rfq_to_agent
   result = send_rfq_to_agent(rfq.name, "test-agent@example.com")
   print(result)
   ```

4. **Test engage agent**:
   ```python
   from lodgeick.lodgeick.doctype.rfq_agent_details.rfq_agent_details import engage_agent
   result = engage_agent(rfq.name, 1500.00, "Standard resource consent preparation")
   print(result)

   # Verify request is locked
   locked_request = frappe.get_doc("Request", request.name)
   print(f"Locked: {locked_request.locked_for_editing}")
   print(f"Reason: {locked_request.locked_reason}")
   ```

### Automated Testing (To Be Implemented)

**File**: `test_rfq_agent_details.py` (to be created)

Test cases needed:
- ✓ Create RFQ for request
- ✓ Prevent duplicate RFQs for same request
- ✓ Send RFQ to agent
- ✓ Engage agent locks request
- ✓ Cannot edit request after agent engaged
- ✓ Status transitions are valid
- ✓ Timestamps are updated correctly
- ✓ Agent details are populated correctly

## Configuration

### Enabling the Feature

To enable the "Engage Agent" functionality:

1. **Remove disabled attribute** in `Step1ApplicantProposal.vue` (line ~288):
   ```vue
   <input
     type="radio"
     :value="true"
     v-model="agentRequired"
     class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
     <!-- Remove this line: disabled -->
   />
   ```

2. **Add RFQ creation on selection**:
   ```javascript
   watch(agentRequired, async (newVal) => {
     if (newVal === true && localData.value.name) {
       // Create RFQ when user selects "Engage Agent"
       try {
         const result = await createRFQ(localData.value.name)
         // Add to localData
         if (!localData.value.agent_rfqs) {
           localData.value.agent_rfqs = []
         }
         localData.value.agent_rfqs.push(result)
       } catch (error) {
         console.error('Failed to create RFQ:', error)
       }
     }
   })
   ```

3. **Implement agent notification system** (backend):
   - Email template for RFQ notification
   - Email template for quote submission
   - Email template for agent engagement confirmation

4. **Implement agent portal** (optional):
   - View received RFQs
   - Submit quotes
   - Access locked applications
   - Update application on behalf of applicant

## Security Considerations

1. **API Whitelisting**: All RFQ API methods use `@frappe.whitelist()` decorator
2. **Permission Checks**: RFQ operations should respect Frappe's permission system
3. **Request Locking**: Uses `locked_for_editing` flag to prevent modifications
4. **Audit Trail**: All status changes and timestamps are tracked
5. **Agent Verification**: Future implementation should verify agent credentials

## Future Enhancements

1. **Agent Management**:
   - Agent registration and verification
   - Agent profile with qualifications and experience
   - Agent rating and review system
   - Agent availability management

2. **RFQ Management**:
   - Multiple quotes from different agents
   - Quote comparison interface
   - Negotiation/messaging between applicant and agents
   - RFQ expiry and cancellation

3. **Notifications**:
   - Email notifications for all RFQ events
   - SMS notifications (optional)
   - In-app notifications
   - Agent notification preferences

4. **Reporting**:
   - RFQ statistics dashboard
   - Agent performance metrics
   - Quote analysis and trends
   - Application completion rates with/without agents

5. **Integration**:
   - Payment gateway for agent fees
   - Document sharing between applicant and agent
   - Collaborative editing for certain sections
   - Council approval workflow integration

## Files Modified/Created

### Backend Files
- ✓ Created: `lodgeick/lodgeick/doctype/rfq_agent_details/rfq_agent_details.json`
- ✓ Created: `lodgeick/lodgeick/doctype/rfq_agent_details/rfq_agent_details.py`
- ✓ Created: `lodgeick/lodgeick/doctype/rfq_agent_details/__init__.py`

### Frontend Files
- ✓ Created: `frontend/src/components/modals/RFQModal.vue`
- ✓ Created: `frontend/src/api/rfq.js`
- ✓ Modified: `frontend/src/components/request-steps/Step1ApplicantProposal.vue`
  - Added RFQ modal import and component
  - Added Agent Details section UI (lines 269-342)
  - Added RFQ management functions (lines 1016-1111)
  - Added agent_rfqs to localData (line 870)

### Documentation
- ✓ Created: `RFQ_FEATURE_DOCUMENTATION.md` (this file)

## Build and Deployment

### Build Frontend
```bash
cd /workspace/development/frappe-bench/apps/lodgeick/frontend
yarn build
```

### Run Migrations
```bash
cd /workspace/development/frappe-bench
bench --site lodgeick.localhost migrate
```

### Clear Cache
```bash
bench --site lodgeick.localhost clear-cache
```

### Restart Server
```bash
bench restart
```

## Support and Maintenance

### Logging
All RFQ operations are logged using Frappe's error log system:
```python
frappe.log_error(
    title="RFQ - Error description",
    message=f"Details: {error_info}"
)
```

### Debugging
Enable developer mode in Frappe to see detailed error messages:
```bash
bench --site lodgeick.localhost set-config developer_mode 1
bench restart
```

### Common Issues

1. **RFQ not appearing in list**:
   - Check that `agent_rfqs` field exists in Request data model
   - Verify RFQ was saved to database: `select * from tabRFQ Agent Details`
   - Check browser console for API errors

2. **Application not locking**:
   - Verify `locked_for_editing` field exists in Request DocType
   - Check that `engage_agent()` API completed successfully
   - Verify database update: `select locked_for_editing from tabRequest where name = 'REQ-XXX'`

3. **Agent dropdown empty**:
   - Check `get_available_agents()` API response
   - Verify agent users exist in system
   - Check browser console for API errors

## Version History

- **v1.0** (Current): Initial RFQ feature implementation
  - Backend DocType and API endpoints
  - Frontend modal and UI integration
  - Application lock mechanism
  - "Engage Agent" option visible but disabled
  - Ready for full activation when agent system is implemented

# Property Autocomplete - Implementation Complete ✅

## Overview
The property autocomplete feature has been fully implemented, integrating LINZ (Land Information New Zealand) property data with the Lodgeick application. Users can now search for properties using address autocomplete, and all property details including legal description, title information, zoning, and hazard overlays are automatically populated.

## Architecture

### 1. Property API Server (Node.js/Express)
**Location:** `/workspace/development/frappe-bench/apps/lodgeick/property-api/`

**Features:**
- Address autocomplete using LINZ NZ Addresses database
- Property boundary lookup
- Title information retrieval
- District plan zoning data
- Hazard overlays (Flood, Coastal, Slope)
- Coordinate projection (WGS84 → NZTM2000)
- In-memory caching (60s TTL)
- Rate limiting (120 requests/minute)

**API Endpoints:**
- `GET /api/search?q=<address>` - Search for properties
- `GET /health` - Health check

**Starting the server:**
```bash
cd /workspace/development/frappe-bench/apps/lodgeick/property-api
npm start
# or
./start.sh
```

**Server runs on:** `http://localhost:3000`

### 2. Frappe Backend Integration
**Location:** `/workspace/development/frappe-bench/apps/lodgeick/lodgeick/api.py`

**Method:** `search_property_address(query)`
- Whitelisted API method accessible from frontend
- Proxies requests to Property API server
- Handles errors gracefully with logging
- Configurable URL via `site_config.json` (`property_api_url`)

**Usage from frontend:**
```javascript
const response = await fetch('/api/method/lodgeick.api.search_property_address', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Frappe-CSRF-Token': window.csrf_token
  },
  body: JSON.stringify({ query: 'property address' })
})
```

### 3. Frontend Implementation
**Location:** `/workspace/development/frappe-bench/apps/lodgeick/frontend/src/pages/NewRequest.vue`

**Features:**
- Autocomplete input field with dropdown
- Debounced search (300ms)
- Loading indicator while searching
- Displays:
  - Property address (selectable)
  - Legal description (read-only display)
  - Title number (read-only display)
- Auto-fills all property fields on selection:
  - Property address
  - Legal description
  - Title number (CT reference)
  - Valuation reference
  - Parcel ID
  - Property coordinates (NZTM2000)
  - Zoning information
  - Hazard data

**State Variables:**
```javascript
const propertySearchQuery = ref('')        // User's search input
const propertySearchResults = ref([])      // Search results array
const propertySearchLoading = ref(false)   // Loading state
const showPropertyDropdown = ref(false)    // Dropdown visibility
```

**Handler Functions:**
- `handlePropertySearch()` - Debounced search handler
- `selectProperty(result)` - Property selection handler
- `closePropertyDropdown()` - Close dropdown

**Form Data Fields Updated:**
```javascript
formData.value = {
  // ... existing fields
  property_address: '',      // Full address
  legal_description: '',     // e.g., "Lot 1 DP 12345"
  ct_reference: '',          // Title number e.g., "WN123/456"
  valuation_reference: '',   // Valuation ref if available
  parcel_id: '',            // LINZ parcel ID
  property_coordinates: '',  // NZTM2000 coordinates
  hazard_data: null,        // Full hazard overlay data
  zone: '',                 // Zoning code/name from district plan
}
```

## Data Flow

1. **User Types Address** → Frontend debounces input (300ms)
2. **Frontend → Frappe Backend** → `search_property_address(query)`
3. **Frappe → Property API** → `GET /api/search?q=<query>`
4. **Property API** →
   - Queries LINZ Address database
   - For each address result:
     - Projects coordinates to NZTM2000
     - Queries property boundaries
     - Retrieves title information
     - Queries district plan for zoning
     - Queries hazard overlays (flood, coastal, slope)
5. **Results** → Return to frontend with full property data
6. **User Selects Property** → All fields auto-populated

## Response Structure

```json
{
  "query": "123 Main Street",
  "count": 5,
  "results": [
    {
      "address": "123 Main Street, Wellington",
      "address_id": "12345",
      "coords": {
        "gd2000_x": 174.879,
        "gd2000_y": -41.209
      },
      "projected_x": 1748790.5,
      "projected_y": 5427123.2,
      "property": {
        "legal_description": "LOT 1 DP 12345",
        "title_no": "WN123/456",
        "parcel_id": "9876543",
        "area": 800.5,
        "source": "LINZ",
        "issue_date": 1234567890000,
        "status": "LIVE",
        "type": "Freehold",
        "estate_description": "Fee Simple, Lot 1 DP 12345",
        "number_owners": 2,
        "valuation_reference": "123456"
      },
      "hazards": {
        "districtPlan": [
          {
            "attributes": {
              "Zone_Code": "RES-1",
              "Zone_Name": "Residential Zone 1"
            }
          }
        ],
        "floodHazard": [...],
        "coastalHazard": [...],
        "slopeHazard": null
      }
    }
  ]
}
```

## Testing

### 1. Start the Property API Server
```bash
cd /workspace/development/frappe-bench/apps/lodgeick/property-api
npm start
```

### 2. Test the API directly
```bash
# Health check
curl http://localhost:3000/health

# Search for properties
curl "http://localhost:3000/api/search?q=123%20Main"
```

### 3. Test in the frontend
1. Navigate to `/frontend/request/new`
2. Fill out steps 1-2 (Council, Type)
3. On Step 3 (Property):
   - Start typing an address in the "Property Address" field
   - Wait for autocomplete dropdown to appear
   - Select a property from the list
   - Verify all fields are auto-populated

## Configuration

### Optional: Custom Property API URL
Edit `/workspace/development/frappe-bench/sites/lodgeick.localhost/site_config.json`:

```json
{
  "property_api_url": "http://localhost:3000"
}
```

## UI/UX Features

- ✅ Autocomplete dropdown shows address + legal description
- ✅ Loading spinner while searching
- ✅ Minimum 3 characters required to search
- ✅ 300ms debounce to reduce API calls
- ✅ Click outside to close dropdown
- ✅ Auto-fill all property fields on selection
- ✅ Zoning automatically extracted from district plan data
- ✅ Coordinates in NZTM2000 format stored
- ✅ Full hazard overlay data stored for future reference

## Future Enhancements

1. **Display hazard warnings** - Show flood/coastal hazard warnings if property is affected
2. **Map integration** - Display property boundary on a map
3. **Property history** - Show previous consents for the property
4. **Favorite properties** - Allow users to save frequently used properties
5. **Offline support** - Cache recent searches for offline access

## Troubleshooting

### Property API not starting
- Check Node.js is installed: `node --version`
- Check port 3000 is not in use: `lsof -i :3000`
- Check logs: `tail -f /tmp/property-api.log`

### No search results
- Verify Property API is running: `curl http://localhost:3000/health`
- Check LINZ API connectivity (requires internet)
- Check browser console for errors

### Auto-fill not working
- Check browser console for JavaScript errors
- Verify Frappe API method is accessible
- Check that Property API is responding correctly

## Dependencies

### Property API
- express: ^4.18.2
- cors: ^2.8.5
- express-rate-limit: ^7.1.5

### External APIs (LINZ)
- Address Search: LINZ NZ Addresses Pilot
- Property Boundaries: LINZ NZ Property Boundaries
- Title Information: LINZ NZ Property Titles
- District Plan: Lower Hutt District Plan (ArcGIS)
- Hazard Overlays: Flood, Coastal, Slope (ArcGIS)

## Build Status

✅ Property API server created and running
✅ Backend proxy API method implemented
✅ Frontend autocomplete UI implemented
✅ All form fields auto-populate on selection
✅ Zoning and hazard data extracted
✅ Build successful with no errors
✅ Integration tested and working

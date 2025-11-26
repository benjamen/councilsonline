# Lodgeick Property API

Property search and autocomplete API using LINZ (Land Information New Zealand) data via ArcGIS services.

## Features

- Address autocomplete search
- Automatic property boundary lookup
- Legal description and title information
- Zoning information (District Plan)
- Hazard overlays (Flood, Coastal, Slope)
- Coordinate projection (WGS84 to NZTM2000)

## Installation

```bash
cd /workspace/development/frappe-bench/apps/lodgeick/property-api
npm install
```

## Running

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

The server will start on `http://localhost:3000` by default.

## API Endpoints

### `GET /api/search?q=<address>`

Search for addresses and retrieve property information.

**Parameters:**
- `q` - Address search query (e.g., "123 Main Street")

**Response:**
```json
{
  "query": "123 Main Street",
  "count": 5,
  "results": [
    {
      "address": "123 Main Street, Lower Hutt",
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
        "source": "LINZ"
      },
      "hazards": {
        "districtPlan": [...],
        "floodHazard": [...],
        "coastalHazard": [...],
        "slopeHazard": null
      }
    }
  ]
}
```

### `GET /health`

Health check endpoint.

## Integration with Frappe

The Frappe backend should proxy requests to this service or run it as a separate microservice accessible from the frontend.

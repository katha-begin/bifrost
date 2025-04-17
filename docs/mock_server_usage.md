# Mock API Server

This is a simple mock server that simulates API responses for the Bifrost platform. It's designed to help with frontend development and testing without requiring a full backend implementation.

## Features

- **Dynamic Response Loading**: Serves JSON files based on request paths and methods
- **Request Validation**: Validates incoming request payloads against JSON schemas
- **Query Parameter Filtering**: Filter response data using URL query parameters
- **Pagination Support**: Handles pagination with `page` and `per_page` parameters
- **Error Simulation**: Simulate different error responses
- **Response Delay**: Simulate network latency for testing loading states
- **Enhanced Asset Format**: Support for both legacy and new enhanced asset structure
- **Department-specific Endpoints**: Support for managing asset departments and versions

## Directory Structure

```
mocks/
├── api/
│   └── v1/
│       ├── GET_assets.json
│       ├── GET_assets_enhanced.json
│       ├── GET_departments.json
│       ├── assets/
│       │   ├── GET_assets_{id}.json
│       │   ├── GET_assets_{id}_departments.json
│       │   ├── GET_assets_{id}_departments_modeling_versions.json
│       │   ├── GET_assets_{id}_departments_rigging_versions.json
│       │   ├── POST_assets_{id}_departments_rigging_versions.json
│       │   └── PUT_assets_{id}_departments_rigging_status.json
│       ├── departments/
│       │   ├── GET_departments_modeling_dependencies.json
│       │   ├── GET_departments_rigging_dependencies.json
│       │   ├── GET_departments_texturing_dependencies.json
│       │   └── GET_departments_animation_dependencies.json
│       └── common/
│           └── errors.json
└── schemas/
    ├── assets_post_schema.json
    ├── assets_enhanced_post_schema.json
    ├── department_status_put_schema.json
    ├── department_version_post_schema.json
    └── departments_post_schema.json
```

## Naming Convention for Mock Files

The mock files follow a specific naming convention:

- `{METHOD}_{resource}.json` - For top-level resources (e.g., `GET_assets.json`)
- `{METHOD}_{resource}_{action}.json` - For nested resources (e.g., `GET_assets_{id}_versions.json`)
- `{METHOD}_{resource}_enhanced.json` - For enhanced data format (e.g., `GET_assets_enhanced.json`)

## Usage

### Running the Server

```bash
python -m bifrost.api.mock_api
```

### API Requests

#### Basic Asset Requests
- **Basic GET**: `GET /assets` - Returns all assets
- **Filtering**: `GET /assets?type=character` - Returns only character assets
- **Pagination**: `GET /assets?page=1&per_page=10` - Returns paginated results
- **Error Simulation**: `GET /assets?simulate_error=404` - Simulates a 404 error
- **Response Delay**: `GET /assets?delay=2000` - Adds a 2-second delay to the response

#### Enhanced Asset Format
- **Enhanced Assets**: `GET /assets/enhanced` - Returns assets in the enhanced format with pagination wrapper
- **Enhanced with Filtering**: `GET /assets/enhanced?departments.name=modeling` - Filter by department name
- **Enhanced with Query Parameter**: `GET /assets?enhanced=true` - Alternative way to get enhanced format

#### Department-specific Endpoints
- **List Asset Departments**: `GET /assets/{id}/departments` - List all departments for an asset
- **List Department Versions**: `GET /assets/{id}/departments/{department}/versions` - List versions for a specific department
- **Create Version**: `POST /assets/{id}/departments/{department}/versions` - Create a new version for a department
- **Update Status**: `PUT /assets/{id}/departments/{department}/status` - Update department status

#### Department Management API
- **List Departments**: `GET /departments` - List all available departments
- **Create Department**: `POST /departments` - Create a new department
- **Get Dependencies**: `GET /departments/{name}/dependencies` - Get dependency rules for a department

### Adding New Mock Data

1. Create JSON files in the appropriate directory following the naming convention
2. For validating POST/PUT requests, add schema files to the `mocks/schemas` directory

## Examples

### Creating a New Resource Type

1. Add a schema file: `mocks/schemas/shots_post_schema.json`
2. Add mock responses:
   - `mocks/api/v1/GET_shots.json` (list of shots)
   - `mocks/api/v1/shots/GET_shots_{id}.json` (single shot by ID)

### Schema Validation

For POST/PUT requests, the server will validate the request body against the corresponding schema if it exists.

Example schema naming: `{resource}_{method}_schema.json` (e.g., `assets_post_schema.json`)

### Enhanced Asset Format

The enhanced asset format includes:

1. **Departments Array**: Breakdown of the asset by department with status and version tracking
2. **Additional Metadata**: Fields like `created_by`, `thumbnail_url`, and `modified_at`
3. **Consistent ID Format**: Using alphanumeric IDs
4. **Wrapped Response Format**: Returns data in a `{ data: [], pagination: {} }` format

To use the enhanced format:
- `GET /assets/enhanced` - Use path suffix
- `GET /assets?enhanced=true` - Use query parameter

### Department Management

The department API allows for:

1. **Department Assignment**: Manage which departments are assigned to assets
2. **Version Control**: Track versions of department-specific deliverables
3. **Status Tracking**: Monitor the progress of each department's work on an asset
4. **Dependencies**: Enforce prerequisite relationships between departments
from flask import Flask, jsonify, request, Response
import json
import os
import re
from pathlib import Path
import jsonschema
from typing import Tuple, Union, Dict, List, Any
from urllib.parse import urlencode

app = Flask(__name__)

# Directories for mock data and schemas
BASE_DIR = Path(__file__).parent.parent.parent
MOCKS_DIR = BASE_DIR / "mocks" / "api" / "v1"
SCHEMAS_DIR = BASE_DIR / "mocks" / "schemas"
COMMON_DIR = MOCKS_DIR / "common"

# Ensure directories exist
MOCKS_DIR.mkdir(parents=True, exist_ok=True)
SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
COMMON_DIR.mkdir(parents=True, exist_ok=True)

# Default error responses
ERROR_RESPONSES = {
    "not_found": {"error": "Resource not found", "code": 404},
    "validation_error": {"error": "Validation error", "code": 400},
    "server_error": {"error": "Internal server error", "code": 500},
    "unauthorized": {"error": "Unauthorized", "code": 401},
}

# Create default error responses file if it doesn't exist
def initialize_error_files():
    errors_file = COMMON_DIR / "errors.json"
    if not errors_file.exists():
        with open(errors_file, 'w') as f:
            json.dump(ERROR_RESPONSES, f, indent=2)

initialize_error_files()

def load_mock_file(method: str, path: str) -> Tuple[Union[Dict, List], int]:
    """
    Load the appropriate mock file based on the request method and path.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path: Request path
        
    Returns:
        Tuple containing response data and status code
    """
    # Convert path parameters to the mock filename format
    # e.g., /assets/123/versions becomes GET_assets_{id}_versions.json
    pattern = re.sub(r'(\d+)', r'{id}', path)
    parts = pattern.strip('/').split('/')
    
    # Construct mock filename
    if len(parts) == 1:
        filename = f"{method}_{parts[0]}.json"
        directory = MOCKS_DIR
    else:
        resource = parts[0]
        action = '_'.join(parts[1:])
        filename = f"{method}_{resource}_{action}.json"
        directory = MOCKS_DIR / resource
        
        # Create resource directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
    
    file_path = directory / filename
    
    # Check for error simulation query parameter
    error_code = request.args.get('simulate_error')
    if error_code and error_code.isdigit():
        # Load error responses
        with open(COMMON_DIR / "errors.json", 'r') as f:
            errors = json.load(f)
            
        # Find the appropriate error or default to server_error
        error_key = next((k for k, v in errors.items() if v.get('code') == int(error_code)), 'server_error')
        return errors[error_key], int(error_code)
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f), 200
    
    # Fall back to error response
    with open(COMMON_DIR / "errors.json", 'r') as f:
        errors = json.load(f)
        return errors["not_found"], 404

def validate_request_payload(resource: str, method: str) -> Tuple[bool, Dict]:
    """
    Validate request payload against JSON schema.
    
    Args:
        resource: API resource name
        method: HTTP method
        
    Returns:
        Tuple containing validation result and error details
    """
    if request.json:
        schema_file = SCHEMAS_DIR / f"{resource}_{method.lower()}_schema.json"
        
        if schema_file.exists():
            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                
                jsonschema.validate(request.json, schema)
                return True, {}
            except jsonschema.exceptions.ValidationError as e:
                return False, {
                    "error": "Validation error",
                    "details": str(e),
                    "code": 400
                }
    
    # If no schema exists or no JSON payload, consider it valid
    return True, {}

def apply_pagination(data: List[Any], path: str) -> Tuple[Dict, int]:
    """
    Apply pagination to the response data with enhanced format.
    
    Args:
        data: List of items to paginate
        path: The request path for building next/previous links
        
    Returns:
        Tuple containing paginated response object and status code
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Calculate start and end indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get paginated subset of data
    paginated_data = data[start_idx:end_idx]
    
    # Build query string for pagination links
    query_params = request.args.copy()
    
    # Create pagination metadata
    total_items = len(data)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Build next/previous links
    base_url = f"/{path}"
    next_link = None
    previous_link = None
    
    if page < total_pages:
        next_query = query_params.copy()
        next_query['page'] = page + 1
        next_link = f"{base_url}?{urlencode(next_query)}"
    
    if page > 1:
        prev_query = query_params.copy()
        prev_query['page'] = page - 1
        previous_link = f"{base_url}?{urlencode(prev_query)}"
    
    # Create the response object with data and pagination
    response = {
        "data": paginated_data,
        "pagination": {
            "total": total_items,
            "page": page,
            "per_page": per_page,
            "next": next_link,
            "previous": previous_link
        }
    }
    
    return response, 200

def apply_filters(data: List[Dict], filters: Dict) -> List[Dict]:
    """
    Apply filters to the response data with support for nested fields.
    
    Args:
        data: List of items to filter
        filters: Dictionary of filter parameters
        
    Returns:
        Filtered data
    """
    filtered_data = data
    
    # Reserved parameters that shouldn't be used for filtering
    reserved_params = {'page', 'per_page', 'simulate_error', 'delay'}
    
    for key, value in filters.items():
        if key not in reserved_params:
            if '.' in key:
                # Handle nested field filtering (e.g., departments.name=modeling)
                parent_field, child_field = key.split('.', 1)
                filtered_data = [
                    item for item in filtered_data 
                    if parent_field in item and any(
                        str(nested_item.get(child_field, '')) == value 
                        for nested_item in item[parent_field]
                        if isinstance(item[parent_field], list)
                    )
                ]
            else:
                # Support both asset_type and type for backward compatibility
                if key == 'asset_type' and all('type' in item for item in filtered_data):
                    filtered_data = [item for item in filtered_data if str(item.get('type', '')) == value]
                elif key == 'type' and all('asset_type' in item for item in filtered_data):
                    filtered_data = [item for item in filtered_data if str(item.get('asset_type', '')) == value]
                else:
                    filtered_data = [item for item in filtered_data if str(item.get(key, '')) == value]
    
    return filtered_data

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def mock_api(path: str):
    """Main handler for all API requests."""
    resource = path.split('/')[0] if '/' in path else path
    
    # Check if requesting enhanced version
    use_enhanced = 'enhanced' in request.args or path.endswith('/enhanced')
    if path.endswith('/enhanced'):
        path = path[:-9]  # Remove /enhanced suffix for file lookup
    
    # For methods with request body, validate against schema
    if request.method in ('POST', 'PUT'):
        schema_suffix = '_enhanced' if use_enhanced else ''
        is_valid, error = validate_request_payload(f"{resource}{schema_suffix}", request.method)
        if not is_valid:
            return jsonify(error), error.get('code', 400)
    
    # Load mock response
    if use_enhanced and resource == 'assets' and request.method == 'GET' and '/' not in path:
        # Use enhanced asset format for GET /assets/enhanced
        file_path = MOCKS_DIR / 'GET_assets_enhanced.json'
        if file_path.exists():
            with open(file_path, 'r') as f:
                response_data = json.load(f)
                status_code = 200
        else:
            # Fallback to regular assets if enhanced not found
            response_data, status_code = load_mock_file(request.method, 'assets')
    else:
        # Regular path
        response_data, status_code = load_mock_file(request.method, path)
    
    # Apply filters for GET requests with list responses
    if request.method == 'GET' and isinstance(response_data, list):
        # Apply filters
        filtered_data = apply_filters(response_data, request.args)
        
        # Always apply pagination for enhanced requests or when pagination params are present
        if use_enhanced or 'page' in request.args or 'per_page' in request.args:
            response_data, status_code = apply_pagination(filtered_data, path)
        else:
            response_data = filtered_data
    
    # Add delay if specified
    delay = request.args.get('delay')
    if delay and delay.isdigit():
        import time
        time.sleep(int(delay) / 1000)  # Convert ms to seconds
    
    return jsonify(response_data), status_code

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "1.0.0"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

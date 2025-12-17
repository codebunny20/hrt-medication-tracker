def load_json(file_path):
    """Load JSON data from a file."""
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    """Save JSON data to a file."""
    import json
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def validate_data(data, schema):
    """Validate data against a given schema."""
    from jsonschema import validate, ValidationError
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

def format_date(date):
    """Format a date to a standard string format."""
    from datetime import datetime
    return datetime.strptime(date, '%Y-%m-%d').strftime('%d %B %Y') if date else None

def generate_unique_id(existing_ids):
    """Generate a unique ID not present in the existing IDs."""
    import uuid
    new_id = str(uuid.uuid4())
    while new_id in existing_ids:
        new_id = str(uuid.uuid4())
    return new_id
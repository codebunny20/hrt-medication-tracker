import json
import uuid
from datetime import datetime
from typing import Any, Iterable, Optional

def load_json(file_path: str) -> Optional[Any]:
    """Load JSON data from a file. Returns None if file does not exist or is invalid JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def save_json(file_path: str, data: Any) -> None:
    """Save data to a JSON file (creates directories as needed)."""
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def validate_data(data: Any, schema: dict) -> bool:
    """Validate data against a JSON Schema.

    Returns True when valid, False when invalid. If jsonschema is not installed,
    prints an instruction and returns False.
    """
    try:
        from jsonschema import validate
        from jsonschema.exceptions import ValidationError
    except ImportError:
        print("jsonschema is not installed. Install it with: pip install jsonschema")
        return False

    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        # print a concise validation message
        print(f"Validation error: {e.message}")
        return False

def format_date(date_str: Optional[str]) -> Optional[str]:
    """Format a date string 'YYYY-MM-DD' to 'DD Month YYYY'. Returns None for falsy input."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
    except ValueError:
        return None

def generate_unique_id(existing_ids: Optional[Iterable[str]] = None) -> str:
    """Generate a UUID4 string not present in existing_ids (if provided)."""
    existing = set(existing_ids) if existing_ids is not None else set()
    while True:
        new_id = str(uuid.uuid4())
        if new_id not in existing:
            return new_id
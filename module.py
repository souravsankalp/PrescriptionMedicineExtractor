import base64
from pathlib import Path

# Base directory where this module.py lives
BASE_DIR = Path(__file__).resolve().parent

# Temp folder for saving decoded images
TEMP_DIR = BASE_DIR / "temp"   # will be created automatically


def process_data(data):
    """
    Expects a dict:
    {
        "id": "<file name part, string>",
        "String": "<base64 image string>"
    }

    Saves the base64 string as <id>.png inside temp/ folder.
    Returns the saved file path as string.
    """
    # Ensure temp folder exists
    TEMP_DIR.mkdir(exist_ok=True)

    file_id = data["id"]
    b64_string = data["String"]

    # If base64 comes with a prefix like "data:image/png;base64,XXXX"
    # you can optionally strip that. If you don't need this, you can remove this block.
    if "," in b64_string and "base64" in b64_string[:50]:
        b64_string = b64_string.split(",", 1)[1]

    # Decode base64 and write to file
    image_bytes = base64.b64decode(b64_string)
    file_path = TEMP_DIR / f"{file_id}.png"
    file_path.write_bytes(image_bytes)

    # Returning the file path so app.py can send it back if needed
    return str(file_path)

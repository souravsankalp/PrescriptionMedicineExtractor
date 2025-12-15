# module.py
import base64
from pathlib import Path

# Base directory where this file lives
BASE_DIR = Path(__file__).resolve().parent

# Temp folder for saving decoded images
TEMP_DIR = BASE_DIR / "temp"


def process_data(base64_string: str, file_id: str = "image") -> str:
    """
    Decode a base64-encoded image string and save it as <file_id>.png
    inside the 'temp' folder.

    Parameters
    ----------
    base64_string : str
        Raw base64 image data. Can optionally include a data URL prefix
        like 'data:image/png;base64,XXXX'.
    file_id : str
        Logical ID used for the filename. The final path will be:
            <project_root>/temp/<file_id>.png

    Returns
    -------
    str
        Full path to the saved image file.
    """
    if not isinstance(base64_string, str) or not base64_string.strip():
        raise ValueError("base64_string must be a non-empty string")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    b64_string = base64_string.strip()

    # If base64 comes as: "data:image/png;base64,AAAA..."
    if "," in b64_string and "base64" in b64_string[:50]:
        b64_string = b64_string.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(b64_string, validate=True)
    except Exception as e:
        raise ValueError(f"Invalid base64 image data: {e}") from e

    file_path = TEMP_DIR / f"{file_id}.png"
    file_path.write_bytes(image_bytes)

    return str(file_path)

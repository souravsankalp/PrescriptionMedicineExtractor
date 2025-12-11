import base64
from pathlib import Path
import os

# Base directory = folder where this module.py lives
BASE_DIR = Path(__file__).resolve().parent

# Input folder - where downloaded images are stored
DOWNLOADED_DIR = BASE_DIR / "downloaded_image"

# Output folder - where base64 converted images will be stored
INPUT_DIR = BASE_DIR / "input_image"


def process_data(data):
    """
    Expects a dict like:
    {
        "id": 123 or "abc",
        "String": "<base64-image-string>"
    }
    
    Decodes the base64 string and saves it as an image under input_image/.
    Returns the saved file path as a string.
    """
    
    # Create input_image folder if it doesn't exist
    INPUT_DIR.mkdir(exist_ok=True)
    
    # Use id as file name (string version)
    file_id = str(data.get("id"))
    b64_str = data.get("String")
    
    if b64_str is None:
        raise ValueError("Missing 'String' in data")
    
    # Decode base64 and save
    image_data = base64.b64decode(b64_str)
    file_path = INPUT_DIR / f"{file_id}.png"
    
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    return str(file_path)


def convert_downloaded_images():
    """
    Converts ALL image files from downloaded_image/ folder to base64
    and saves them as text files in input_image/ folder.
    
    This is useful for preprocessing images before sending to APIs.
    Returns a list of tuples: [(filename, base64_string), ...]
    """
    
    # Create output folder if it doesn't exist
    INPUT_DIR.mkdir(exist_ok=True)
    
    # Check if downloaded_image folder exists
    if not DOWNLOADED_DIR.exists():
        print(f"❌ Error: {DOWNLOADED_DIR} folder not found!")
        return []
    
    # Get all image files (png, jpg, jpeg, bmp, gif)
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    image_files = [f for f in DOWNLOADED_DIR.iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"⚠️  No images found in {DOWNLOADED_DIR}")
        return []
    
    print(f"🔄 Found {len(image_files)} image(s). Converting to base64...\n")
    
    converted_images = []
    
    for image_file in image_files:
        try:
            # Read image file
            with open(image_file, "rb") as f:
                image_data = f.read()
            
            # Encode to base64
            b64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Save base64 string to output folder as .txt
            output_file = INPUT_DIR / f"{image_file.stem}.txt"
            
            with open(output_file, "w") as f:
                f.write(b64_string)
            
            # Also save as .b64 for clarity
            output_b64_file = INPUT_DIR / f"{image_file.stem}.b64"
            with open(output_b64_file, "w") as f:
                f.write(b64_string)
            
            converted_images.append((image_file.stem, b64_string))
            
            print(f"✅ {image_file.name}")
            print(f"   └─ Size: {len(image_data) / 1024:.2f} KB")
            print(f"   └─ Base64: {len(b64_string) / 1024:.2f} KB\n")
        
        except Exception as e:
            print(f"❌ Error processing {image_file.name}: {e}\n")
    
    print(f"✨ Conversion complete!")
    print(f"📁 Output folder: {INPUT_DIR}/\n")
    
    return converted_images


def convert_single_image(image_path):
    """
    Convert a single image file to base64 string.
    
    Args:
        image_path (str or Path): Path to the image file
    
    Returns:
        str: Base64 encoded string
    """
    try:
        image_file = Path(image_path)
        
        if not image_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_file, "rb") as f:
            image_data = f.read()
        
        b64_string = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ Successfully converted: {image_file.name}")
        return b64_string
    
    except Exception as e:
        print(f"❌ Error converting image: {e}")
        return None


def save_base64_to_image(b64_string, output_path):
    """
    Convert base64 string back to image file.
    
    Args:
        b64_string (str): Base64 encoded string
        output_path (str or Path): Where to save the image
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        image_data = base64.b64decode(b64_string)
        
        with open(output_file, "wb") as f:
            f.write(image_data)
        
        print(f"✅ Image saved: {output_file}")
        return True
    
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False


def get_all_base64_images():
    """
    Get all base64 converted images from input_image/ folder.
    
    Returns:
        dict: {filename: base64_string, ...}
    """
    
    if not INPUT_DIR.exists():
        print(f"⚠️  {INPUT_DIR} folder doesn't exist yet")
        return {}
    
    base64_files = {}
    
    for txt_file in INPUT_DIR.glob("*.txt"):
        try:
            with open(txt_file, "r") as f:
                b64_content = f.read()
            base64_files[txt_file.stem] = b64_content
        
        except Exception as e:
            print(f"❌ Error reading {txt_file.name}: {e}")
    
    return base64_files


def cleanup_temp_files():
    """
    Remove all .txt and .b64 files from input_image/ folder.
    Useful for cleaning up before re-running conversion.
    """
    
    if not INPUT_DIR.exists():
        print(f"⚠️  {INPUT_DIR} folder doesn't exist")
        return
    
    deleted_count = 0
    
    for file in INPUT_DIR.glob("*.txt"):
        file.unlink()
        deleted_count += 1
    
    for file in INPUT_DIR.glob("*.b64"):
        file.unlink()
        deleted_count += 1
    
    print(f"🧹 Deleted {deleted_count} temporary file(s)")


if __name__ == "__main__":
    # Run conversion when executed directly
    print("=" * 60)
    print("🖼️  IMAGE TO BASE64 CONVERTER")
    print("=" * 60 + "\n")
    
    convert_downloaded_images()


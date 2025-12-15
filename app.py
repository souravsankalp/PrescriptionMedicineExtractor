# app.py
# ============================================
# STEP 1: IMPORT REQUIRED LIBRARIES
# ============================================
from flask import Flask, request, jsonify
from uuid import uuid4

from module import process_data                     # base64 -> image
from extraction import extract_text_from_image      # image -> DOCX
from clean import clean_text                        # DOCX -> cleaned text
from LLM import medi_Extract                        # cleaned text -> medicines


# ============================================
# STEP 2: CREATE FLASK APPLICATION INSTANCE
# ============================================
app = Flask(__name__)


# ============================================
# STEP 3: DEFINE ROUTE TO RECEIVE JSON DATA
# ============================================
@app.route('/receive-data', methods=['POST'])
def receive_data():
    """
    Expected JSON body:
        {
            "Base64_String": "<base64 image data>"
        }

    Returns JSON:
        {
            "message": "Data processed successfully",
            "image_path": "<path to saved PNG>",
            "docx_path": "<path to generated DOCX>",
            "text": "<cleaned extracted text>",
            "medications": [ ... ]
        }
    """

    # STEP 4: GET JSON DATA FROM REQUEST
    data = request.get_json(silent=True)

    # STEP 5: BASIC VALIDATION
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    if "Base64_String" not in data:
        return jsonify({"error": "Missing 'Base64_String' key"}), 400

    base64_string = data["Base64_String"]

    if not isinstance(base64_string, str) or not base64_string.strip():
        return jsonify({"error": "'Base64_String' must be a non-empty string"}), 400

    # Generate an internal file ID (no id required from client)
    file_id = f"req_{uuid4().hex[:8]}"

    # ============================================
    # STEP 6: DECODE BASE64 -> PNG IMAGE
    # ============================================
    try:
        image_path = process_data(base64_string, file_id=file_id)
    except Exception as e:
        return jsonify({"error": f"Failed to decode base64 image: {e}"}), 500

    # ============================================
    # STEP 7: RUN OCR (IMAGE -> DOCX)
    # ============================================
    try:
        docx_path = extract_text_from_image(image_path, file_id=file_id)
    except Exception as e:
        return jsonify({"error": f"Failed to extract text from image: {e}"}), 500

    # ============================================
    # STEP 8: CLEAN TEXT FROM DOCX
    # ============================================
    try:
        extracted_text = clean_text(docx_path)
    except Exception as e:
        return jsonify({"error": f"Failed to clean text from DOCX: {e}"}), 500

    # ============================================
    # STEP 9: RUN LLM TO GET MEDICATIONS
    # ============================================
    try:
        medications = medi_Extract(extracted_text)
    except Exception as e:
        # LLM failure shouldn't crash the whole request; return empty list
        medications = []
        # If you want to expose the error, uncomment:
        # return jsonify({"error": f"LLM processing failed: {e}"}), 500

    # ============================================
    # STEP 10: RETURN RESPONSE
    # ============================================
    return jsonify({
        "message": "Data processed successfully",
        "image_path": image_path,
        "docx_path": docx_path,
        "text": extracted_text,
        "medications": medications
    }), 200


# ============================================
# STEP 11: RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True)

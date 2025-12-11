# ============================================
# STEP 1: IMPORT REQUIRED LIBRARIES
# ============================================
from flask import Flask, request, jsonify
from module import process_data                     # base64 -> image
from extraction import extract_text_from_image      # image -> DOCX
from clean import clean_text                        # DOCX -> cleaned text
from LLM import medi_Extract                        # cleaned text -> medicines
# from docx import Document                         # Used earlier for text_shown (now commented)


# ============================================
# STEP 2: CREATE FLASK APPLICATION INSTANCE
# ============================================
app = Flask(__name__)


# ------------------------------------------------
# (OLD) Helper function: DOCX -> text
# Kept here but commented out as per your request
# ------------------------------------------------
# def text_shown(docx_path):
#     """
#     Reads the generated .docx file and returns all text as a single string.
#     (No cleaning, just raw paragraphs.)
#     """
#     doc = Document(docx_path)
#     lines = []
#     for para in doc.paragraphs:
#         line = para.text.strip()
#         if line:
#             lines.append(line)
#     return "\n".join(lines)


# ============================================
# STEP 3: DEFINE ROUTE - ACCEPT KEY-VALUE PAIRS
# ============================================
@app.route('/receive-data', methods=['POST'])
def receive_data():
    # ============================================
    # STEP 4: GET JSON DATA FROM REQUEST
    # ============================================
    data = request.get_json(silent=True)  # Parses JSON; returns None if invalid

    # ============================================
    # STEP 5: BASIC VALIDATION
    # ============================================
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Required keys
    if "id" not in data or "String" not in data:
        return jsonify({"error": "Missing 'id' or 'String' key"}), 400

    # id is used as file name / identifier
    if not isinstance(data["id"], str):
        return jsonify({"error": "id must be string"}), 400

    # Base64 must be text
    if not isinstance(data["String"], str):
        return jsonify({"error": "String must be text"}), 400

    try:
        # ============================================
        # STEP 6: BASE64 -> IMAGE (module.py)
        # ============================================
        image_path = process_data(data)   # returns full path to saved image (e.g., id-2.png)

        # ============================================
        # STEP 7: IMAGE -> DOCX (extraction.py)
        # ============================================
        docx_path = extract_text_from_image(image_path, data["id"])
        # This creates something like: E:\ImageTextSqubix\temp\<id>.docx

        # ============================================
        # STEP 8: DOCX -> CLEANED TEXT (clean.py)
        # ============================================
        # Old approach (commented out, as you requested):
        # extracted_text = text_shown(docx_path)
        extracted_text = clean_text(docx_path)

        # ============================================
        # STEP 9: CLEANED TEXT -> MEDICINE LIST (LLM.py via Groq)
        # ============================================
        medications = medi_Extract(extracted_text)

    except Exception as e:
        # Any unexpected error in the pipeline
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

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

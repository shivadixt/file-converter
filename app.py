from flask_cors import CORS
from flask import Flask, request, send_file
from PIL import Image
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. JPG to PDF
@app.route("/convert/jpg-to-pdf", methods=["POST"])
def jpg_to_pdf():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    image_file = request.files["file"]
    filename = str(uuid.uuid4()) + ".pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    img = Image.open(image_file.stream).convert("RGB")
    img.save(filepath, "PDF", resolution=100.0)
    img.close()

    return send_file(filepath, as_attachment=True)

# 2. JPG ↔ PNG
@app.route("/convert/jpg-png", methods=["POST"])
def jpg_png():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    image_file = request.files["file"]
    original_name = image_file.filename.lower()
    ext = os.path.splitext(original_name)[1]

    if ext in [".jpg", ".jpeg"]:
        new_ext = ".png"
        output_format = "PNG"
    elif ext == ".png":
        new_ext = ".jpg"
        output_format = "JPEG"
    else:
        return {"error": "Unsupported file format"}, 400

    new_filename = str(uuid.uuid4()) + new_ext
    filepath = os.path.join(UPLOAD_FOLDER, new_filename)

    img = Image.open(image_file.stream).convert("RGB")
    img.save(filepath, output_format)
    img.close()

    return send_file(filepath, as_attachment=True)

# 3. PDF to JPG
@app.route("/convert/pdf-to-jpg", methods=["POST"])
def pdf_to_jpg():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    pdf_file = request.files["file"]
    images = convert_from_bytes(pdf_file.read())

    output_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.jpg")
    images[0].save(output_path, "JPEG")

    return send_file(output_path, as_attachment=True)

# 4. Compress PDF
@app.route("/convert/compress-pdf", methods=["POST"])
def compress_pdf():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    pdf_file = request.files["file"]
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

    output_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_compressed.pdf")
    doc.save(output_path, deflate=True)
    doc.close()

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

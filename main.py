from flask import Flask, request, send_file, jsonify
import os
import tempfile
import subprocess

app = Flask(__name__)

# Example: convert any office doc to PDF using LibreOffice
def convert_to_pdf(input_path):
    output_dir = tempfile.mkdtemp()
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf",
        "--outdir", output_dir, input_path
    ], check=True)
    filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    return os.path.join(output_dir, filename)

# Example: convert PDF to text using pdftotext (Poppler)
def convert_pdf_to_txt(input_path):
    output_path = tempfile.mktemp(suffix=".txt")
    subprocess.run(["pdftotext", input_path, output_path], check=True)
    return output_path

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    direction = request.form.get("direction", "to-pdf")  # "to-pdf" or "from-pdf"
    target = request.form.get("target", "txt")           # target format when from-pdf

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        input_path = tmp.name

    try:
        if direction == "to-pdf":
            output_path = convert_to_pdf(input_path)
        else:
            if target == "txt":
                output_path = convert_pdf_to_txt(input_path)
            else:
                return jsonify({"error": "Unsupported target format"}), 400

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(input_path)

if __name__ == "__main__":
    app.run(debug=True)
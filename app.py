import os
import sys
import tempfile
import traceback
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Force UTF-8 output encoding on Windows to handle Unicode characters from LLM responses
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from services.summarizer import summarize_report
from services.guardrails import verify_measurements
from services.parser import extract_text_from_file
from services.samples import SAMPLES

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit

# Enable CORS for local development & direct file opening
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/samples", methods=["GET"])
def get_samples():
    return jsonify(SAMPLES)

@app.route("/summarize", methods=["POST", "OPTIONS"])
def summarize():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        raw_text = ""

        # Check JSON payload
        if request.is_json:
            data = request.get_json() or {}
            sample_key = data.get("sample_key")
            if sample_key and sample_key in SAMPLES:
                sample = SAMPLES[sample_key]
                raw_text = sample["report_text"]
                if "precomputed_summary" in sample:
                    summary_dict = sample["precomputed_summary"]
                    guardrails = verify_measurements(raw_text, summary_dict)
                    return jsonify({
                        "success": True,
                        "raw_text": raw_text,
                        "summary": summary_dict,
                        "guardrails": guardrails,
                        "instant": True
                    })

            raw_text = data.get("text", "")

        # Check Multipart / Form submission
        else:
            if "file" in request.files and request.files["file"].filename != "":
                file_obj = request.files["file"]
                filename = file_obj.filename
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                    file_obj.save(temp_file.name)
                    temp_path = temp_file.name

                try:
                    raw_text = extract_text_from_file(temp_path, filename)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                raw_text = request.form.get("text", "")

        raw_text = (raw_text or "").strip()
        if not raw_text or len(raw_text) < 10:
            return jsonify({
                "error": "Please provide a valid medical report file or text with at least 10 characters."
            }), 400

        # Run Gemini Summarizer Engine
        summary_model = summarize_report(raw_text)
        summary_dict = summary_model.model_dump()

        # Run Anti-Hallucination Guardrails
        guardrail_result = verify_measurements(raw_text, summary_dict)

        return jsonify({
            "success": True,
            "raw_text": raw_text,
            "summary": summary_dict,
            "guardrails": guardrail_result,
            "instant": False
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Failed to analyze medical report: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

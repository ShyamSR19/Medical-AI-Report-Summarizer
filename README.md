# ClarityMed Navigator 🏥

> **Patient-Centered Medical Report Navigator & Visual Summarizer**

ClarityMed Navigator translates complex, clinical medical reports (CT scans, blood panels, MRIs) into clear, compassionate, patient-friendly language at a 6th–8th grade reading level, while remaining strictly faithful to the original medical document.

---

## 🌟 Key Features

- **Strict Medical Faithfulness**: Explains exactly what the report says without inventing medical advice, lifestyle changes, symptom diaries, or ungrounded claims.
- **Exact Metric Preservation**: Preserves all measurements (e.g., `1.4 cm`, `11.2 g/dL`) with everyday visual size analogies (e.g., *"Smaller than a pea (1.4 cm)"*).
- **Anti-Hallucination Guardrails**: Cross-verifies all numeric values in generated findings against the source report text to ensure grounding and accuracy.
- **Calm, Non-Intimidating UI**: Clean, uncluttered interface designed to reduce patient anxiety with progressive disclosure:
  - Overall status banner with reassuring, objective categorization (`routine`, `monitor`, or `urgent`).
  - Plain-language findings with real-world scale comparisons.
  - Actionable next steps derived strictly from explicit recommendations in the report.
  - Collapsible consultation questions for the patient's next doctor visit.
  - Expandable medical details preserving verbatim doctor impressions and pertinent negatives.
- **Multi-Format Ingestion**: Supports uploading PDFs, images (`PNG`, `JPG`), plain text files (`.txt`), or direct text pasting.
- **Preloaded Clinical Samples**: One-click demos for Chest CT, Routine Blood Panel, and Brain MRI.
- **PDF Export**: Print/save clean patient analysis summaries.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14+, Flask
- **LLM Engine**: Groq API (`openai/gpt-oss-120b`) with strict JSON schema validation
- **Document & Image Parsing**: `pdfplumber`, `pytesseract` (Tesseract OCR), `Pillow`
- **Data Validation**: Pydantic v2
- **Frontend**: HTML5, Vanilla CSS, Tailwind CSS v3, Lucide Icons

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.12+ (or Python 3.14)
- A [Groq API Key](https://console.groq.com)
- *(Optional)* [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (required only for image OCR)

### 2. Installation

Clone this repository and navigate into the project directory:

```bash
git clone https://github.com/<your-username>/Medical-AI-Report-Summarizer.git
cd Medical-AI-Report-Summarizer
```

Create and activate a virtual environment:

```bash
# Windows
py -3.14 -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory (based on `.env.example`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔒 Privacy & Safety Disclaimer

ClarityMed Navigator is an educational and informational tool designed to help patients understand complex clinical terminology. It does not provide medical diagnosis, treatment, or clinical decision-making. Always consult a licensed healthcare provider for clinical advice and treatment decisions.

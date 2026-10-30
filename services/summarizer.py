import os
import sys
import json
import unicodedata
import requests
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

# Try importing Google GenAI SDK if available
try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

# Force UTF-8 on Windows stdout to prevent charmap errors when printing LLM output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=env_path)


# ─── Pydantic Output Schema ───────────────────────────────────────────────────

class ClinicalDrawer(BaseModel):
    exact_impression: str = Field(
        description="Raw verbatim clinical quote from impression or findings."
    )
    measurements: str = Field(
        description="Exact metric units (e.g. '1.4 cm x 1.1 cm', '11.2 g/dL') or 'None reported'."
    )
    pertinent_negatives: List[str] = Field(
        description="Explicitly ruled-out conditions in the report (e.g. ['No acute pulmonary embolism'])."
    )
    clinical_action: str = Field(
        description="Recommendation explicitly stated in the report, or 'None specified'."
    )

class Finding(BaseModel):
    organ: str = Field(
        description="Specific organ/system. If incidental in report, label clearly (e.g. 'Left Adrenal Gland (Incidental Finding)')."
    )
    simple_explanation: str = Field(
        description="Plain language translation strictly faithful to report. Preserves uncertainty and measurements without stronger interpretations or unmentioned claims."
    )
    visual_analogy: str = Field(
        description="Real-world physical scale comparison with exact metric measurement in parentheses, e.g. 'Smaller than a pea (1.4 cm)' or 'Within normal reference limits'."
    )
    clinical_drawer: ClinicalDrawer

class OverallStatus(BaseModel):
    banner_title: str = Field(
        description="Calm, objective title banner based strictly on findings (e.g. 'No Concerning Findings Identified', 'Routine Finding Identified', 'Findings Requiring Follow-Up')."
    )
    subtitle: str = Field(
        description="Concise 1-2 sentence faithful summary explaining findings without exaggerated reassurance or ungrounded claims."
    )
    status_level: Literal["routine", "monitor", "urgent"] = Field(
        description="Categorization: 'routine' (normal, clear, or stable/benign findings without required intervention) | 'monitor' (findings with explicit recommendation for follow-up testing, re-scan, biopsy, or doctor discussion) | 'urgent' (report explicitly indicates acute or immediate emergency pathology)."
    )

class MedicalSummary(BaseModel):
    overall_status: OverallStatus
    target_systems: List[str] = Field(
        description="List of target organs/systems explicitly examined in report."
    )
    findings: List[Finding]
    patient_checklist: List[str] = Field(
        description="Actionable next steps based ONLY on explicit recommendations in the report. Never invent medical advice."
    )
    doctor_questions: List[str] = Field(
        description="2 to 3 questions for consultation grounded directly in the report findings."
    )


# ─── JSON Schema Builder ──────────────────────────────────────────────────────

def _build_json_schema() -> dict:
    """Returns the JSON schema for MedicalSummary for Groq's json_schema mode."""
    return {
        "name": "MedicalSummary",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "overall_status": {
                    "type": "object",
                    "properties": {
                        "banner_title": {"type": "string"},
                        "subtitle": {"type": "string"},
                        "status_level": {"type": "string", "enum": ["routine", "monitor", "urgent"]}
                    },
                    "required": ["banner_title", "subtitle", "status_level"],
                    "additionalProperties": False
                },
                "target_systems": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "organ": {"type": "string"},
                            "simple_explanation": {"type": "string"},
                            "visual_analogy": {"type": "string"},
                            "clinical_drawer": {
                                "type": "object",
                                "properties": {
                                    "exact_impression": {"type": "string"},
                                    "measurements": {"type": "string"},
                                    "pertinent_negatives": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "clinical_action": {"type": "string"}
                                },
                                "required": ["exact_impression", "measurements", "pertinent_negatives", "clinical_action"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["organ", "simple_explanation", "visual_analogy", "clinical_drawer"],
                        "additionalProperties": False
                    }
                },
                "patient_checklist": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "doctor_questions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["overall_status", "target_systems", "findings", "patient_checklist", "doctor_questions"],
            "additionalProperties": False
        }
    }


# ─── Main Summarizer ──────────────────────────────────────────────────────────

def _sanitize_unicode(text: str) -> str:
    """
    Replaces non-ASCII Unicode characters that Windows charmap can't handle
    with safe ASCII equivalents.
    """
    replacements = {
        '\u2011': '-',   # non-breaking hyphen
        '\u2010': '-',   # hyphen
        '\u2012': '-',   # figure dash
        '\u2013': '-',   # en dash
        '\u2014': '-',   # em dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2022': '*',   # bullet
        '\u00b0': ' degrees',  # degree sign
        '\u00d7': 'x',   # multiplication sign
        '\u2265': '>=',  # greater or equal
        '\u2264': '<=',  # less or equal
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('ascii', errors='replace').decode('ascii')


def _extract_json_string(text: str) -> str:
    """
    Extracts JSON substring if wrapped in markdown codeblocks (```json ... ```)
    or extraneous preambles/postscripts.
    """
    text = text.strip()
    if "```json" in text:
        parts = text.split("```json", 1)[1]
        text = parts.split("```", 1)[0].strip()
    elif "```" in text:
        parts = text.split("```", 1)[1]
        text = parts.split("```", 1)[0].strip()
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1].strip()
    return text


SYSTEM_PROMPT = """You are an expert clinical AI assistant that explains medical reports to patients with strict, uncompromising faithfulness to the source document.

CRITICAL IDENTITY AND PURPOSE:
- You are an EXPLANATION TOOL, NOT a medical decision-making system.
- Your purpose is to explain what the report says, preserve the report's exact degree of uncertainty, and surface the report's own recommendations without inventing additional medical instructions.
- Be objective, crisp, and concise. Do NOT be verbose, flowery, conversational, or overly wordy. Keep each explanation direct and strictly grounded in the report text.
- Always output valid JSON conforming strictly to the requested schema."""


def _build_prompt(raw_text: str) -> str:
    return f"""Translate the following clinical medical report into clear, patient-accessible language while adhering STRICTLY to all non-negotiable faithfulness rules below:

=== CORE MANDATE: STRICT FAITHFULNESS TO SOURCE REPORT ===

1. NEVER INVENT MEDICAL ADVICE:
- Only include recommendations or next steps that are EXPLICITLY present in the source report.
- Do NOT add lifestyle advice, symptom diaries, smoking cessation advice, diet advice, hydration advice, exercise advice, or unmentioned medication advice unless the report itself explicitly contains them.
- If the source report does NOT contain explicit follow-up recommendations, the patient checklist must state: "Discuss these results with your doctor at your next appointment." Do NOT invent tasks.

2. NEVER MAKE RECOMMENDATIONS MORE URGENT OR MORE SPECIFIC THAN THE SOURCE:
- If source states: "PET/CT and/or tissue sampling is recommended."
  Good: "Your report recommends further evaluation with PET/CT and/or tissue sampling. Discuss the appropriate next step with your doctor."
  Bad: "Schedule a biopsy immediately."
- Match the exact urgency of the report. Never escalate or assume timeframes not stated in the report.

3. PRESERVE ALL MEASUREMENTS EXACTLY & NO UNMEASURED ANALOGIES:
- Keep every measurement exactly as stated with its original numbers and metric units (e.g., 2.3 x 1.8 cm, 6 mm, 1.3 cm lymph node, 1.4 cm adrenal nodule, 1.1 cm liver cyst, 1.2 cm kidney cyst, 5.1 x 4.6 x 4.8 cm prostate, 11.2 g/dL, 4 HU).
- Never round, drop, estimate, or alter numbers or units.
- In visual analogies, ONLY provide an object comparison if an exact measurement was explicitly reported, and always include that measurement in parentheses, e.g., "Smaller than a pea (1.4 cm)".
- If NO measurement is given in the report for a finding, visual_analogy MUST be: "No measurement specified in report". NEVER invent an analogy (such as "size of a walnut" or "size of an orange") when no measurement is in the report.

4. DO NOT INTRODUCE STRONGER INTERPRETATIONS THAN THE SOURCE:
- If source says "mild centrilobular emphysematous changes", do NOT change this to "early emphysema" or "early signs of emphysema" unless the report explicitly uses the word "early".
  Good: "Mild emphysematous changes are present in the visualized lungs."
  Bad: "Early emphysema" or "early signs of emphysema".
- Never insert qualifier words like "early", "mild", "advanced", "chronic", or "acute" unless they are explicitly in the source report text.

5. DO NOT INTRODUCE CLAIMS ABSENT FROM THE REPORT:
- If source only says "mildly enlarged prostate", do NOT generate "not causing any blockage" or mention urinary flow.
  Good: "The prostate is mildly enlarged."
  Bad: "The prostate is enlarged but isn't causing blockage."
- If information is not present in the source report, do not guess or extrapolate. Use wording such as: "The report does not specify this."

6. PRESERVE UNCERTAINTY:
- If the report says "suspicious", "most likely", "compatible with", "possible", or "recommended", preserve that exact level of uncertainty in the patient-friendly explanation.
- Example: Instead of "A harmless fatty tumor", use: "The 1.4 cm adrenal nodule has imaging characteristics compatible with a benign lipid-rich adrenal adenoma."

7. AVOID EMOTIONALLY ALARMING LANGUAGE:
- Do not automatically introduce words like "cancer", "dangerous", or "serious" unless the source report explicitly establishes or strongly discusses that diagnosis.

8. MEDICALLY FAITHFUL & CONCISE TRANSLATION:
- Simplify terminology to 6th-8th grade reading level without altering medical meaning, certainty, or scope.
- Keep simple_explanation concise and direct (1-2 sentences per finding). Avoid conversational fluff, padding, or excessive verbosity.

9. CLEARLY DISTINGUISH INCIDENTAL FINDINGS:
- For incidental findings, clearly label them (e.g. in the organ field: "Left Adrenal Gland (Incidental Finding)") so they are not confused with primary indications.

10. "WHAT TO DO NEXT" (patient_checklist):
- Must be generated ONLY from explicit recommendations in the report.
- If the report has explicit recommendations, list them faithfully.
- If the report has NO explicit recommendations, provide: "Discuss these findings with your doctor." Do NOT invent tasks like keeping a headache diary or changing diet.

11. "QUESTIONS FOR YOUR DOCTOR" (doctor_questions):
- Convert explicit findings or recommendations from the report into 2-3 focused consultation questions.
- Do NOT introduce new diagnoses, speculative treatments, or unmentioned conditions.

12. STATUS LEVEL CATEGORIZATION:
- 'routine': scan is unremarkable, completely clear, or has purely incidental benign findings with routine checkups.
- 'monitor': report explicitly recommends follow-up imaging (e.g. follow-up CT, PET/CT), further testing, tissue sampling/biopsy, repeat lab panels, or physician discussion.
- 'urgent': report explicitly describes acute emergency or immediately life-threatening findings.

13. INTERNAL CROSS-CHECK BEFORE OUTPUTTING:
- Cross-check every:
  • number & measurement
  • body location & organ
  • diagnosis & finding
  • recommendation
  against the source report. Everything must be grounded in the text.

Medical Report to Translate:
---
{raw_text}
---

Respond with valid JSON matching the schema."""


# ─── Model Callers ────────────────────────────────────────────────────────────

def _call_groq(groq_api_key: str, model_name: str, prompt: str) -> str:
    """Calls Groq API with json_schema, falling back to json_object if needed."""
    client = Groq(api_key=groq_api_key)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": _build_json_schema()
            },
            temperature=0.0,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback to json_object format
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=4096
        )
        return response.choices[0].message.content


def _call_gemini(gemini_api_key: str, prompt: str) -> str:
    """Calls Google Gemini API with fallback across model versions."""
    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest"
    ]
    last_err = None

    for model_name in models_to_try:
        # 1. Try Google GenAI SDK if available
        if HAS_GOOGLE_GENAI:
            try:
                client = genai.Client(api_key=gemini_api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MedicalSummary,
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.0
                    )
                )
                if response and response.text:
                    return response.text
            except Exception as sdk_err:
                last_err = sdk_err

        # 2. Try REST API fallback
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
            payload = {
                "system_instruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.0
                }
            }
            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                last_err = RuntimeError(f"Gemini {model_name} HTTP {resp.status_code}: {resp.text}")
        except Exception as rest_err:
            last_err = rest_err

    raise RuntimeError(f"Gemini API Error: {last_err}")


# ─── Main Summarizer with Multi-Model Fallback ────────────────────────────────

def summarize_report(raw_text: str) -> MedicalSummary:
    """
    Translates a clinical medical report for patients strictly faithful to the source document.
    Uses multi-model fallback:
      1. Primary: Groq openai/gpt-oss-120b
      2. Backup 1: Google Gemini API (if GEMINI_API_KEY is configured in .env)
      3. Backup 2: Groq qwen/qwen3.8-27b
    """
    # Reload environment to pick up any manually added keys in .env
    load_dotenv(dotenv_path=env_path, override=True)

    groq_api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()

    if not groq_api_key and not gemini_api_key:
        raise RuntimeError(
            "Neither GROQ_API_KEY nor GEMINI_API_KEY is configured in your .env file.\n"
            "Please provide at least one API key in the .env file."
        )

    prompt = _build_prompt(raw_text)

    # Build fallback candidates list
    candidates = []

    # 1. Primary: Groq openai/gpt-oss-120b
    if groq_api_key:
        candidates.append({
            "name": "Groq (openai/gpt-oss-120b)",
            "func": lambda: _call_groq(groq_api_key, "openai/gpt-oss-120b", prompt)
        })

    # 2. Backup 1: Google Gemini API (if configured in .env)
    if gemini_api_key:
        candidates.append({
            "name": "Google Gemini API",
            "func": lambda: _call_gemini(gemini_api_key, prompt)
        })

    # 3. Backup 2: Groq qwen/qwen3.8-27b
    if groq_api_key:
        candidates.append({
            "name": "Groq (qwen/qwen3.8-27b)",
            "func": lambda: _call_groq(groq_api_key, "qwen/qwen3.8-27b", prompt)
        })

    attempt_errors = []

    for candidate in candidates:
        name = candidate["name"]
        try:
            print(f"[Summarizer] Attempting analysis using {name}...")
            raw_output = candidate["func"]()
            extracted_json = _extract_json_string(raw_output)
            clean_json = _sanitize_unicode(extracted_json)
            summary = MedicalSummary.model_validate_json(clean_json)
            print(f"[Summarizer] Successfully generated summary using {name}!")
            return summary
        except Exception as err:
            err_msg = str(err).encode("ascii", errors="replace").decode("ascii")
            print(f"[Summarizer] {name} failed: {err_msg}")
            attempt_errors.append(f"{name}: {err_msg}")

    # If all candidates fail
    details = "\n".join(f"  * {e}" for e in attempt_errors)
    raise RuntimeError(f"All AI summary providers failed:\n{details}")




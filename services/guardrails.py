import re
from typing import Dict, Any, List

def extract_metric_tokens(text: str) -> List[str]:
    """
    Extracts numerical measurements with units from text.
    Matches formats like: 1.4 cm, 14 mm, 11.5 g/dL, 45%, 1.4 x 1.1 cm, 120/80 mmHg, etc.
    """
    # Regex for numbers followed by optional spaces and standard medical/metric units
    pattern = r'\b\d+(?:\.\d+)?(?:\s*(?:x|×|-|\to)\s*\d+(?:\.\d+)?)?\s*(?:cm|mm|mg|g/dL|g/L|mL|mmHg|%|U/L|mmol/L|mcg|kg)\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    # Normalize matches
    normalized = [m.strip().lower() for m in matches]
    return normalized

def extract_raw_numbers(text: str) -> List[str]:
    """
    Extracts raw numbers (integers & floats) from text.
    """
    pattern = r'\b\d+(?:\.\d+)?\b'
    return re.findall(pattern, text)

def verify_measurements(raw_text: str, structured_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anti-Hallucination Guardrail:
    Cross-verifies all numerical measurements found across clinical drawers and
    finding explanations against the source report text.
    """
    source_metrics = extract_metric_tokens(raw_text)
    source_numbers = set(extract_raw_numbers(raw_text))

    reported_measurements: List[str] = []
    hallucinations: List[str] = []
    matched_metrics: List[str] = []

    # Traverse structured findings
    findings = structured_summary.get("findings", [])
    for finding in findings:
        drawer = finding.get("clinical_drawer", {})
        measurement_text = drawer.get("measurements", "")
        if measurement_text and measurement_text.lower() != "none reported":
            reported_measurements.append(measurement_text)
            
            # Extract numbers inside this reported measurement
            numbers_in_drawer = extract_raw_numbers(measurement_text)
            for num in numbers_in_drawer:
                if num in source_numbers:
                    matched_metrics.append(f"{num} (Verified in source)")
                else:
                    hallucinations.append(f"Unverified number '{num}' in measurement: '{measurement_text}'")

        # Also cross-verify any metric units stated in simple_explanation or visual_analogy
        for field_name in ["simple_explanation", "visual_analogy"]:
            field_text = finding.get(field_name, "")
            metrics_in_field = extract_metric_tokens(field_text)
            for m in metrics_in_field:
                m_nums = extract_raw_numbers(m)
                for num in m_nums:
                    if num in source_numbers:
                        matched_metrics.append(f"{num} (Verified in source)")
                    else:
                        hallucinations.append(f"Unverified metric number '{num}' in {field_name}: '{m}'")

    grounding_score = 100.0 if not hallucinations else round(max(0.0, 100.0 - (len(hallucinations) * 25.0)), 1)
    passed = len(hallucinations) == 0

    return {
        "passed": passed,
        "grounding_score": grounding_score,
        "source_metrics_detected": source_metrics,
        "matched_metrics": list(set(matched_metrics)),
        "hallucinations": hallucinations,
        "message": "Measurements checked against your report" if passed else f"{len(hallucinations)} unverified value(s) detected"
    }



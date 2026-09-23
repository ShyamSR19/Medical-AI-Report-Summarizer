SAMPLES = {
    "chest_ct": {
        "title": "Chest CT (1.4 cm Adrenal Spot)",
        "report_text": """
EXAMINATION: CT CHEST WITH CONTRAST

CLINICAL INDICATION: Persistent post-viral cough and atypical chest pain.

FINDINGS:
LUNGS: Clear. No consolidation, pleural effusion, or pneumothorax. No acute pulmonary embolism.
HEART: Normal cardiac size and mediastinal contours. No pericardial effusion.
ABDOMEN / LOWER CUTS: Incidental note of a well-circumscribed, low-attenuation (4 HU) nodule in the left adrenal gland measuring 1.4 cm x 1.1 cm. Features are consistent with a benign adrenal adenoma. No lymphadenopathy.

IMPRESSION:
1. No acute thoracic pathology. Lungs are completely clear. No pulmonary embolism.
2. Incidental 1.4 cm benign left adrenal nodule (attenuation 4 HU, consistent with lipid-rich adenoma).
3. Recommendation: Follow-up non-contrast CT abdomen in 6 to 12 months for stability confirmation.
""",
        "precomputed_summary": {
            "overall_status": {
                "banner_title": "Routine Finding Identified",
                "subtitle": "No acute thoracic pathology is identified in your chest scan. An incidental 1.4 cm adrenal nodule was noted with features consistent with a benign adenoma, with follow-up recommended in 6 to 12 months.",
                "status_level": "routine"
            },
            "target_systems": ["Lungs & Heart", "Adrenal Gland"],
            "findings": [
                {
                    "organ": "Lungs & Heart (Primary Finding)",
                    "simple_explanation": "No acute thoracic pathology was identified. The lungs and heart are completely clear of acute issues or pulmonary embolism.",
                    "visual_analogy": "100% Clear & Healthy",
                    "clinical_drawer": {
                        "exact_impression": "No acute thoracic pathology. Lungs are completely clear. No pulmonary embolism.",
                        "measurements": "None reported (All clear)",
                        "pertinent_negatives": ["No acute pulmonary embolism", "No consolidation", "No pleural effusion", "No pneumothorax", "No pericardial effusion"],
                        "clinical_action": "No respiratory follow-up required."
                    }
                },
                {
                    "organ": "Left Adrenal Gland (Incidental Finding)",
                    "simple_explanation": "The 1.4 cm adrenal nodule has imaging characteristics compatible with a benign lipid-rich adrenal adenoma.",
                    "visual_analogy": "Smaller than a pea (1.4 cm x 1.1 cm)",
                    "clinical_drawer": {
                        "exact_impression": "Incidental 1.4 cm benign left adrenal nodule (attenuation 4 HU, consistent with lipid-rich adenoma).",
                        "measurements": "1.4 cm x 1.1 cm (4 HU)",
                        "pertinent_negatives": ["No lymphadenopathy"],
                        "clinical_action": "Follow-up non-contrast CT abdomen in 6 to 12 months for stability confirmation."
                    }
                }
            ],
            "patient_checklist": [
                "Schedule a follow-up non-contrast CT scan of the abdomen in 6 to 12 months for stability confirmation as recommended in your report.",
                "Discuss these scan findings and the follow-up timeline with your doctor."
            ],
            "doctor_questions": [
                "When would you like to schedule the recommended 6 to 12 month follow-up CT scan for the adrenal nodule?",
                "Are any simple hormone evaluations indicated for this incidental adrenal nodule?",
                "Since my chest scan is clear, what next steps do you recommend for my cough and chest discomfort?"
            ]
        }
    },
    "blood_panel": {
        "title": "Routine Blood Panel (Mild Anemia)",
        "report_text": """
EXAMINATION: COMPLETE BLOOD COUNT (CBC) & COMPREHENSIVE METABOLIC PANEL

CLINICAL INDICATION: Annual routine health screening, mild fatigue.

LABORATORY FINDINGS:
HEMOGLOBIN: 11.2 g/dL (Reference Range: 12.0 - 15.5 g/dL) - Mildly Low.
HEMATOCRIT: 34.1% (Reference Range: 37.0 - 48.0%) - Mildly Low.
RBC COUNT: 3.9 x10^6/uL (Reference Range: 4.2 - 5.4 x10^6/uL).
MCV: 78 fL (Reference Range: 80 - 100 fL) - Slightly Microcytic.
WBC COUNT: 6.4 x10^3/uL (Reference Range: 4.5 - 11.0 x10^3/uL) - Normal.
PLATELETS: 245 x10^3/uL (Reference Range: 150 - 450 x10^3/uL) - Normal.
SERUM FERRITIN: 14 ng/mL (Reference Range: 20 - 200 ng/mL) - Low iron storage.
KIDNEY & LIVER FUNCTION: BUN 14 mg/dL, Creatinine 0.8 mg/dL, AST 18 U/L, ALT 22 U/L - All within normal limits.

IMPRESSION:
1. Mild microcytic hypochromic anemia consistent with early stage iron deficiency.
2. Normal white blood cell count and platelet count; no signs of active infection or marrow suppression.
3. Recommendation: Oral iron supplementation under physician guidance; dietary optimization; repeat CBC in 8-12 weeks.
""",
        "precomputed_summary": {
            "overall_status": {
                "banner_title": "Mild Anemia Identified",
                "subtitle": "Findings show mild microcytic hypochromic anemia consistent with early stage iron deficiency. White blood cells, platelets, kidney, and liver function are all within normal limits.",
                "status_level": "monitor"
            },
            "target_systems": ["Red Blood Cells & Iron", "White Blood Cells & Platelets", "Kidneys & Liver"],
            "findings": [
                {
                    "organ": "Red Blood Cells & Iron Storage",
                    "simple_explanation": "Mild microcytic hypochromic anemia consistent with early stage iron deficiency. Hemoglobin is mildly low at 11.2 g/dL and ferritin is 14 ng/mL.",
                    "visual_analogy": "Hemoglobin 11.2 g/dL (Reference: 12.0 - 15.5 g/dL)",
                    "clinical_drawer": {
                        "exact_impression": "Mild microcytic hypochromic anemia consistent with early stage iron deficiency.",
                        "measurements": "Hemoglobin 11.2 g/dL, Hematocrit 34.1%, Ferritin 14 ng/mL, MCV 78 fL",
                        "pertinent_negatives": ["No white blood cell abnormality", "No platelet count abnormality", "No signs of marrow suppression", "Normal kidney and liver function"],
                        "clinical_action": "Oral iron supplementation under physician guidance; dietary optimization; repeat CBC in 8-12 weeks."
                    }
                }
            ],
            "patient_checklist": [
                "Discuss oral iron supplementation under your physician's guidance as recommended in your report.",
                "Discuss dietary optimization options with your doctor.",
                "Schedule a repeat CBC blood test in 8 to 12 weeks to monitor your levels."
            ],
            "doctor_questions": [
                "What specific type and dosage of oral iron supplement do you recommend for my mild anemia?",
                "What dietary adjustments would best support improving my iron storage levels?",
                "Should we schedule the repeat CBC test at 8 weeks or 12 weeks?"
            ]
        }
    },
    "brain_mri": {
        "title": "Brain MRI (Unremarkable Scan)",
        "report_text": """
EXAMINATION: MRI BRAIN WITHOUT CONTRAST

CLINICAL INDICATION: Intermittent tension headaches, no focal neurological deficit.

FINDINGS:
BRAIN PARENCHYMA: Normal signal intensity throughout cerebrum, cerebellum, and brainstem. No acute cerebral infarction, hemorrhage, or mass effect.
VENTRICLES & EXTRA-AXIAL SPACES: Ventricles and sulci are within normal limits for age. No midline shift.
VESSELS & CRANIAL NERVES: Major intracranial vascular flow voids intact. Major cranial nerve complexes intact.
SINUSES & ORBITS: Minimal mucosal thickening in left maxillary sinus, otherwise clear paranasal sinuses. Orbits are unremarkable.

IMPRESSION:
1. Unremarkable brain MRI. No acute intracranial abnormality, hemorrhage, mass effect, or aneurysm.
2. Benign, minimal left maxillary sinus mucosal thickening.
3. Recommendation: Routine clinical follow-up for headache management. No specialized neuro-imaging required.
""",
        "precomputed_summary": {
            "overall_status": {
                "banner_title": "No Concerning Structural Findings Identified",
                "subtitle": "The brain MRI is unremarkable with no acute intracranial abnormality, stroke, hemorrhage, or mass effect. Minimal left maxillary sinus thickening was noted.",
                "status_level": "routine"
            },
            "target_systems": ["Brain Tissue & Vessels", "Sinuses"],
            "findings": [
                {
                    "organ": "Brain Parenchyma & Vessels (Primary Finding)",
                    "simple_explanation": "Unremarkable brain MRI. There is no acute intracranial abnormality, hemorrhage, mass effect, or aneurysm.",
                    "visual_analogy": "100% Normal Signal & Structure",
                    "clinical_drawer": {
                        "exact_impression": "Unremarkable brain MRI. No acute intracranial abnormality, hemorrhage, mass effect, or aneurysm.",
                        "measurements": "None reported (Normal scan)",
                        "pertinent_negatives": ["No acute cerebral infarction", "No hemorrhage", "No mass effect", "No aneurysm", "No midline shift"],
                        "clinical_action": "Routine clinical follow-up for headache management. No specialized neuro-imaging required."
                    }
                },
                {
                    "organ": "Maxillary Sinus (Incidental Finding)",
                    "simple_explanation": "Benign, minimal mucosal thickening in the left maxillary sinus. Paranasal sinuses are otherwise clear.",
                    "visual_analogy": "Minimal Mucosal Thickening",
                    "clinical_drawer": {
                        "exact_impression": "Benign, minimal left maxillary sinus mucosal thickening.",
                        "measurements": "None reported (Minimal)",
                        "pertinent_negatives": ["Otherwise clear paranasal sinuses", "Orbits are unremarkable"],
                        "clinical_action": "Routine clinical follow-up for headache management."
                    }
                }
            ],
            "patient_checklist": [
                "Follow up with your physician for routine clinical headache management as recommended in your report.",
                "No specialized follow-up neuro-imaging is required as stated in your report."
            ],
            "doctor_questions": [
                "Since the MRI found no structural cause for my tension headaches, what clinical strategies do you recommend for headache management?",
                "Does the minimal sinus mucosal thickening noted in the report require any treatment or relate to my symptoms?"
            ]
        }
    }
}

import fitz  # PyMuPDF
import json
import os
import requests

# --- CONFIGURATION ---
PDF_PATH = "Brochure A4-RDC Entrepreunariat-AIRTEL.pdf"
OUTPUT_DIR = "questions_par_page"
GEMINI_API_KEY = "AIzaSyAayNaBCTKcDYhWYMpR5He_7Ru61IMlIyI"  # Remplace par   ta clé réelle
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- FONCTION D'APPEL À GEMINI ---
def generate_questions_from_text(page_text):
    prompt = f"""
Tu es un assistant éducatif. Génère au moins 50 questions à choix multiples de culture générale sur la RDC basées uniquement sur ce texte :

{page_text}

Pour chaque question, retourne un objet JSON avec :
- question
- assertions (4 options)
- reponse (index de la bonne réponse)

Répond uniquement avec un tableau JSON comme :
[
  {{"question": "...", "assertions": ["...", "...", "...", "..."], "reponse": 2}},
  ...
]
"""

    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    if response.status_code == 200:
        try:
            content = response.json()['candidates'][0]['content']['parts'][0]['text']
            print(content)
            # Remove json and ``` characters from content before parsing
            content = content.replace('```json', '').replace('```', '')
            return json.loads(content)
        except Exception as e:
            print("Erreur lors du traitement de la réponse Gemini:", e)
            return []
    else:
        print("Erreur API Gemini:", response.status_code, response.text)
        return []

# --- LECTURE DU PDF ET GÉNÉRATION DES FICHIERS JSON ---
def process_pdf(pdf_path):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        if len(text.strip()) < 100:
            continue  # ignore empty or irrelevant pages

        print(f"\nTraitement de la page {i+1}...")
        questions = generate_questions_from_text(text)
        if questions:
            with open(os.path.join(OUTPUT_DIR, f"page_{i+1}.json"), "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
        else:
            print(f"Aucune question générée pour la page {i+1}.")

    print("\nTraitement terminé.")

# --- EXÉCUTION PRINCIPALE ---
if __name__ == "__main__":
    process_pdf(PDF_PATH)
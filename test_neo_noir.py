import google.generativeai as genai
import os

# Configuration de l'API avec la nouvelle clé
api_key = "AIzaSyDjBiuiueb4_nSHpMD8M-8c-hXmGuLOc9k"
genai.configure(api_key=api_key)

# Configuration du modèle
generation_config = {
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

# Utilisation de gemini-1.5-flash qui est le modèle standard actuel
model = genai.GenerativeModel(
  model_name="gemini-pro",
  generation_config=generation_config,
)

film_title = "L.A. Confidential (Curtis Hanson, 1997)"

prompts = [
    f"""Vous êtes un expert en cinéma Neo-Noir des années 80 et 90.
    Analysez comment les codes visuels du noir classique sont réinterprétés dans : {film_title}
    
    Concentrez-vous sur :
    - L'utilisation de la couleur et des contrastes modernes
    - La représentation de la ville et de la corruption urbaine
    - Le style visuel (esthétique léchée, clair-obscur moderne)""",
    
    f"""En tant qu'analyste du Neo-Noir, identifiez la subversion des archétypes classiques dans : {film_title}
    
    Examinez :
    - L'évolution de la femme fatale
    - La moralité ambiguë des protagonistes
    - L'influence du contexte social et politique des années 80/90
    - La violence et le cynisme contemporain"""
]

print(f"--- Analyse pour le film : {film_title} ---\n")

for i, prompt in enumerate(prompts):
    print(f"--- Prompt {i+1} ---")
    try:
        response = model.generate_content(prompt)
        print(response.text)
    except Exception as e:
        print(f"Erreur : {e}")
    print("\n" + "="*50 + "\n")

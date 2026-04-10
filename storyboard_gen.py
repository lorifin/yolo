import google.generativeai as genai
import os
import json

# Configuration Gemini
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def generate_storyboard_prompt(script_text):
    """
    Transforme un texte de script en un prompt visuel détaillé pour storyboarder.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    En tant que Directeur Artistique expert en Néo-Noir, transforme l'extrait de script suivant en un PROMPT IMAGE ultra-détaillé pour un storyboard. 
    
    TEXTE DU SCRIPT :
    "{script_text}"
    
    DIRECTIVES VISUELLES :
    - Style : Néo-Noir des années 80 (esthétique à la Blade Runner / Seven).
    - Éclairage : Chiaroscuro intense, ombres découpées, sources de lumière néon (bleu électrique, rose magenta, jaune sodium).
    - Caméra : Angle cinématographique (ex: Dutch angle, Low angle), focale anamorphique, grain de film 35mm.
    - Atmosphère : Pluie battante, asphalte mouillé, fumée de cigarette volumétrique. 
    
    FORMAT DE RÉPONSE :
    Donne uniquement le prompt en ANGLAIS, optimisé pour Stable Diffusion / Midjourney.
    Commence par "Cinematic storyboard shot, ..."
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Erreur : {e}"

# Exemple d'utilisation pour la démo
if __name__ == "__main__":
    example_script = "JACK (tenant son arme dans l'ombre) : C'est fini, Miller. Le passé vient de te rattraper dans cette impasse."
    
    print("🎬 EXTRAIT DU SCRIPT :")
    print(example_script)
    print("\n🚀 GÉNÉRATION DU PROMPT STORYBOARD (Optimisé IA Image) :")
    
    storyboard_prompt = generate_storyboard_prompt(example_script)
    print("-" * 50)
    print(storyboard_prompt)
    print("-" * 50)
    
    # Sauvegarde pour la présentation
    with open('storyboard_prompt.txt', 'w') as f:
        f.write(storyboard_prompt)
    print("\n✅ Prompt sauvegardé dans 'storyboard_prompt.txt'")

import yaml
import subprocess
import os

# 1. Vos données (pourraient venir d'un CSV, d'une API, ou d'une DB)
films_to_test = [
    {"title": "L.A. Confidential (1997)", "keywords": ["Bud White", "corruption"]},
    {"title": "Memento (2000)", "keywords": ["mémoire", "polaire", "tatouage"]},
    {"title": "Mulholland Drive (2001)", "keywords": ["rêve", "Hollywood", "illusion"]},
    {"title": "Sin City (2005)", "keywords": ["contraste", "rouge", "Frank Miller"]},
    {"title": "Nightcrawler (2014)", "keywords": ["médias", "vidéo", "cynisme"]}
]

# 2. Définition du Prompt "Template" (Le prompt amélioré)
expert_prompt = """
Tu es un analyste expert du Néo-Noir.
Sujet : {{film_title}}

Analyse la scène d'ouverture ou l'ambiance générale sous l'angle de la "Fatalité".
Comment l'environnement visuel condamne-t-il les personnages dès le début ?

Sois concis (max 150 mots) mais incisif.
"""

# 3. Construction de la structure YAML pour promptfoo
config = {
    "description": "Analyse Automatisée Néo-Noir via Python Script",
    "prompts": [expert_prompt],
    "providers": [{
        "id": "google:gemini-2.5-flash",
        "config": {
            "apiKey": "AIzaSyDjBiuiueb4_nSHpMD8M-8c-hXmGuLOc9k",
            "temperature": 0.3
        }
    }],
    "tests": []
}

# 4. Génération dynamique des tests
for film in films_to_test:
    test_case = {
        "vars": {
            "film_title": film["title"]
        },
        "assert": [
            {
                "type": "contains-any",
                "value": film["keywords"]
            },
            {
                # On s'assure que le modèle ne "bavarde" pas trop
                "type": "javascript",
                "value": "output.length < 1500" 
            }
        ]
    }
    config["tests"].append(test_case)

# 5. Écriture du fichier de config temporaire
with open("dynamic_config.yaml", "w") as f:
    yaml.dump(config, f, allow_unicode=True)

print("✅ Fichier 'dynamic_config.yaml' généré avec succès.")
print(f"✅ {len(films_to_test)} films prêts à être testés.")

# 6. Exécution automatique de promptfoo (Optionnel, vous pouvez le lancer à la main)
print("🚀 Lancement de promptfoo...")
subprocess.run(["npx", "promptfoo", "eval", "-c", "dynamic_config.yaml", "--no-cache"])

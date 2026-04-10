import json

with open('results.json', 'r') as f:
    data = json.load(f)

print("--- ANALYSE DES ÉCHECS ---\n")

for result in data['results']['results']:
    film = result['vars']['film_title']
    if not result['success']:
        print(f"🎬 FILM : {film}")
        print(f"❌ RÉSULTAT : ÉCHEC")
        
        # Afficher la réponse du modèle
        model_output = result['response']['output']
        print(f"\n📝 RÉPONSE DU MODÈLE :\n{model_output[:300]}...\n(tronqué)\n")
        
        # Afficher pourquoi ça a échoué
        print("🔍 RAISON DE L'ÉCHEC :")
        for test in result['gradingResult']['componentResults']:
            if not test['pass']:
                print(f"  - Attendu : {test['assertion']['type']} -> {test['assertion']['value']}")
                print(f"  - Trouvé : {test['reason']}")
        
        print("\n" + "-"*50 + "\n")
    else:
        print(f"🎬 FILM : {film} -> ✅ SUCCÈS")

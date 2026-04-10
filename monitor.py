import subprocess
from classifier import simple_classifier

def run_auto_test():
    phrase = "Le code de cette <b>IA</b> est vraiment <u>génial</u> et efficace, même si j'ai trouvé un petit <i>bug</i> dans le script."
    
    # Test du sentiment
    resultat = simple_classifier(phrase)
    
    print(f"--- RAPPORT D'AUTOMATION ---")
    print(f"Phrase testée : {phrase}")
    print(f"Verdict ML : {resultat}")
    
    if "Positif" in resultat:
        print("✅ TEST RÉUSSI : Le système détecte bien l'intention positive.")
    else:
        print("❌ TEST ÉCHOUÉ : Le modèle manque de précision.")

if __name__ == "__main__":
    run_auto_test()

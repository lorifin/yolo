import os
import sys

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"ERREUR: Le fichier {filepath} n'existe pas.")
        return False
    return True

def main():
    files_to_check = [
        'formation/index.html',
        'formation/style.css',
        'formation/script.js',
        'formation/a_propos.html'
    ]
    
    all_passed = True
    for file in files_to_check:
        if not check_file_exists(file):
            all_passed = False
            
    if all_passed:
        print("Tous les tests sont passés !")
        sys.exit(0)
    else:
        print("Certains tests ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()

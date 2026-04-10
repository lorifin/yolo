import re
import os

def count_words_in_html(file_path):
    """
    Simule une étape de pré-traitement ML :
    Lit un fichier HTML, nettoie les balises et compte les mots.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Suppression basique des balises HTML avec une regex (Feature Extraction)
        # On remplace les balises par un espace pour éviter de coller les mots
        text_only = re.sub('<[^<]+?>', ' ', content)
        
        # Nettoyage des espaces multiples
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        
        words = text_only.split()
        return len(words)
    except FileNotFoundError:
        return 0

def main():
    directory = 'formation'
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    
    print(f"{'Fichier':<20} | {'Nombre de mots (Feature)':<25}")
    print("-" * 50)
    
    total_words = 0
    for filename in html_files:
        path = os.path.join(directory, filename)
        count = count_words_in_html(path)
        print(f"{filename:<20} | {count:<25}")
        total_words += count
        
    print("-" * 50)
    print(f"{'TOTAL':<20} | {total_words:<25}")

if __name__ == "__main__":
    main()

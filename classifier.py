import re

def simple_classifier(text):
    # Dictionnaires
    pos_words = ['génial', 'super', 'excellent', 'rapide', 'efficace', 'bravo', 'top', 'magnifique', 'élégante', 'précieuse']
    neg_words = ['lent', 'mauvais', 'erreur', 'difficile', 'problème', 'nul', 'bug', 'horrible', 'déteste']
    intensifiers = ['très', 'trop', 'terriblement', 'vraiment']
    negations = ['pas', 'ne', 'non', 'n'] # Ajout de 'n' pour "n'est"
    
    text = text.lower()
    
    # Règle 2 : Contraste avec 'mais'
    # On sépare la phrase en segments
    segments = text.split('mais')
    
    total_score = 0
    
    for segment_index, segment in enumerate(segments):
        # Si on est après un "mais" (index > 0), on applique le multiplicateur de contraste
        contrast_multiplier = 1.5 if segment_index > 0 else 1.0
        
        words = re.findall(r'\b\w+\b', segment)
        
        for i, word in enumerate(words):
            word_score = 0
            
            # Détection de la polarité de base
            if word in pos_words:
                word_score = 1
            elif word in neg_words:
                word_score = -1
                
            if word_score != 0:
                # Vérification du contexte (fenêtre de 2 mots avant)
                start_idx = max(0, i - 2)
                context = words[start_idx:i]
                
                # Règle 1 : Gestion de la négation (inverse le score)
                # On vérifie si un mot de négation est présent juste avant
                is_negated = any(n in context for n in negations)
                if is_negated:
                    word_score *= -1
                
                # Règle 3 : Gestion de l'intensité (multiplie par 2)
                is_intensified = any(inten in context for inten in intensifiers)
                if is_intensified:
                    word_score *= 2.0
                
                # Application du multiplicateur de contraste (mais)
                word_score *= contrast_multiplier
                
                total_score += word_score
        
    if total_score > 0: return "Positif 😊"
    elif total_score < 0: return "Négatif 😡"
    else: return "Neutre 😐"

# Test du modèle
if __name__ == "__main__":
    sample = "L'interface est élégante mais le temps de réponse est horrible."
    print(f"Analyse : {sample}")
    print(f"Résultat ML : {simple_classifier(sample)}")

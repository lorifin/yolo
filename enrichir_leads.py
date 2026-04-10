# /// script
# dependencies = [
#   "pandas",
#   "requests",
# ]
# ///

import pandas as pd
import json
import os
import requests
import time
import re

# --- CONFIGURATION ---
HUNTER_API_KEY = "ab7ec36e073d19726366aa1eb0abff9dd340a1d5"
# ---------------------

def clean_company_name(name):
    """Nettoie le nom de l'entreprise pour deviner le domaine."""
    if not name or pd.isna(name): return ""
    name = re.sub(r'\b(SAS|SARL|SA|GROUP|GROUPE|FRANCE|OFFICIAL|AFPA|CNED)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower().strip()
    return name

def guess_professional_email(first_name, last_name, company_name):
    """Génère un email probable (pattern standard français)."""
    f = first_name.lower().replace(' ', '').strip()
    l = last_name.lower().replace(' ', '').strip()
    domain = clean_company_name(company_name)
    if not f or not l or not domain: return None
    # Pattern le plus courant en France : p.nom@entreprise.fr
    return f"{f[0]}.{l}@{domain}.fr"

def get_email_from_hunter(first_name, last_name, company_name):
    """Interroge l'API Hunter.io pour trouver l'email vérifié."""
    if not HUNTER_API_KEY:
        return None
    
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "first_name": first_name,
        "last_name": last_name,
        "company": company_name,
        "api_key": HUNTER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', {})
            email = data.get('email')
            score = data.get('score', 0)
            if email and score > 70:
                print(f"  ✨ Hunter trouvé : {email} (Score: {score}%)")
                return email, "Hunter.io"
        elif response.status_code == 429:
            print("  ⚠️ Plus de crédits Hunter.io. Passage en mode 'Devinette'...")
            return None, "Out of Credits"
    except Exception as e:
        print(f"  ❌ Erreur Hunter.io : {e}")
    
    return None, "Not Found"

def enrich_from_csv(csv_path, output_json='leads_valides.json'):
    print(f"🚀 Lecture de l'export : {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
    except:
        df = pd.read_csv(csv_path, sep=';')

    col_mapping = {'fullName': 'nom_complet', 'firstName': 'prenom', 'lastName': 'nom', 
                   'companyName': 'entreprise', 'currentCompany': 'entreprise', 'jobTitle': 'poste'}
    df = df.rename(columns=lambda x: col_mapping.get(x, x))

    if os.path.exists(output_json):
        with open(output_json, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except: data = {"leads": []}
            existing_emails = {l['email'] for l in data.get('leads', [])}
    else:
        data = {"leads": []}
        existing_emails = set()

    added_count = 0
    
    for _, row in df.iterrows():
        prenom = str(row.get('prenom', '')).strip()
        nom = str(row.get('nom', '')).strip()
        if not prenom or prenom == 'nan':
            full = str(row.get('nom_complet', ''))
            if ' ' in full:
                prenom, nom = full.split(' ', 1)
            else: nom = full

        entreprise = str(row.get('entreprise', '')).strip()
        if not entreprise or entreprise == 'nan': continue

        print(f"🔍 Traitement de {prenom} {nom} ({entreprise})...")
        
        # 1. Tentative Hunter
        email, source = get_email_from_hunter(prenom, nom, entreprise)
        
        # 2. Repli Devinette si Hunter échoue
        if not email:
            email = guess_professional_email(prenom, nom, entreprise)
            source = "Guess (Pattern)"
            if email: print(f"  💡 Devinette : {email}")

        if email and email not in existing_emails:
            new_lead = {
                "nom": f"{prenom} {nom}".strip(),
                "entreprise": entreprise,
                "poste": str(row.get('poste', 'Directeur Innovation')),
                "email": email,
                "score": 70 if source == "Guess (Pattern)" else 95,
                "source": source
            }
            if 'leads' not in data: data['leads'] = []
            data['leads'].append(new_lead)
            existing_emails.add(email)
            added_count += 1

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Terminé ! {added_count} leads ajoutés à {output_json}.")

if __name__ == "__main__":
    path = "resultats_phantombuster.csv"
    if os.path.exists(path):
        enrich_from_csv(path)
    else:
        print(f"❌ Fichier {path} non trouvé.")

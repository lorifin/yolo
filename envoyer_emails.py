import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "stephane.krebs8@gmail.com"
SENDER_PASSWORD = "xcyj rfcx utsq cnko" 
# ---------------------

def envoyer_email(destinataire, prenom, entreprise):
    msg = MIMEMultipart()
    msg['From'] = f"Stéphane KREBS <{SENDER_EMAIL}>"
    msg['To'] = destinataire
    msg['Subject'] = f"Opportunité de formation en IA pour {entreprise}"

    corps = f"""Bonjour {prenom},

Expert IA depuis 10 ans, je vous contacte pour vous présenter nos modules d'expertise en intelligence artificielle (GenAI, Edge AI, Automatisation via n8n/Make).

Étant donné votre rôle chez {entreprise}, je pense que ces formations pourraient enrichir vos programmes et répondre aux besoins croissants de vos apprenants sur les technologies de pointe.

Seriez-vous disponible pour en discuter plus en détail ?

Cordialement,

Stéphane KREBS
"""
    msg.attach(MIMEText(corps, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"  ❌ Erreur lors de l'envoi à {destinataire} : {e}")
        return False

def lancer_campagne():
    with open('leads_valides.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # On cible les 10 derniers leads ajoutés (les nouveaux de Phantombuster/Hunter)
    leads = [l for l in data['leads'] if l.get('source') in ['Hunter.io', 'Guess (Pattern)']]
    
    print(f"🚀 Lancement de l'envoi pour {len(leads)} leads...")
    
    envoyes = 0
    for lead in leads:
        nom_complet = lead['nom']
        prenom = nom_complet.split(' ')[0].capitalize()
        email = lead['email']
        entreprise = lead['entreprise']

        print(f"📧 Envoi à {prenom} ({email}) chez {entreprise}...")
        
        if envoyer_email(email, prenom, entreprise):
            print("  ✅ Envoyé !")
            envoyes += 1
            time.sleep(3) # Pause de sécurité légèrement augmentée
        
    print(f"\n✨ Campagne terminée : {envoyes} emails envoyés avec succès.")

if __name__ == "__main__":
    lancer_campagne()

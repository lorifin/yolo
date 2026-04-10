import cv2
from ultralytics import YOLO
import os
from openai import OpenAI
import json
import threading
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import logging

# Ensure execution context is the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder=None)
CORS(app)

# --- Routes Explicites ---

@app.route('/')
def index():
    print("📢 Requête reçue sur / (index)")
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "Fichier index.html introuvable", 404

@app.route('/style.css')
def style():
    if os.path.exists('style.css'):
        response = make_response(send_file('style.css'))
        response.headers['Content-Type'] = 'text/css'
        return response
    return "", 404

@app.route('/script.js')
def script():
    if os.path.exists('script.js'):
        response = make_response(send_file('script.js'))
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return "", 404

@app.route('/data.js')
def data_js():
    if os.path.exists('data.js'):
        response = make_response(send_file('data.js'))
        response.headers['Content-Type'] = 'application/javascript'
        # Désactiver le cache pour les données dynamiques
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "var detectionData = {};", 200

@app.route('/live.jpg')
def live_jpg():
    if os.path.exists('live.jpg'):
        response = make_response(send_file('live.jpg'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "", 404

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    if os.path.exists(f'assets/{filename}'):
        return send_file(f'assets/{filename}')
    return "", 404

# --- API ---

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    try:
        data = request.json
        text = data.get('text', '')
        with open('input_sentiment.txt', 'w') as f:
            f.write(text)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error"}), 500

def run_flask():
    print("🚀 DASHBOARD LIVE : http://127.0.0.1:5001", flush=True)
    # Host 0.0.0.0 permet l'accès depuis n'importe quelle interface réseau
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

# Démarrage du serveur dans un thread séparé
t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

# Configuration OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
    print("ℹ️  Using default API key. Set OPENAI_API_KEY to use your own.")
else:
    print("✅ Using OPENAI_API_KEY from environment.")

client = OpenAI(api_key=api_key)

def fusion_yolo_script(objets_yolo, scenario_text):
    """
    Fusionne la détection d'objets YOLO et une amorce de scénario via GPT-4o.
    Style: Néo-Noir hybride (Blade Runner / Drive).
    """
    if not scenario_text:
        return None

    # Détermination dynamique du style (Bascule Drive si 'car' ou 'steering_wheel' est détecté)
    is_driving = any(obj in ['car', 'steering_wheel', 'truck'] for obj in objets_yolo)
    
    if is_driving:
        style_name = "DRIVE (Minimaliste/Tendu)"
        system_prompt = (
            "Agis comme le moteur d'intelligence d'un film Néo-Noir stylisé type 'Drive'. "
            "Ton univers est silencieux, tendu, baigné de lumières néons (rose, bleu) et d'une violence latente. "
            "Les objets sont des extensions des personnages. Utilise-les pour ralentir le temps ou accentuer le silence."
        )
    else:
        style_name = "BLADE RUNNER (Cyberpunk/Mélancolique)"
        system_prompt = (
            "Agis comme le moteur d'intelligence d'un film Cyberpunk Néo-Noir style 'Blade Runner'. "
            "Ton univers est fait de pluie incessante, néons saturés, décadence urbaine et technologie omniprésente. "
            "Fusionne les objets et le script pour créer une atmosphère oppressante et artificielle. "
            "Insiste sur la lumière, la texture et la mélancolie."
        )

    # Prompt Utilisateur
    user_prompt = f"""
    📥 DONNÉES :
    Objets YOLO : {', '.join(objets_yolo) if objets_yolo else "Aucun"}
    Extrait Script : "{scenario_text}"

    ⚙️ MISSION :
    Génère une réponse JSON (STRICT) avec ces clés :
    {{
        "sentiment": "Emotion dominante (Focus: {style_name})",
        "analyse_yolo": "Impact des objets sur l'ambiance",
        "script_enrichi": "Texte narratif immersif (style littéraire)",
        "verdict": "Prompt visuel ultra-détaillé pour Stable Diffusion (Style: {style_name})"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Erreur OpenAI : {e}")
        # Fallback JSON en cas d'erreur
        return {
            "sentiment": "Erreur technique",
            "analyse_yolo": "Impossible d'analyser les objets.",
            "script_enrichi": "Le système a rencontré une erreur. La connexion neuronale est instable.",
            "verdict": "Ecran statique, bruit numérique, glitch art, noir et blanc"
        }

# Initialisation Vision
model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)
current_verdict = "Prêt pour l'analyse..."

print("🎥 SYSTÈME PRÊT : Lancement de la vision...")

try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Détection d'objets YOLO
        results = model.predict(source=frame, conf=0.3, verbose=False)
        annotated_frame = results[0].plot()

        detection_dict = {}
        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            detection_dict[label] = detection_dict.get(label, 0) + 1
        
        # Récupération de la liste des objets pour le script
        current_objects_list = list(detection_dict.keys())

        # 2. Vérification des requêtes d'analyse texte
        if os.path.exists('input_sentiment.txt'):
            with open('input_sentiment.txt', 'r') as f:
                texte_a_analyser = f.read()
            
            if texte_a_analyser.strip():
                print(f"🎬 ANALYSE EN COURS...")
                # Appel de la nouvelle fonction fusion (renvoie un dict)
                resultat = fusion_yolo_script(current_objects_list, texte_a_analyser)
                
                # Sécurité et Extraction des données
                if resultat and isinstance(resultat, dict) and 'error' not in resultat:
                    sentiment = resultat.get('sentiment', 'Neutre')
                    analyse = resultat.get('analyse_yolo', '')
                    script = resultat.get('script_enrichi', '')
                    verdict = resultat.get('verdict', '')
                    
                    # Mise à jour du verdict courant (formaté pour le Dashboard)
                    current_verdict = json.dumps(resultat, ensure_ascii=False, indent=2)
                    print(f"✅ RESULTAT EXTRAIT : {sentiment} | {analyse[:50]}...")
                else:
                    current_verdict = "Erreur de traitement API"
                    print("❌ Échec de l'analyse ou format invalide")
            
            os.remove('input_sentiment.txt')
        
        detection_dict['sentiment_verdict'] = current_verdict

        # 3. Sauvegardes pour le Dashboard
        cv2.imwrite('live.jpg', annotated_frame)
        
        # Nettoyage sécurisé pour le JavaScript
        # On échappe les guillemets doubles pour éviter de casser la variable JS
        clean_v = current_verdict.replace('"', '\\"').replace('\n', ' ')
        
        with open('data.js', 'w') as f:
            f.write(f"var detectionData = {json.dumps(detection_dict)};\n")
            f.write(f'var apiVerdict = "{clean_v}";')

except KeyboardInterrupt:
    print("\nArrêt propre du système.")
finally:
    cap.release()
    cv2.destroyAllWindows()
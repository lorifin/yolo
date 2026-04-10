import cv2
from ultralytics import YOLO
import os
import google.generativeai as genai
import json
import threading
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import logging

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
    print("🚀 DASHBOARD LIVE : http://127.0.0.1:5001")
    # Host 0.0.0.0 permet l'accès depuis n'importe quelle interface réseau
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

# Démarrage du serveur dans un thread séparé
t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

# Configuration Gemini
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Utilisation forcée de la version stable v1beta pour garantir la compatibilité
def analyze_text_with_gemini(text):
    try:
        # On cherche le premier modèle disponible qui accepte la génération de contenu
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            return "Aucun modèle trouvé"
            
        # On choisit le premier modèle de la liste (souvent gemini-pro ou flash)
        selected_model = available_models[0]
        print(f"📡 Utilisation du modèle : {selected_model}")
        
        model_gemini = genai.GenerativeModel(selected_model)
        prompt = (
            "Tu es un expert en cinéma noir. Analyse la noirceur de ce script. "
            "Verdict obligatoire : NOIR, GRIS ou CLAIR. "
            f"Texte : {text}"
        )
        response = model_gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erreur système : {e}")
        return "Erreur d'analyse"

# Initialisation Vision
model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)
current_verdict = "Prêt pour l'analyse..."

print("🎥 SYSTÈME PRÊT : Lancement de la vision...")

try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Vérification des requêtes d'analyse texte
        if os.path.exists('input_sentiment.txt'):
            with open('input_sentiment.txt', 'r') as f:
                texte_a_analyser = f.read()
            
            if texte_a_analyser.strip():
                print(f"🎬 ANALYSE EN COURS...")
                current_verdict = analyze_text_with_gemini(texte_a_analyser)
                print(f"✅ RESULTAT : {current_verdict}")
            
            os.remove('input_sentiment.txt')

        # 2. Détection d'objets YOLO
        results = model.predict(source=frame, conf=0.3, verbose=False)
        annotated_frame = results[0].plot()

        detection_dict = {}
        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            detection_dict[label] = detection_dict.get(label, 0) + 1
        
        detection_dict['sentiment_verdict'] = current_verdict

        # 3. Sauvegardes pour le Dashboard
        cv2.imwrite('live.jpg', annotated_frame)
        
        # Nettoyage sécurisé pour le JavaScript
        clean_v = current_verdict.replace('"', "'").replace('\n', ' ')
        
        with open('data.js', 'w') as f:
            f.write(f"var detectionData = {json.dumps(detection_dict)};\n")
            f.write(f'var apiVerdict = "{clean_v}";')

except KeyboardInterrupt:
    print("\nArrêt propre du système.")
finally:
    cap.release()
    cv2.destroyAllWindows()
import cv2
from ultralytics import YOLO
import os
import google.generativeai as genai
import json
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Désactiver les logs Flask trop verbeux
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder='formation')
CORS(app) # Autorise la communication avec le Dashboard

@app.route('/')
def index():
    return send_from_directory('formation', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('formation', path)

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    try:
        data = request.json
        text = data.get('text', '')
        with open('formation/input_sentiment.txt', 'w') as f:
            f.write(text)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error"}), 500

def run_flask():
    print("🚀 DASHBOARD LIVE : http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# Démarrage du serveur dans un thread séparé
t = threading.Thread(target=run_flask)
t.daemon = True
t.start()

# Configuration Gemini
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_text_with_gemini(text):
    try:
        # Utilisation de gemini-pro pour éviter l'erreur 404
        model_gemini = genai.GenerativeModel('gemini-pro')
        prompt = (
            "Tu es un expert en cinéma noir. Analyse la noirceur de ce script. "
            "Verdict obligatoire : NOIR, GRIS ou CLAIR. "
            f"Texte : {text}"
        )
        response = model_gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erreur Gemini: {e}")
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
        if os.path.exists('formation/input_sentiment.txt'):
            with open('formation/input_sentiment.txt', 'r') as f:
                texte_a_analyser = f.read()
            
            if texte_a_analyser.strip():
                print(f"🎬 ANALYSE EN COURS...")
                current_verdict = analyze_text_with_gemini(texte_a_analyser)
                print(f"✅ RESULTAT : {current_verdict}")
            
            os.remove('formation/input_sentiment.txt')

        # 2. Détection d'objets YOLO
        results = model.predict(source=frame, conf=0.3, verbose=False)
        annotated_frame = results[0].plot()

        detection_dict = {}
        for box in results[0].boxes:
            label = model.names[int(box.cls[0])]
            detection_dict[label] = detection_dict.get(label, 0) + 1
        
        detection_dict['sentiment_verdict'] = current_verdict

        # 3. Sauvegardes pour le Dashboard
        cv2.imwrite('formation/live.jpg', annotated_frame)
        
        # Nettoyage sécurisé pour le JavaScript
        clean_v = current_verdict.replace('"', "'").replace('\n', ' ')
        
        with open('formation/data.js', 'w') as f:
            f.write(f"var detectionData = {json.dumps(detection_dict)};\n")
            f.write(f'var apiVerdict = "{clean_v}";')

except KeyboardInterrupt:
    print("\nArrêt propre du système.")
finally:
    cap.release()
    cv2.destroyAllWindows()
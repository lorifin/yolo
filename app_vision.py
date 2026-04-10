import cv2
from ultralytics import YOLO
import time
import os
import json

# Configuration
output_file = 'formation/live.jpg'
json_file = 'formation/vision_results.json'
model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)

print("------------------------------------------------")
print("APPLICATION VISION (MODE FICHIER + JSON)")
print(f"Images : {output_file}")
print(f"Données : {json_file}")
print("------------------------------------------------")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur lecture webcam")
            break
        
        # Lecture dynamique de la confiance
        conf_threshold = 0.5
        try:
            if os.path.exists('formation/confidence.txt'):
                with open('formation/confidence.txt', 'r') as f:
                    conf_threshold = float(f.read().strip())
        except:
            pass

        # Inférence YOLO avec seuil dynamique
        results = model(frame, conf=conf_threshold, verbose=False)
        result = results[0]
        annotated_frame = result.plot()
        
        # 1. Sauvegarde Image (Atomique)
        cv2.putText(annotated_frame, "MODE FICHIER + JSON", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        tmp_img = output_file + '.tmp.jpg'
        cv2.imwrite(tmp_img, annotated_frame)
        os.replace(tmp_img, output_file)
        
        # 2. Comptage des objets
        counts = {}
        for box in result.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            counts[label] = counts.get(label, 0) + 1
            
        # 3. Sauvegarde JSON (Atomique)
        data = {
            "timestamp": time.time(),
            "objects": counts
        }
        tmp_json = json_file + '.tmp'
        with open(tmp_json, 'w') as f:
            json.dump(data, f)
        os.replace(tmp_json, json_file)
        
        # Pause
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")
finally:
    cap.release()
    if os.path.exists(output_file):
        os.remove(output_file)
    print("Ressources libérées.")

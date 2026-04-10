# YOLO Vision & Smart Prospector

Projet IA combinant deux modules :
- **Vision YOLO** : détection d'objets en temps réel via YOLOv8 + analyse GPT-4 Vision
- **Smart Prospector** : application de gestion de leads avec scoring IA

Développé par **Stéphane Krebs** — Expert IA Freelance

---

## Architecture

```
yolo/
├── vision_final.py       # API Flask — détection YOLO + analyse Vision
├── app.py                # Smart Prospector — gestion leads
├── app_vision.py         # Interface vision alternative
├── monitor.py            # Monitoring temps réel
├── index.html            # Frontend web
├── style.css             # Styles dark theme
├── script.js             # Logique frontend
├── yolov8n.pt            # Modèle YOLO pré-entraîné
├── config.json           # Configuration (seuil de confiance)
├── Dockerfile            # Image Docker
├── docker-compose.yml    # Stack complète
└── pyproject.toml        # Dépendances Python
```

---

## Installation

### Avec Conda (recommandé)

```bash
conda create -n yolo-env python=3.11 -y
conda activate yolo-env
pip install pandas requests flask ultralytics opencv-python-headless pypdf python-dotenv openai flask-cors
```

### Variables d'environnement

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY=sk-...
```

---

## Lancement

### Module Vision YOLO

```bash
conda activate yolo-env
python vision_final.py
```

Accès : **http://localhost:5000**

### Smart Prospector

```bash
conda activate yolo-env
python app.py
```

Accès : **http://localhost:5001**

---

## Docker

```bash
docker-compose up --build
```

---

## Fonctionnalités

### Vision YOLO
- Détection d'objets en temps réel (webcam ou image)
- Analyse contextuelle via GPT-4 Vision
- Seuil de confiance configurable (`config.json`)
- Interface web dark mode

### Smart Prospector
- Gestion de leads avec scoring IA
- Intégration n8n via webhook
- Enrichissement automatique des leads
- Dark mode Bootstrap

---

## Technologies

| Composant | Technologie |
|-----------|-------------|
| Détection | YOLOv8 (Ultralytics) |
| Vision IA | GPT-4 Vision (OpenAI) |
| Backend | Flask |
| Frontend | HTML/CSS/JS dark theme |
| Container | Docker |

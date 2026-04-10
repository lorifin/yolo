# Utiliser Python 3.11 comme base
FROM python:3.11-slim

# Éviter les questions interactives de l'installeur
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système pour OpenCV et Vision
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml . 
# (On utilisera uv pour la rapidité)
RUN pip install uv && uv pip install --system pandas requests flask ultralytics opencv-python-headless pypdf python-dotenv

# Copier le reste de l'application
COPY . .

# Exposer les ports pour le serveur Flask et l'interface
EXPOSE 8081

# Lancer le serveur par défaut
CMD ["python", "app.py"]

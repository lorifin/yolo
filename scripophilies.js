document.addEventListener('DOMContentLoaded', () => {
    
    // === PARTIE 1 : ANALYSE DE SENTIMENT (NLP) ===
    const btnImprove = document.getElementById('btn-improve');
    const suggestionsArea = document.getElementById('suggestions-area');
    const modelSuggestions = document.getElementById('model-suggestions');
    const xaiExplanation = document.getElementById('xai-explanation');

    if (btnImprove) {
        btnImprove.addEventListener('click', () => {
            suggestionsArea.style.display = 'block';
            console.log("Section Sentiment activée");
            // Ajoute ici ta logique spécifique pour le texte si besoin
        });
    }

    // === PARTIE 2 : IA VISION (YOLOv8) ===
    const videoImg = document.getElementById('camera-stream');
    const btnStart = document.getElementById('btn-start-stream');
    const btnStop = document.getElementById('btn-stop-stream');
    const btnAlarm = document.getElementById('btn-alarm');
    const alarmAlert = document.getElementById('alarm-alert');
    const statusLed = document.getElementById('status-led');

    let isRunning = false;
    let alarmActive = false;

    // Démarrer le flux
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            isRunning = true;
            if (statusLed) statusLed.style.color = "#2ecc71"; 
            console.log("Vision démarrée");
        });
    }

    // Arrêter le flux
    if (btnStop) {
        btnStop.addEventListener('click', () => {
            isRunning = false;
            videoImg.src = ""; 
            if (statusLed) statusLed.style.color = "#e74c3c";
            alarmAlert.style.display = 'none';
        });
    }

    // Activer l'alarme
    if (btnAlarm) {
        btnAlarm.addEventListener('click', () => {
            alarmActive = !alarmActive;
            btnAlarm.textContent = alarmActive ? "🛑 Désactiver l'Alarme" : "🔔 Activer l'Alarme";
            btnAlarm.style.backgroundColor = alarmActive ? "#e74c3c" : "#555";
        });
    }

    // Boucle de rafraîchissement
    setInterval(() => {
        if (!isRunning) return;

        // Mise à jour de l'image
        videoImg.src = 'live.jpg?t=' + Date.now();

        // Lecture de la détection
        fetch('vision_results.json?t=' + Date.now())
            .then(r => r.json())
            .then(data => {
                if (alarmActive && data.person > 0) {
                    if (alarmAlert) alarmAlert.style.display = 'block';
                } else {
                    if (alarmAlert) alarmAlert.style.display = 'none';
                }
            }).catch(() => {});
    }, 200);
});

document.addEventListener('DOMContentLoaded', () => {
    // --- VARIABLES ---
    const videoImg = document.getElementById('camera-stream');
    const btnStart = document.getElementById('btn-start-stream');
    const btnStop = document.getElementById('btn-stop-stream');
    const btnAlarm = document.getElementById('btn-alarm');
    const alarmAlert = document.getElementById('alarm-alert');
    const objectList = document.getElementById('object-list');
    const mlResult = document.getElementById('ml-result');
    
    const btnAnalyze = document.getElementById('btn-analyze-sentiment');
    const sentimentInput = document.getElementById('sentiment-input');
    const sentimentLabel = document.getElementById('sentiment-label');
    const btnImprove = document.getElementById('btn-improve');
    const suggestionsArea = document.getElementById('suggestions-area');

    let isRunning = false;
    let alarmActive = false;

    // --- LOGIQUE VISION & CAMÉRA ---
    btnStart.onclick = () => { isRunning = true; videoImg.style.display = "block"; };
    btnStop.onclick = () => { isRunning = false; videoImg.src = ""; alarmAlert.style.display = 'none'; };
    
    btnAlarm.onclick = () => {
        alarmActive = !alarmActive;
        btnAlarm.textContent = alarmActive ? "🛑 Désactiver Surveillance" : "🔔 Activer Surveillance";
        btnAlarm.style.background = alarmActive ? "#e74c3c" : "#555";
    };

    // --- FEEDBACK & JOURNAL UTILISATEUR ---
    const btnFeedback = document.getElementById('btn-submit-feedback');
    const feedbackInput = document.getElementById('feedback-input');
    const eventLog = document.getElementById('event-log');
    
    // JOURNAL SYSTEME
    const activityLog = document.getElementById('activity-log');
    let lastLogTime = 0;

    if (btnFeedback) {
        btnFeedback.onclick = () => {
            const text = feedbackInput.value.trim();
            if (text) {
                const now = new Date();
                const timeStr = now.toLocaleTimeString();
                
                const li = document.createElement('li');
                li.innerHTML = `<span style="color: #3498db; font-weight:bold;">[${timeStr}]</span> ${text}`;
                li.style.borderLeft = "4px solid #3498db"; 
                
                if (eventLog.children.length > 0 && eventLog.children[0].textContent.includes("Aucun événement")) {
                    eventLog.innerHTML = "";
                }
                
                eventLog.appendChild(li);
                feedbackInput.value = ""; 
            }
        };
    }

    // --- LOGIQUE NLP (SENTIMENT) ---
    if (btnAnalyze) {
        btnAnalyze.onclick = () => {
            const textValue = sentimentInput.value; 
            if (!textValue.trim()) return;
            
            sentimentLabel.textContent = "Transmission...";
            sentimentLabel.style.color = "#ccc";
            
            // Envoi au backend Python (URL absolue demandée)
            fetch('http://127.0.0.1:5001/analyze_text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: textValue })
            })
            .then(response => {
                console.log("Envoi réussi");
                sentimentLabel.textContent = "Analyse en cours...";
            })
            .catch(err => {
                console.error("Erreur détectée:", err);
                sentimentLabel.textContent = "Erreur de connexion";
            });
        };
    }

    if (btnImprove) {
        btnImprove.onclick = () => {
            suggestionsArea.style.display = suggestionsArea.style.display === 'none' ? 'block' : 'none';
        };
    }

    // --- SLIDER CONFIANCE ---
    const confSlider = document.getElementById('conf-threshold');
    const confValue = document.getElementById('conf-value');

    if (confSlider && confValue) {
        confSlider.addEventListener('input', () => {
            const val = parseFloat(confSlider.value).toFixed(2); // Format 0.50
            confValue.textContent = val;
            
            fetch('/set_confidence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ confidence: val })
            }).catch(err => console.log("Erreur API:", err));
        });
    }

    // --- BOUCLE DE MISE À JOUR (Toutes les 200ms) ---
    setInterval(() => {
        if (!isRunning) return;

        // Mise à jour image
        videoImg.src = 'live.jpg?t=' + Date.now();

        // Mise à jour objets (Multi-détection)
        if (typeof detectionData !== 'undefined') {
            objectList.innerHTML = ""; // On vide pour reconstruire
            let personFound = false;
            let foundAny = false;

            // Boucle dynamique sur toutes les clés (person, cell phone, etc.)
            for (const [label, count] of Object.entries(detectionData)) {
                // On ignore la clé 'sentiment_verdict' pour la liste d'objets
                if (label === 'sentiment_verdict') continue;

                if (count > 0) {
                    const li = document.createElement('li');
                    li.innerHTML = `<b>${label.toUpperCase()}</b> : ${count}`;
                    objectList.appendChild(li);
                    foundAny = true;
                    if (label === 'person') personFound = true;
                }
            }
            if (!foundAny) objectList.innerHTML = "<li style='color: #777;'>Rien à signaler</li>";

            // MISE À JOUR DU SENTIMENT (FORCEE VIA VARIABLE GLOBALE)
            const currentVerdict = (typeof apiVerdict !== 'undefined' && apiVerdict) ? apiVerdict : detectionData.sentiment_verdict;

            if (currentVerdict && currentVerdict !== "Prêt pour l'analyse...") {
                // On affiche la totalité du texte (accepte les longs textes)
                document.getElementById('xai-explanation').innerText = currentVerdict;
                
                // Style dynamique "Noir"
                if (currentVerdict.toUpperCase().includes("NOIR") || currentVerdict.toUpperCase().includes("CYNIQUE")) {
                    sentimentLabel.textContent = "VERDICT : NOIR 💀";
                    sentimentLabel.style.color = "#e74c3c"; // Rouge
                    document.body.style.border = "4px solid #e74c3c"; // Alerte visuelle
                } else {
                    sentimentLabel.textContent = "VERDICT : REÇU ✅";
                    sentimentLabel.style.color = "#4ecca3";
                    document.body.style.border = "none";
                }
            }

            // BRIDGE VISION -> NLP
            if (mlResult) {
                if (personFound) {
                    if (mlResult.firstChild) mlResult.firstChild.textContent = "ALERTE SÉCURITÉ : ";
                } else {
                    if (mlResult.firstChild) mlResult.firstChild.textContent = "Verdict : ";
                }
            }

            // Alarme
            if (alarmActive && personFound) {
                alarmAlert.style.display = 'block';
            } else {
                alarmAlert.style.display = 'none';
            }

            // JOURNAL AUTOMATIQUE (SYSTEM LOG)
            // Log si Personne ou Téléphone détecté
            const hasIntruder = (detectionData.person > 0) || (detectionData['cell phone'] > 0);
            if (hasIntruder && (Date.now() - lastLogTime > 3000)) {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const msg = document.createElement('div');
                msg.style.borderBottom = "1px solid #333";
                msg.innerHTML = `<span style="color:#e74c3c">[${timeString}]</span> ⚠️ Intrusion détectée (Personne/Tel)`;
                if (activityLog) {
                    activityLog.appendChild(msg);
                    activityLog.scrollTop = activityLog.scrollHeight; 
                }
                lastLogTime = Date.now();
            }
        }
    }, 200);
});

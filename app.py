from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash
import json
import os
import datetime
import subprocess
import requests
from openai import OpenAI

# --- CONFIGURATION ---
app = Flask(__name__)
app.secret_key = 'smart_prospector_secret_key'
DB_FILE = 'prospects.json'
# Configuration pour n8n local (Workflow "Prospection API")
WEBHOOK_N8N = "http://127.0.0.1:5678/webhook-test/prospect-action"

# Configuration OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# --- HTML TEMPLATE (DARK MODE) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Smart Prospector | Beyond RAG</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; font-family: 'Segoe UI', sans-serif; }
        .card { border: 1px solid #334155; background-color: #1e293b; }
        .table-dark { --bs-table-bg: #1e293b; --bs-table-border-color: #334155; }
        .badge-score { min-width: 40px; }
        .btn-action { width: 35px; height: 35px; padding: 0; display: inline-flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-secondary mb-4">
    <div class="container-fluid">
        <a class="navbar-brand text-info fw-bold" href="#"><i class="fas fa-network-wired"></i> Smart Prospector</a>
        <button class="btn btn-outline-light btn-sm" data-bs-toggle="modal" data-bs-target="#addModal">
            <i class="fas fa-plus"></i> Nouveau Lead
        </button>
    </div>
</nav>

<div class="container-fluid px-4">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="card shadow-lg">
        <div class="card-header d-flex justify-content-between align-items-center bg-transparent border-bottom border-secondary">
            <h5 class="mb-0 text-white">Pipeline Actif</h5>
            <span class="badge bg-primary">{{ prospects|length }} Prospects</span>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-dark table-hover mb-0 align-middle">
                    <thead class="text-uppercase text-secondary small">
                        <tr>
                            <th>Score</th>
                            <th>Identité</th>
                            <th>Email</th>
                            <th>Expertise & Stack</th>
                            <th>Statut / Dern. Relance</th>
                            <th>Feedback Client</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in prospects %}
                        <tr>
                            <td>
                                {% set s = p.scoring.lead_score %}
                                <span class="badge rounded-pill badge-score {% if s >= 80 %}bg-danger{% elif s >= 50 %}bg-warning text-dark{% else %}bg-secondary{% endif %}">
                                    {{ s }}
                                </span>
                            </td>
                            <td>
                                <div class="fw-bold text-white">{{ p.contact_info.full_name }}</div>
                                <div class="small text-muted">{{ p.contact_info.role }}</div>
                                <div class="small text-info">{{ p.contact_info.organization }}</div>
                            </td>
                            <td class="small text-secondary">
                                {{ p.contact_info.email or '—' }}
                            </td>
                            <td>
                                <span class="badge bg-dark border border-secondary">{{ p.contact_info.segment }}</span>
                                <div class="mt-1 small text-white-50">
                                    <i class="fas fa-code"></i> {{ p.tech_stack_interest.primary_focus|join(', ') }}
                                </div>
                            </td>
                            <td>
                                {% if p.pipeline_status.last_interaction %}
                                    <div class="text-success small"><i class="fas fa-check-circle"></i> {{ p.pipeline_status.last_interaction[:10] }}</div>
                                {% else %}
                                    <span class="badge bg-secondary opacity-50">Aucune action</span>
                                {% endif %}
                            </td>
                            <td>
                                <form action="/feedback/{{ p.id }}" method="POST" class="d-flex gap-2">
                                    <input type="text" name="feedback" class="form-control form-control-sm bg-dark text-white border-secondary" 
                                           placeholder="Noter un retour..." value="{{ p.pipeline_status.get('feedback', '') }}">
                                    <button type="submit" class="btn btn-sm btn-outline-secondary"><i class="fas fa-save"></i></button>
                                </form>
                            </td>
                            <td class="text-end">
                                <button onclick="generateEmail('{{ p.id }}')" class="btn btn-sm btn-outline-info me-1" title="Générer Relance IA">
                                    <i class="fas fa-magic"></i> <span id="spin-{{ p.id }}" class="spinner-border spinner-border-sm d-none"></span>
                                </button>
                                <form action="/push/{{ p.id }}" method="POST" class="d-inline">
                                    <button type="submit" class="btn btn-sm btn-outline-success" title="Pousser vers N8N">
                                        <i class="fas fa-rocket"></i>
                                    </button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Modal Ajout -->
<div class="modal fade" id="addModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Ajouter un Prospect</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form action="/add" method="POST">
                <div class="modal-body">
                    <div class="mb-3"><label>Nom Complet</label><input name="name" class="form-control bg-dark text-white" required></div>
                    <div class="mb-3"><label>Email Prospect</label><input type="email" name="email" class="form-control bg-dark text-white" placeholder="ex: contact@entreprise.com" required></div>
                    <div class="row">
                        <div class="col-6 mb-3"><label>Rôle</label><input name="role" class="form-control bg-dark text-white" required></div>
                        <div class="col-6 mb-3"><label>Organisation</label><input name="org" class="form-control bg-dark text-white" required></div>
                    </div>
                    <div class="mb-3"><label>Segment</label>
                        <select name="segment" class="form-select bg-dark text-white">
                            <option value="PROFESSIONAL">Industrie (Pro)</option>
                            <option value="ACADEMIC">Académique (École)</option>
                        </select>
                    </div>
                    <div class="mb-3"><label>Stack Technique (virgules)</label><input name="stack" class="form-control bg-dark text-white" placeholder="YOLO, N8N, Python..." required></div>
                </div>
                <div class="modal-footer"><button type="submit" class="btn btn-primary">Sauvegarder</button></div>
            </form>
        </div>
    </div>
</div>

<!-- Modal Email -->
<div class="modal fade" id="emailModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title text-info">📧 Email Généré (Beyond RAG)</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body bg-black">
                <pre id="emailOutput" class="text-white p-3" style="white-space: pre-wrap; font-family: monospace;"></pre>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                <button class="btn btn-success" onclick="copyEmail()">Copier le texte</button>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
async function generateEmail(id) {
    const spin = document.getElementById('spin-' + id);
    spin.classList.remove('d-none');
    
    try {
        const res = await fetch('/generate/' + id);
        const data = await res.json();
        spin.classList.add('d-none');
        
        if(data.error) alert(data.error);
        else {
            document.getElementById('emailOutput').textContent = data.email;
            new bootstrap.Modal(document.getElementById('emailModal')).show();
        }
    } catch(e) {
        spin.classList.add('d-none');
        alert("Erreur serveur");
    }
}
function copyEmail() {
    navigator.clipboard.writeText(document.getElementById('emailOutput').textContent);
    alert("Copié !");
}
</script>
</body>
</html>
"""

# --- LOGIQUE BACKEND ---

def get_db():
    if not os.path.exists(DB_FILE): return {"prospects": []}
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {"prospects": []}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=2)

def calc_score(role, stack):
    score = 10
    if any(x in role.lower() for x in ['directeur', 'cto', 'lead', 'head']): score += 20
    if any(x in [s.lower() for s in stack] for x in ['yolo', 'n8n', 'nvidia']): score += 30
    return score

@app.route('/')
def home():
    db = get_db()
    # Tri par score
    leads = sorted(db['prospects'], key=lambda x: x['scoring']['lead_score'], reverse=True)
    return render_template_string(HTML_TEMPLATE, prospects=leads)

@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    stack = [s.strip() for s in request.form['stack'].split(',')]
    lead = {
        "id": str(len(db['prospects']) + 1).zfill(3),
        "contact_info": {
            "full_name": request.form['name'],
            "role": request.form['role'],
            "organization": request.form['org'],
            "segment": request.form['segment'],
            "email": request.form['email']
        },
        "tech_stack_interest": { "primary_focus": stack, "maturity_level": "UNKNOWN", "tools_detected": stack },
        "scoring": { "lead_score": calc_score(request.form['role'], stack) },
        "pipeline_status": { "stage": "COLD_OUTREACH", "last_interaction": None }
    }
    db['prospects'].append(lead)
    save_db(db)
    flash("Lead ajouté avec succès !", "success")
    return redirect(url_for('home'))

@app.route('/generate/<id>')
def generate(id):
    db = get_db()
    lead = next((p for p in db['prospects'] if p['id'] == id), None)
    if not lead: return jsonify({"error": "Lead introuvable"}), 404

    # Construction du Prompt Expert
    seg = lead['contact_info']['segment']
    stack = ", ".join(lead['tech_stack_interest']['primary_focus'])
    
    context = "Optimisation ROI, NVIDIA, Edge AI" if seg == "PROFESSIONAL" else "Pédagogie Moderne, Workflows, Théorie vs Réalité"
    
    prompt = f"""
    [RÔLE] Tu es Stéphane Krebs, Expert IA (10 ans). Approche: "Beyond RAG" et Industrialisation.
    [MISSION] Rédige un email court et percutant pour {lead['contact_info']['full_name']} ({lead['contact_info']['role']}).
    [TECH] Stack: {stack}. Contexte: {context}.
    [STYLE] Direct, Expert, Problème/Solution. Pas de blabla.
    
    [SIGNATURE À UTILISER]
    Cordialement,
    Stéphane Krebs
    Expert en Automatisation & IA | Stéphane Krebs Consulting
    Web: https://www.stephanekrebs.fr
    """
    
    try:
        if not client:
            return jsonify({"error": "Clé API OpenAI manquante. Définissez la variable d'environnement OPENAI_API_KEY."})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es Stéphane Krebs, Expert IA (10 ans)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        email_content = response.choices[0].message.content
        
        # On stocke le mail généré pour l'envoyer plus tard à n8n
        lead['pipeline_status']['draft_email'] = email_content.strip()
        save_db(db)
        
        return jsonify({"email": email_content.strip()})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/feedback/<id>', methods=['POST'])
def feedback(id):
    db = get_db()
    lead = next((p for p in db['prospects'] if p['id'] == id), None)
    if lead:
        lead['pipeline_status']['feedback'] = request.form['feedback']
        save_db(db)
        flash("Feedback enregistré.", "info")
    return redirect(url_for('home'))

@app.route('/push/<id>', methods=['POST'])
def push(id):
    db = get_db()
    lead = next((p for p in db['prospects'] if p['id'] == id), None)
    
    if not lead:
        flash("Erreur: Lead introuvable.", "danger")
        return redirect(url_for('home'))

    # Sécurité : Vérifier si un mail a été généré
    email_text = lead['pipeline_status'].get('draft_email')
    if not email_text:
        flash("Erreur: Vous devez d'abord générer un email avec la baguette magique 🪄 !", "warning")
        return redirect(url_for('home'))

    # Préparation du Payload pour n8n
    payload = {
        "email": lead['contact_info'].get('email', 'email_manquant@example.com'),
        "nom": lead['contact_info']['full_name'],
        "entreprise": lead['contact_info']['organization'],
        "poste": lead['contact_info']['role'],
        "type_action": "approche" if not lead['pipeline_status']['last_interaction'] else "relance",
        "message_personnalise": lead['pipeline_status'].get('draft_email', '')
    }

    print(f"DEBUG - Payload envoyé à n8n : {json.dumps(payload, indent=2)}")

    try:
        # Envoi réel au Webhook N8N
        response = requests.post(WEBHOOK_N8N, json=payload, timeout=5)
        response.raise_for_status()
        
        # On marque l'interaction seulement après succès de l'envoi
        lead['pipeline_status']['last_interaction'] = datetime.datetime.now().isoformat()
        save_db(db)
        
        flash(f"Succès ! Lead envoyé à n8n (Code {response.status_code}).", "success")
    except Exception as e:
        flash(f"Erreur de connexion à n8n : {str(e)}", "danger")

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)

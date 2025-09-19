from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import datetime
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_super_complexe_123456789'  # Changez ceci en production

CSV_FILE = 'incidents.csv'
USERS_FILE = 'users.csv'

# Charger les utilisateurs

# Charger les utilisateurs
def lire_utilisateurs():
    utilisateurs = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            utilisateurs = list(reader)
    return utilisateurs

# Vérifier les identifiants
def verifier_utilisateur(username, password):
    utilisateurs = lire_utilisateurs()
    for user in utilisateurs:
        if user['username'] == username and user['password'] == password:
            return user
    return None

# Charger les incidents
def lire_incidents():
    incidents = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            incidents = list(reader)
    return incidents

# Ajouter un incident
def ajouter_incident(titre, description, gravite):
    incidents = lire_incidents()
    nouvel_id = str(max([int(i['id']) for i in incidents], default=0) + 1)
    nouveau = {
        'id': nouvel_id,
        'titre': titre,
        'description': description,
        'gravite': gravite,
        'date': datetime.datetime.today().strftime('%Y-%m-%d'),
        'statut': 'Nouveau'
    }
    incidents.append(nouveau)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=nouveau.keys())
        writer.writeheader()
        writer.writerows(incidents)

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verifier_utilisateur(username, password)
        if user:
            session['user_id'] = user['username']
            session['user_name'] = user['nom_complet']
            session['user_role'] = user['role']
            session['user_email'] = user['email']
            flash(f'Bienvenue {user["nom_complet"]} !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

# Route de déconnexion
@app.route('/logout')
def logout():
    user_name = session.get('user_name', 'Utilisateur')
    session.clear()
    flash(f'Au revoir {user_name} ! Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('login'))

# Route principale (protégée)
@app.route('/')
@login_required
def index():
    incidents = lire_incidents()
    return render_template('index.html', incidents=incidents)

# Ajouter un incident (protégé)
@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        gravite = request.form['gravite']
        ajouter_incident(titre, description, gravite)
        flash('Incident ajouté avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('ajouter.html')

# Détails d’un incident
@app.route('/incident/<int:incident_id>')
def detail(incident_id):
    incidents = lire_incidents()
    incident = next((i for i in incidents if int(i['id']) == incident_id), None)
    return render_template('detail.html', incident=incident)

if __name__ == '__main__':
    app.run(debug=True)
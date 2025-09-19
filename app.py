from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import datetime
from functools import wraps

# Configuration pour Azure
try:
    from config import Config
    config = Config()
except ImportError:
    # Configuration par défaut
    class Config:
        SECRET_KEY = 'dev-secret-key-change-in-production'
        PORT = 5000
    config = Config()

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'incidents.csv')
USERS_FILE = os.path.join(BASE_DIR, 'users.csv')

# Décorateur pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def lire_utilisateurs():
    if not os.path.exists(USERS_FILE):
        return []
    
    with open(USERS_FILE, 'r', encoding='utf-8') as file:
        return list(csv.DictReader(file))

def lire_incidents():
    if not os.path.exists(CSV_FILE):
        return []
    
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        return list(csv.DictReader(file))

def ecrire_incident(incident):
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'titre', 'description', 'priorite', 'statut', 'date_creation']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(incident)

def obtenir_prochain_id():
    incidents = lire_incidents()
    if not incidents:
        return 1
    return max(int(i['id']) for i in incidents) + 1

# Routes
@app.route('/')
@login_required
def index():
    incidents = lire_incidents()
    return render_template('index.html', incidents=incidents, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        utilisateurs = lire_utilisateurs()
        
        for user in utilisateurs:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                flash(f'Bienvenue {username}!', 'success')
                return redirect(url_for('index'))
        
        flash('Nom d utilisateur ou mot de passe incorrect!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if request.method == 'POST':
        incident = {
            'id': obtenir_prochain_id(),
            'titre': request.form['titre'],
            'description': request.form['description'],
            'priorite': request.form['priorite'],
            'statut': 'Ouvert',
            'date_creation': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        ecrire_incident(incident)
        flash('Incident ajouté avec succès!', 'success')
        return redirect(url_for('index'))
    
    return render_template('ajouter.html', username=session['username'])

@app.route('/incident/<int:incident_id>')
@login_required
def detail(incident_id):
    incidents = lire_incidents()
    incident = next((i for i in incidents if int(i['id']) == incident_id), None)
    return render_template('detail.html', incident=incident)

@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    }

if __name__ == '__main__':
    port = config.PORT if hasattr(config, 'PORT') else 5000
    debug = not os.environ.get('FLASK_ENV') == 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
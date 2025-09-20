from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import datetime
import pyodbc
import bcrypt
import re
from functools import wraps
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialise la connexion à la base de données Azure SQL"""
        self.connection_string = self.get_connection_string()
    
    def get_connection_string(self):
        """Récupère la chaîne de connexion depuis les variables d'environnement"""
        conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
        if conn_string:
            return conn_string
        
        # Construire la chaîne de connexion avec les paramètres séparés
        server = os.getenv('AZURE_SQL_SERVER')
        database = os.getenv('AZURE_SQL_DATABASE')
        username = os.getenv('AZURE_SQL_USERNAME')
        password = os.getenv('AZURE_SQL_PASSWORD')
        
        if all([server, database, username, password]):
            return (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            )
        else:
            raise ValueError("Variables d'environnement de base de données manquantes")
    
    def get_connection(self):
        """Établit et retourne une connexion à la base de données"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"Erreur de connexion à la base de données : {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False):
        """
        Exécute une requête SQL
        
        Args:
            query (str): Requête SQL à exécuter
            params (tuple): Paramètres pour la requête
            fetch (bool): True pour récupérer les résultats
            
        Returns:
            list: Résultats si fetch=True, None sinon
        """
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                cursor.close()
                return results
            else:
                connection.commit()
                cursor.close()
                return None
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

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

# Fonctions de gestion des utilisateurs avec Azure SQL

def hash_password(password):
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Vérifie un mot de passe contre son hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valide la force d'un mot de passe"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, "Mot de passe valide"

def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur depuis la base de données"""
    try:
        query = "SELECT * FROM users WHERE username = ? AND actif = 1"
        results = db_manager.execute_query(query, (username,), fetch=True)
        return results[0] if results else None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur : {e}")
        return None

def get_user_by_email(email):
    """Récupère un utilisateur par son email depuis la base de données"""
    try:
        query = "SELECT * FROM users WHERE email = ? AND actif = 1"
        results = db_manager.execute_query(query, (email,), fetch=True)
        return results[0] if results else None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur par email : {e}")
        return None

def create_user(username, email, password, nom_complet, role='user'):
    """Crée un nouvel utilisateur dans la base de données"""
    try:
        # Vérifier si l'utilisateur ou l'email existe déjà
        if get_user_by_username(username):
            return False, "Ce nom d'utilisateur existe déjà"
        
        if get_user_by_email(email):
            return False, "Cette adresse email est déjà utilisée"
        
        # Valider le mot de passe
        is_valid, message = validate_password(password)
        if not is_valid:
            return False, message
        
        # Hasher le mot de passe
        password_hash = hash_password(password)
        
        # Insérer le nouvel utilisateur
        query = """
        INSERT INTO users (username, email, password_hash, nom_complet, role) 
        VALUES (?, ?, ?, ?, ?)
        """
        params = (username, email, password_hash, nom_complet, role)
        db_manager.execute_query(query, params)
        
        return True, "Utilisateur créé avec succès"
        
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")
        return False, "Erreur lors de la création de l'utilisateur"

def verifier_utilisateur(username, password):
    """Vérifie les identifiants d'un utilisateur avec la base de données"""
    try:
        user = get_user_by_username(username)
        if user and verify_password(password, user['password_hash']):
            return user
        return None
    except Exception as e:
        print(f"Erreur lors de la vérification de l'utilisateur : {e}")
        return None

# Fonction de compatibilité (deprecated)
def lire_utilisateurs():
    """Fonction deprecated - utiliser get_user_by_username à la place"""
    try:
        query = "SELECT * FROM users WHERE actif = 1"
        return db_manager.execute_query(query, fetch=True)
    except Exception as e:
        print(f"Erreur lors de la lecture des utilisateurs : {e}")
        return []

# Charger les incidents
def lire_incidents():
    """Lit tous les incidents depuis la base de données Azure SQL"""
    try:
        query = "SELECT * FROM incidents ORDER BY date DESC, id DESC"
        incidents = db_manager.execute_query(query, fetch=True)
        
        # Convertir les dates en chaînes pour l'affichage
        for incident in incidents:
            if incident['date']:
                incident['date'] = incident['date'].strftime('%Y-%m-%d')
        
        return incidents
    except Exception as e:
        print(f"Erreur lors de la lecture des incidents : {e}")
        flash('Erreur lors du chargement des incidents depuis la base de données.', 'error')
        return []

# Ajouter un incident
def ajouter_incident(titre, description, gravite):
    """Ajoute un nouvel incident dans la base de données Azure SQL"""
    try:
        # Obtenir le prochain ID
        query_max_id = "SELECT ISNULL(MAX(id), 0) + 1 as next_id FROM incidents"
        result = db_manager.execute_query(query_max_id, fetch=True)
        nouvel_id = result[0]['next_id'] if result else 1
        
        # Insérer le nouvel incident
        query_insert = """
        INSERT INTO incidents (id, titre, description, gravite, date, statut) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        date_today = datetime.datetime.today().strftime('%Y-%m-%d')
        params = (nouvel_id, titre, description, gravite, date_today, 'Nouveau')
        
        db_manager.execute_query(query_insert, params)
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'incident : {e}")
        flash('Erreur lors de l\'ajout de l\'incident dans la base de données.', 'error')
        return False

def obtenir_incident_par_id(incident_id):
    """Récupère un incident spécifique par son ID depuis la base de données"""
    try:
        query = "SELECT * FROM incidents WHERE id = ?"
        results = db_manager.execute_query(query, (incident_id,), fetch=True)
        
        if results:
            incident = results[0]
            # Convertir la date en chaîne pour l'affichage
            if incident['date']:
                incident['date'] = incident['date'].strftime('%Y-%m-%d')
            return incident
        return None
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'incident {incident_id} : {e}")
        return None

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

# Route d'enregistrement
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        nom_complet = request.form['nom_complet'].strip()
        role = request.form.get('role', 'user')
        
        # Validation des données
        if not all([username, email, password, password_confirm, nom_complet]):
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Format d\'email invalide.', 'error')
            return render_template('register.html')
        
        if len(username) < 3 or len(username) > 50:
            flash('Le nom d\'utilisateur doit contenir entre 3 et 50 caractères.', 'error')
            return render_template('register.html')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores.', 'error')
            return render_template('register.html')
        
        # Créer l'utilisateur
        success, message = create_user(username, email, password, nom_complet, role)
        
        if success:
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('register.html')
    
    return render_template('register.html')

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
        
        if ajouter_incident(titre, description, gravite):
            flash('Incident ajouté avec succès !', 'success')
        else:
            flash('Erreur lors de l\'ajout de l\'incident.', 'error')
        
        return redirect(url_for('index'))
    return render_template('ajouter.html')

# Détails d'un incident
@app.route('/incident/<int:incident_id>')
@login_required
def detail(incident_id):
    incident = obtenir_incident_par_id(incident_id)
    if incident is None:
        flash('Incident non trouvé.', 'error')
        return redirect(url_for('index'))
    return render_template('detail.html', incident=incident)

if __name__ == '__main__':
    app.run(debug=True)
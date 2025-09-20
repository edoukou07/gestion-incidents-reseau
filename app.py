from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import datetime
import pyodbc
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
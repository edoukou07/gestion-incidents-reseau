from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
import datetime
import pyodbc
import bcrypt
import re
import requests
import json
import time
from functools import wraps
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential
from io import StringIO
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

class BlobStorageManager:
    def __init__(self):
        """Initialise la connexion à Azure Blob Storage avec Service Principal"""
        try:
            # Récupérer les variables d'environnement
            self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
            self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
            self.client_id = os.getenv('AZURE_CLIENT_ID')
            self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
            self.tenant_id = os.getenv('AZURE_TENANT_ID')
            
            # Validation des variables d'environnement
            if not all([self.storage_account_name, self.container_name, 
                       self.client_id, self.client_secret, self.tenant_id]):
                raise ValueError("Variables d'environnement Azure manquantes pour Blob Storage")
            
            # Créer les credentials du service principal
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # URL du compte de stockage
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            
            # Créer le client Blob Service
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=self.credential
            )
            
            print(f"✅ Connexion à Azure Blob Storage établie: {self.storage_account_name}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de Blob Storage: {e}")
            raise
    
    def download_blob_as_text(self, blob_name):
        """Télécharge un blob et retourne son contenu en tant que texte"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            # Télécharger le contenu du blob
            blob_data = blob_client.download_blob()
            content = blob_data.readall().decode('utf-8')
            
            print(f"✅ Blob téléchargé avec succès: {blob_name}")
            return content
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement du blob {blob_name}: {e}")
            raise
    
    def list_blobs(self):
        """Liste tous les blobs dans le container"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = container_client.list_blobs()
            blob_list = [blob.name for blob in blobs]
            print(f"✅ {len(blob_list)} blobs trouvés dans le container {self.container_name}")
            return blob_list
            
        except Exception as e:
            print(f"❌ Erreur lors de la liste des blobs: {e}")
            return []
    
    def blob_exists(self, blob_name):
        """Vérifie si un blob existe dans le container"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            return blob_client.exists()
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification de l'existence du blob {blob_name}: {e}")
            return False

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
        # server = os.getenv('AZURE_SQL_SERVER')
        # database = os.getenv('AZURE_SQL_DATABASE')
        # username = os.getenv('AZURE_SQL_USERNAME')
        # password = os.getenv('AZURE_SQL_PASSWORD')
        
        """ if all([server, database, username, password]):
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
     """
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

# Instance globale du gestionnaire Blob Storage
try:
    blob_manager = BlobStorageManager()
except Exception as e:
    print(f"⚠️ Attention: Impossible d'initialiser Blob Storage: {e}")
    print("💡 L'application continuera avec les données de la base de données.")
    blob_manager = None

def call_azure_function_migration():
    """
    Appelle la fonction Azure pour migrer les utilisateurs depuis Azure Blob Storage
    """
    azure_function_url = "https://testhttpinc.azurewebsites.net/api/migrate-csv-from-blob"
    params = {
        "container_name": "appfiles",
        "blob_name": "users.csv"
    }
    
    try:
        print("🚀 Appel de la fonction Azure pour la migration des utilisateurs...")
        print(f"📡 URL: {azure_function_url}")
        print(f"📦 Container: {params['container_name']}")
        print(f"📄 Fichier: {params['blob_name']}")
        
        # Effectuer l'appel avec un timeout
        response = requests.get(azure_function_url, params=params, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Réponse de la fonction Azure reçue avec succès")
            print(f"📊 Utilisateurs migrés : {result.get('migrated_count', 0)}")
            print(f"⚠️ Utilisateurs ignorés : {result.get('skipped_count', 0)}")
            print(f"❌ Erreurs : {result.get('error_count', 0)}")
            
            if result.get('success', False):
                print("🎉 Migration des utilisateurs terminée avec succès !")
            else:
                print("⚠️ Migration terminée avec des avertissements")
                
            # Afficher quelques messages importants
            messages = result.get('messages', [])
            for message in messages[-5:]:  # Afficher les 5 derniers messages
                print(f"   {message}")
                
        else:
            print(f"❌ Erreur lors de l'appel à la fonction Azure: {response.status_code}")
            print(f"📄 Réponse: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout lors de l'appel à la fonction Azure (plus de 60 secondes)")
        print("💡 La migration peut encore être en cours...")
    except requests.exceptions.RequestException as e:
        print(f"🔌 Erreur de connexion lors de l'appel à la fonction Azure: {e}")
        print("💡 Vérifiez que la fonction Azure est accessible")
    except Exception as e:
        print(f"❌ Erreur inattendue lors de l'appel à la fonction Azure: {e}")

def migrate_incidents_from_blob():
    """
    Migre les incidents depuis Azure Blob Storage vers la base de données Azure SQL
    """
    if not blob_manager:
        print("⚠️ Blob Storage non configuré, migration des incidents annulée")
        return False
    
    try:
        print("🔄 === MIGRATION DES INCIDENTS ===")
        print("📦 Recherche des fichiers d'incidents dans Azure Blob Storage...")
        
        # Nom du fichier CSV d'incidents dans le blob
        incidents_blob_name = "incidents.csv"
        
        # Vérifier si le blob existe
        if not blob_manager.blob_exists(incidents_blob_name):
            print(f"ℹ️ Fichier {incidents_blob_name} non trouvé dans le blob storage")
            print("💡 Aucune migration d'incidents nécessaire")
            return True
        
        # Télécharger le contenu du blob
        print(f"⬇️ Téléchargement de {incidents_blob_name}...")
        csv_content = blob_manager.download_blob_as_text(incidents_blob_name)
        
        # Utiliser pandas pour lire le CSV
        df = pd.read_csv(StringIO(csv_content))
        incidents_data = df.to_dict('records')
        
        if not incidents_data:
            print("ℹ️ Aucun incident trouvé dans le fichier CSV")
            return True
        
        print(f"📊 {len(incidents_data)} incidents trouvés dans le blob storage")
        
        # Vérifier si la table incidents existe et est vide
        try:
            count_query = "SELECT COUNT(*) as count FROM incidents"
            count_result = db_manager.execute_query(count_query, fetch=True)
            existing_count = count_result[0]['count'] if count_result else 0
            
            if existing_count > 0:
                print(f"ℹ️ La table contient déjà {existing_count} incidents")
                print("💡 Migration annulée pour éviter les doublons")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de la vérification de la table incidents: {e}")
            print("💡 Assurez-vous que la table incidents existe")
            return False
        
        # Migrer chaque incident
        migrated_count = 0
        error_count = 0
        
        print("🔄 Début de la migration des incidents...")
        
        for incident in incidents_data:
            try:
                # Nettoyer et valider les données
                incident_id = int(incident.get('id', 0))
                titre = str(incident.get('titre', '')).strip()
                description = str(incident.get('description', '')).strip()
                gravite = str(incident.get('gravite', 'Moyen')).strip()
                date = incident.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
                statut = str(incident.get('statut', 'Nouveau')).strip()
                
                # Valider les champs obligatoires
                if not titre:
                    print(f"⚠️ Incident ID {incident_id} ignoré: titre manquant")
                    continue
                
                # Normaliser les valeurs de gravité
                gravite_normalisee = gravite
                if gravite.lower() in ['critical', 'critique']:
                    gravite_normalisee = 'Critique'
                elif gravite.lower() in ['major', 'majeur']:
                    gravite_normalisee = 'Majeur'
                elif gravite.lower() in ['minor', 'mineur']:
                    gravite_normalisee = 'Mineur'
                elif gravite.lower() in ['low', 'bas', 'faible']:
                    gravite_normalisee = 'Faible'
                
                # Normaliser la date
                try:
                    if isinstance(date, str):
                        parsed_date = pd.to_datetime(date)
                        date_normalized = parsed_date.strftime('%Y-%m-%d')
                    else:
                        date_normalized = datetime.datetime.now().strftime('%Y-%m-%d')
                except:
                    date_normalized = datetime.datetime.now().strftime('%Y-%m-%d')
                
                # Insérer l'incident dans la base de données
                insert_query = """
                INSERT INTO incidents (id, titre, description, gravite, date, statut) 
                VALUES (?, ?, ?, ?, ?, ?)
                """
                params = (incident_id, titre, description, gravite_normalisee, 
                         date_normalized, statut)
                
                db_manager.execute_query(insert_query, params)
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"   📝 {migrated_count} incidents migrés...")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Erreur migration incident ID {incident.get('id', 'unknown')}: {e}")
                continue
        
        # Résumé de la migration
        print(f"\n📊 === RÉSUMÉ DE LA MIGRATION ===")
        print(f"✅ Incidents migrés avec succès : {migrated_count}")
        print(f"❌ Incidents avec erreurs : {error_count}")
        print(f"📈 Total traités : {len(incidents_data)}")
        
        if migrated_count > 0:
            print("🎉 Migration des incidents terminée avec succès !")
            return True
        else:
            print("⚠️ Aucun incident n'a pu être migré")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration des incidents: {e}")
        return False

def initialize_application():
    """
    Initialise l'application au démarrage
    """
    print("🔧 === INITIALISATION DE L'APPLICATION ===")
    print("📅 Démarrage de l'application de gestion des incidents réseau")
    
    # Appeler la fonction Azure pour migrer les utilisateurs
    call_azure_function_migration()
    
    # Migrer les incidents depuis blob storage vers la base de données
    migrate_incidents_from_blob()
    
    print("✅ === INITIALISATION TERMINÉE ===\n")

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

# Initialiser l'application au démarrage
initialize_application()

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
        print("🔄 Chargement des incidents depuis la base de données SQL...")
        query = "SELECT * FROM incidents ORDER BY date DESC, id DESC"
        incidents = db_manager.execute_query(query, fetch=True)
        
        # Convertir les dates en chaînes pour l'affichage
        for incident in incidents:
            if incident['date']:
                incident['date'] = incident['date'].strftime('%Y-%m-%d')
        
        print(f"✅ {len(incidents)} incidents chargés depuis la base de données SQL")
        return incidents
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des incidents depuis SQL: {e}")
        flash('Erreur lors du chargement des incidents. Vérifiez la configuration de la base de données.', 'error')
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

# Route pour déclencher manuellement la migration des utilisateurs
@app.route('/admin/migrate-users')
@login_required
def migrate_users_manually():
    # Vérifier que l'utilisateur est administrateur
    if session.get('user_role') != 'admin':
        flash('Accès refusé. Cette fonctionnalité est réservée aux administrateurs.', 'error')
        return redirect(url_for('index'))
    
    try:
        call_azure_function_migration()
        flash('Migration des utilisateurs déclenchée avec succès ! Consultez les logs pour plus de détails.', 'success')
    except Exception as e:
        flash(f'Erreur lors du déclenchement de la migration : {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
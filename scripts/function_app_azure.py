import azure.functions as func
import logging
import os
import csv
import json
import io
from dotenv import load_dotenv
import pyodbc
import bcrypt
import re
from azure.storage.blob import BlobServiceClient

# Charger les variables d'environnement
load_dotenv()

def get_blob_service_client():
    """Initialise le client Azure Blob Storage"""
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("Variable d'environnement AZURE_STORAGE_CONNECTION_STRING manquante")
    return BlobServiceClient.from_connection_string(connection_string)

def download_csv_from_blob(container_name, blob_name):
    """
    Télécharge un fichier CSV depuis Azure Blob Storage
    
    Args:
        container_name (str): Nom du conteneur
        blob_name (str): Nom du fichier blob
        
    Returns:
        StringIO: Contenu du fichier CSV
    """
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        # Télécharger le contenu du blob
        blob_data = blob_client.download_blob()
        csv_content = blob_data.readall().decode('utf-8')
        
        return io.StringIO(csv_content)
        
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du fichier {blob_name} : {e}")
        raise

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

class DatabaseManager:
    def __init__(self):
        """Initialise la connexion à la base de données Azure SQL"""
        self.connection_string = self.get_connection_string()
    
    def get_connection_string(self):
        """Récupère la chaîne de connexion depuis les variables d'environnement"""
        conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
        if conn_string:
            return conn_string
        raise ValueError("Variable d'environnement AZURE_SQL_CONNECTION_STRING manquante")
    
    def get_connection(self):
        """Établit et retourne une connexion à la base de données"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"Erreur de connexion à la base de données : {e}")
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
            logging.error(f"Erreur lors de l'exécution de la requête : {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()

def create_users_table_if_not_exists():
    """Crée la table users si elle n'existe pas"""
    try:
        # Vérifier si la table existe
        check_table_query = """
        SELECT COUNT(*) as table_count 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'users'
        """
        
        result = db_manager.execute_query(check_table_query, fetch=True)
        table_exists = result[0]['table_count'] > 0 if result else False
        
        if table_exists:
            logging.info("✅ Table 'users' existe déjà")
            return True, "Table users existe déjà"
        
        # Créer la table users
        create_table_query = """
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(50) UNIQUE NOT NULL,
            email NVARCHAR(100) UNIQUE NOT NULL,
            password_hash NVARCHAR(255) NOT NULL,
            nom_complet NVARCHAR(100) NOT NULL,
            role NVARCHAR(20) DEFAULT 'user',
            actif BIT DEFAULT 1,
            date_creation DATETIME2 DEFAULT GETDATE(),
            date_modification DATETIME2 DEFAULT GETDATE()
        )
        """
        
        db_manager.execute_query(create_table_query)
        logging.info("✅ Table 'users' créée avec succès")
        
        # Créer un index sur l'email pour optimiser les recherches
        create_index_query = """
        CREATE INDEX IX_users_email ON users(email)
        """
        db_manager.execute_query(create_index_query)
        logging.info("✅ Index sur email créé")
        
        # Créer un index sur le username
        create_username_index_query = """
        CREATE INDEX IX_users_username ON users(username)
        """
        db_manager.execute_query(create_username_index_query)
        logging.info("✅ Index sur username créé")
        
        return True, "Table users créée avec succès"
        
    except Exception as e:
        logging.error(f"Erreur lors de la création de la table users : {e}")
        return False, f"Erreur lors de la création de la table : {str(e)}"

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
        logging.error(f"Erreur lors de la récupération de l'utilisateur : {e}")
        return None

def get_user_by_email(email):
    """Récupère un utilisateur par son email depuis la base de données"""
    try:
        query = "SELECT * FROM users WHERE email = ? AND actif = 1"
        results = db_manager.execute_query(query, (email,), fetch=True)
        return results[0] if results else None
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'utilisateur par email : {e}")
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
        logging.error(f"Erreur lors de la création de l'utilisateur : {e}")
        return False, "Erreur lors de la création de l'utilisateur"

def get_blob_service_client():
    """Crée un client Azure Blob Storage"""
    try:
        # Récupérer la connection string Azure Storage depuis les variables d'environnement
        connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("Variable d'environnement AZURE_STORAGE_CONNECTION_STRING manquante")
        
        return BlobServiceClient.from_connection_string(connection_string)
    except Exception as e:
        logging.error(f"Erreur lors de la création du client Blob Storage : {e}")
        raise

def download_csv_from_blob(container_name, blob_name):
    """Télécharge le fichier CSV depuis Azure Blob Storage"""
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Télécharger le contenu du blob
        blob_data = blob_client.download_blob().readall()
        
        # Convertir en string et créer un objet StringIO pour csv.DictReader
        csv_content = blob_data.decode('utf-8')
        return io.StringIO(csv_content)
    
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du fichier CSV depuis le blob : {e}")
        raise

@app.route(route="migrate-csv-users-from-azure")
def migrate_csv_users_from_azure(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fonction Azure pour migrer les utilisateurs depuis un fichier CSV stocké dans Azure Blob Storage
    """
    logging.info('🚀 Démarrage migration CSV depuis Azure Blob Storage vers Azure SQL Database')
    
    result = {
        "success": False,
        "migrated_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        "messages": [],
        "users_created": []
    }
    
    try:
        # Vérifier et créer la table users si nécessaire
        result["messages"].append("🔍 Vérification de la table users...")
        table_success, table_message = create_users_table_if_not_exists()
        result["messages"].append(f"📋 {table_message}")
        
        if not table_success:
            result["error_count"] += 1
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=500
            )
        
        # Récupérer les paramètres depuis la requête
        container_name = req.params.get('container', 'users-data')  # Nom du container par défaut
        blob_name = req.params.get('blob', 'users.csv')  # Nom du fichier par défaut
        
        # Ou depuis le body JSON
        try:
            req_body = req.get_json()
            if req_body:
                container_name = req_body.get('container', container_name)
                blob_name = req_body.get('blob', blob_name)
        except ValueError:
            pass
        
        result["messages"].append(f"📡 Téléchargement du fichier {blob_name} depuis le container {container_name}...")
        
        # Télécharger le fichier CSV depuis Azure Blob Storage
        try:
            csv_file = download_csv_from_blob(container_name, blob_name)
        except Exception as e:
            result["messages"].append(f"❌ Impossible de télécharger le fichier CSV depuis Azure Blob Storage")
            result["messages"].append(f"💡 Vérifiez que le container '{container_name}' et le fichier '{blob_name}' existent")
            result["messages"].append(f"🔧 Erreur: {str(e)}")
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=400
            )
        
        result["messages"].append(f"✅ Fichier téléchargé avec succès")
        result["messages"].append(f"📖 Lecture du fichier CSV...")
        
        # Lire et migrer les utilisateurs
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            username = row.get('username', '').strip()
            email = row.get('email', '').strip()
            password = row.get('password', '').strip()
            nom_complet = row.get('nom_complet', '').strip()
            role = row.get('role', 'user').strip()
            
            # Vérifier les données obligatoires
            if not all([username, email, password, nom_complet]):
                result["messages"].append(f"⚠️ Données manquantes pour {username or 'utilisateur inconnu'}, ignoré")
                result["skipped_count"] += 1
                continue
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = get_user_by_username(username)
            if existing_user:
                result["messages"].append(f"⚠️ Utilisateur '{username}' existe déjà, ignoré")
                result["skipped_count"] += 1
                continue
            
            # Créer l'utilisateur directement
            success, message = create_user(username, email, password, nom_complet, role)
            
            if success:
                result["messages"].append(f"✅ Utilisateur '{username}' créé avec succès")
                result["migrated_count"] += 1
                result["users_created"].append({
                    "username": username,
                    "email": email,
                    "nom_complet": nom_complet,
                    "role": role
                })
            else:
                result["messages"].append(f"❌ Erreur pour '{username}': {message}")
                result["error_count"] += 1
        
        # Résumé final
        result["messages"].append(f"\n📊 === RÉSUMÉ DE LA MIGRATION ===")
        result["messages"].append(f"📡 Source: Azure Blob Storage ({container_name}/{blob_name})")
        result["messages"].append(f"✅ Utilisateurs migrés : {result['migrated_count']}")
        result["messages"].append(f"⚠️ Utilisateurs ignorés : {result['skipped_count']}")
        result["messages"].append(f"❌ Erreurs rencontrées : {result['error_count']}")
        
        if result["migrated_count"] > 0:
            result["success"] = True
            result["messages"].append(f"\n🎉 Migration terminée avec succès ! {result['migrated_count']} utilisateur(s) ajouté(s) à la base de données")
        else:
            result["messages"].append(f"\n⚠️ Aucun nouvel utilisateur n'a été migré")
            if result["error_count"] == 0:
                result["success"] = True  # Pas d'erreur, juste pas de nouveaux utilisateurs
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Erreur critique lors de la migration depuis Azure Blob Storage : {e}")
        result["messages"].append(f"❌ Erreur critique : {str(e)}")
        result["error_count"] += 1
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="create-users-table")
def create_users_table(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fonction Azure pour créer uniquement la table users
    """
    logging.info('🔧 Création de la table users')
    
    result = {
        "success": False,
        "messages": [],
        "table_created": False
    }
    
    try:
        # Créer la table users
        success, message = create_users_table_if_not_exists()
        result["messages"].append(message)
        result["success"] = success
        result["table_created"] = success
        
        if success:
            result["messages"].append("✅ La table users est maintenant prête pour recevoir des données")
            status_code = 200
        else:
            status_code = 500
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=status_code
        )
        
    except Exception as e:
        logging.error(f"Erreur lors de la création de la table : {e}")
        result["messages"].append(f"❌ Erreur inattendue : {str(e)}")
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="migrate-csv-users")
def migrate_csv_users(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fonction Azure unique pour migrer directement les utilisateurs du fichier CSV vers Azure SQL Database
    """
    logging.info('🚀 Démarrage migration CSV vers Azure SQL Database')
    
    result = {
        "success": False,
        "migrated_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        "messages": [],
        "users_created": []
    }
    
    try:
        # Vérifier et créer la table users si nécessaire
        result["messages"].append("🔍 Vérification de la table users...")
        table_success, table_message = create_users_table_if_not_exists()
        result["messages"].append(f"📋 {table_message}")
        
        if not table_success:
            result["error_count"] += 1
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=500
            )
        
        # Vérifier si le fichier users.csv existe
        users_csv = 'users.csv'
        if not os.path.exists(users_csv):
            result["messages"].append(f"❌ Fichier {users_csv} non trouvé dans le répertoire")
            result["messages"].append("💡 Assurez-vous que le fichier users.csv est présent")
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=400
            )
        
        result["messages"].append(f"📖 Lecture du fichier {users_csv}...")
        
        # Lire et migrer les utilisateurs
        with open(users_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', '').strip()
                nom_complet = row.get('nom_complet', '').strip()
                role = row.get('role', 'user').strip()
                
                # Vérifier les données obligatoires
                if not all([username, email, password, nom_complet]):
                    result["messages"].append(f"⚠️ Données manquantes pour {username or 'utilisateur inconnu'}, ignoré")
                    result["skipped_count"] += 1
                    continue
                
                # Vérifier si l'utilisateur existe déjà
                existing_user = get_user_by_username(username)
                if existing_user:
                    result["messages"].append(f"⚠️ Utilisateur '{username}' existe déjà, ignoré")
                    result["skipped_count"] += 1
                    continue
                
                # Créer l'utilisateur directement
                success, message = create_user(username, email, password, nom_complet, role)
                
                if success:
                    result["messages"].append(f"✅ Utilisateur '{username}' créé avec succès")
                    result["migrated_count"] += 1
                    result["users_created"].append({
                        "username": username,
                        "email": email,
                        "nom_complet": nom_complet,
                        "role": role
                    })
                else:
                    result["messages"].append(f"❌ Erreur pour '{username}': {message}")
                    result["error_count"] += 1
        
        # Résumé final
        result["messages"].append(f"\n📊 === RÉSUMÉ DE LA MIGRATION ===")
        result["messages"].append(f"✅ Utilisateurs migrés : {result['migrated_count']}")
        result["messages"].append(f"⚠️ Utilisateurs ignorés : {result['skipped_count']}")
        result["messages"].append(f"❌ Erreurs rencontrées : {result['error_count']}")
        
        if result["migrated_count"] > 0:
            result["success"] = True
            result["messages"].append(f"\n🎉 Migration terminée avec succès ! {result['migrated_count']} utilisateur(s) ajouté(s) à la base de données")
            
            # Sauvegarder le fichier CSV
            try:
                backup_file = f"{users_csv}.backup"
                os.rename(users_csv, backup_file)
                result["messages"].append(f"📦 Fichier CSV sauvegardé vers {backup_file}")
            except Exception as e:
                result["messages"].append(f"⚠️ Impossible de sauvegarder le fichier CSV: {str(e)}")
        else:
            result["messages"].append(f"\n⚠️ Aucun nouvel utilisateur n'a été migré")
            if result["error_count"] == 0:
                result["success"] = True  # Pas d'erreur, juste pas de nouveaux utilisateurs
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Erreur critique lors de la migration : {e}")
        result["messages"].append(f"❌ Erreur critique : {str(e)}")
        result["error_count"] += 1
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="migrate-csv-from-blob")
def migrate_csv_from_blob(req: func.HttpRequest) -> func.HttpResponse:
    """
    Fonction Azure pour migrer des utilisateurs depuis un fichier CSV stocké dans Azure Blob Storage
    Paramètres attendus : container_name, blob_name
    """
    logging.info('🚀 Démarrage migration CSV depuis Azure Blob Storage vers Azure SQL Database')
    
    result = {
        "success": False,
        "migrated_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        "messages": [],
        "users_created": []
    }
    
    try:
        # Récupérer les paramètres
        container_name = req.params.get('container_name')
        blob_name = req.params.get('blob_name')
        
        if not container_name:
            container_name = req.get_json().get('container_name') if req.get_json() else None
        if not blob_name:
            blob_name = req.get_json().get('blob_name') if req.get_json() else None
        
        # Valeurs par défaut
        if not container_name:
            container_name = "users-data"
        if not blob_name:
            blob_name = "users.csv"
        
        result["messages"].append(f"📡 Container : {container_name}")
        result["messages"].append(f"📄 Fichier : {blob_name}")
        
        # Vérifier et créer la table users si nécessaire
        result["messages"].append("🔍 Vérification de la table users...")
        table_success, table_message = create_users_table_if_not_exists()
        result["messages"].append(f"📋 {table_message}")
        
        if not table_success:
            result["error_count"] += 1
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=500
            )
        
        # Télécharger le fichier CSV depuis Azure Blob Storage
        result["messages"].append(f"☁️ Téléchargement du fichier depuis Azure Blob Storage...")
        
        try:
            csv_file = download_csv_from_blob(container_name, blob_name)
        except Exception as e:
            result["messages"].append(f"❌ Erreur lors du téléchargement : {str(e)}")
            result["messages"].append("💡 Vérifiez que le conteneur et le fichier existent dans Azure Blob Storage")
            result["error_count"] += 1
            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False, indent=2),
                mimetype="application/json",
                status_code=400
            )
        
        result["messages"].append(f"✅ Fichier téléchargé avec succès")
        result["messages"].append(f"📖 Lecture du fichier CSV...")
        
        # Lire et migrer les utilisateurs
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            username = row.get('username', '').strip()
            email = row.get('email', '').strip()
            password = row.get('password', '').strip()
            nom_complet = row.get('nom_complet', '').strip()
            role = row.get('role', 'user').strip()
            
            # Vérifier les données obligatoires
            if not all([username, email, password, nom_complet]):
                result["messages"].append(f"⚠️ Données manquantes pour {username or 'utilisateur inconnu'}, ignoré")
                result["skipped_count"] += 1
                continue
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = get_user_by_username(username)
            if existing_user:
                result["messages"].append(f"⚠️ Utilisateur '{username}' existe déjà, ignoré")
                result["skipped_count"] += 1
                continue
            
            # Créer l'utilisateur directement
            success, message = create_user(username, email, password, nom_complet, role)
            
            if success:
                result["messages"].append(f"✅ Utilisateur '{username}' créé avec succès")
                result["migrated_count"] += 1
                result["users_created"].append({
                    "username": username,
                    "email": email,
                    "nom_complet": nom_complet,
                    "role": role
                })
            else:
                result["messages"].append(f"❌ Erreur pour '{username}': {message}")
                result["error_count"] += 1
        
        # Résumé final
        result["messages"].append(f"\n📊 === RÉSUMÉ DE LA MIGRATION ===")
        result["messages"].append(f"📡 Source: Azure Blob Storage ({container_name}/{blob_name})")
        result["messages"].append(f"✅ Utilisateurs migrés : {result['migrated_count']}")
        result["messages"].append(f"⚠️ Utilisateurs ignorés : {result['skipped_count']}")
        result["messages"].append(f"❌ Erreurs rencontrées : {result['error_count']}")
        
        if result["migrated_count"] > 0:
            result["success"] = True
            result["messages"].append(f"\n🎉 Migration terminée avec succès ! {result['migrated_count']} utilisateur(s) ajouté(s) à la base de données")
        else:
            result["messages"].append(f"\n⚠️ Aucun nouvel utilisateur n'a été migré")
            if result["error_count"] == 0:
                result["success"] = True  # Pas d'erreur, juste pas de nouveaux utilisateurs
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Erreur critique lors de la migration depuis Azure Blob Storage : {e}")
        result["messages"].append(f"❌ Erreur critique : {str(e)}")
        result["error_count"] += 1
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=500
        )
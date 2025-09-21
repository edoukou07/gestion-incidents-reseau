import azure.functions as func
import logging
import os
import csv
import json
from dotenv import load_dotenv
import pyodbc
import bcrypt
import re

# Charger les variables d'environnement
load_dotenv()

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
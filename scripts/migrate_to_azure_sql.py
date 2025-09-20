#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration des données CSV vers Azure SQL Database
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les modules nécessaires
from azure_sql_incidents import AzureSQLManager

def migrate_to_azure_sql():
    """Migre les données depuis Azure SQL Database (si elles n'existent pas déjà)"""
    print("🔄 Migration des données vers Azure SQL Database")
    print("=" * 50)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier si le fichier .env existe
    if not os.path.exists('.env'):
        print("❌ Fichier .env manquant !")
        print("📝 Veuillez créer un fichier .env avec votre chaîne de connexion Azure SQL")
        print("📖 Exemple : AZURE_SQL_CONNECTION_STRING=\"DRIVER={ODBC Driver 18 for SQL Server};SERVER=...\"")
        return False
    
    try:
        # Obtenir la chaîne de connexion
        connection_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
        if not connection_string:
            print("❌ Variable AZURE_SQL_CONNECTION_STRING manquante dans .env")
            return False
        
        # Créer une instance du gestionnaire Azure SQL
        sql_manager = AzureSQLManager(connection_string)
        
        # Se connecter à la base de données
        if not sql_manager.connect():
            print("❌ Impossible de se connecter à Azure SQL Database")
            return False
        
        print("✅ Connexion à Azure SQL Database réussie")
        
        # Vérifier si la table existe et contient des données
        check_query = "SELECT COUNT(*) as count FROM incidents"
        try:
            results = sql_manager.execute_query(check_query, fetch=True)
            if results and results[0]['count'] > 0:
                print(f"✅ Table 'incidents' contient déjà {results[0]['count']} enregistrement(s)")
                print("🎉 Migration déjà effectuée !")
                return True
        except:
            print("⚠️ Table 'incidents' n'existe pas encore")
        
        # Créer la table et insérer les données
        print("📋 Création de la table incidents...")
        if not sql_manager.create_incidents_table():
            print("❌ Erreur lors de la création de la table")
            return False
        
        # Insérer les données depuis le CSV
        csv_file = os.path.join(os.path.dirname(__file__), 'incidents.csv')
        print(f"📊 Insertion des données depuis {csv_file}...")
        if not sql_manager.insert_data_from_csv(csv_file):
            print("❌ Erreur lors de l'insertion des données")
            return False
        
        # Afficher les statistiques
        sql_manager.display_statistics()
        
        print("\n🎉 Migration terminée avec succès !")
        print("\n📝 Vous pouvez maintenant utiliser l'application avec Azure SQL :")
        print("   python app_azure_sql.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        return False
    
    finally:
        try:
            sql_manager.disconnect()
        except:
            pass

def main():
    """Fonction principale"""
    print("🚀 Script de migration vers Azure SQL Database")
    print("=" * 50)
    
    if migrate_to_azure_sql():
        print("\n✅ Migration réussie !")
    else:
        print("\n❌ Migration échouée !")
        sys.exit(1)

if __name__ == "__main__":
    main()
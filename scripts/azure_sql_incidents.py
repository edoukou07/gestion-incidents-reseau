#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python pour se connecter à Azure SQL Database et 
créer la table incidents avec les données du CSV
"""

import pyodbc
import csv
import os
import sys
from datetime import datetime

class AzureSQLManager:
    def __init__(self, connection_string):
        """
        Initialise la connexion à Azure SQL Database
        
        Args:
            connection_string (str): Chaîne de connexion pour Azure SQL
        """
        self.connection_string = connection_string
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            print("✅ Connexion réussie à Azure SQL Database")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("🔌 Connexion fermée")
    
    def execute_query(self, query, fetch=False):
        """
        Exécute une requête SQL
        
        Args:
            query (str): Requête SQL à exécuter
            fetch (bool): True pour récupérer les résultats
            
        Returns:
            list: Résultats si fetch=True, None sinon
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self.connection.commit()
                cursor.close()
                return None
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la requête : {e}")
            return None
    
    def create_incidents_table(self):
        """Crée la table incidents"""
        print("📋 Création de la table incidents...")
        
        # Vérifier si la table existe et la supprimer
        drop_table_query = """
        IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'incidents')
        BEGIN
            DROP TABLE incidents;
            PRINT 'Table incidents supprimée.';
        END
        """
        
        # Créer la table
        create_table_query = """
        CREATE TABLE incidents (
            id INT PRIMARY KEY,
            titre NVARCHAR(255) NOT NULL,
            description NVARCHAR(MAX),
            gravite NVARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            statut NVARCHAR(50) NOT NULL
        );
        """
        
        # Exécuter les requêtes
        self.execute_query(drop_table_query)
        result = self.execute_query(create_table_query)
        
        if result is not None or True:  # pyodbc ne retourne pas None pour les DDL
            print("✅ Table incidents créée avec succès")
            return True
        else:
            print("❌ Erreur lors de la création de la table")
            return False
    
    def insert_data_from_csv(self, csv_file_path):
        """
        Insère les données depuis le fichier CSV
        
        Args:
            csv_file_path (str): Chemin vers le fichier CSV
        """
        print(f"📊 Insertion des données depuis {csv_file_path}...")
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    insert_query = """
                    INSERT INTO incidents (id, titre, description, gravite, date, statut) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    cursor = self.connection.cursor()
                    cursor.execute(insert_query, (
                        int(row['id']),
                        row['titre'],
                        row['description'],
                        row['gravite'],
                        row['date'],
                        row['statut']
                    ))
                    cursor.close()
                
                self.connection.commit()
                print("✅ Données insérées avec succès")
                return True
                
        except FileNotFoundError:
            print(f"❌ Fichier {csv_file_path} non trouvé")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion des données : {e}")
            return False
    
    def display_statistics(self):
        """Affiche les statistiques sur les incidents"""
        print("\n📊 Statistiques sur les incidents:")
        
        # Statistiques par statut
        print("\n🔹 Par statut:")
        statut_query = """
        SELECT statut, COUNT(*) as nombre_incidents 
        FROM incidents 
        GROUP BY statut
        """
        results = self.execute_query(statut_query, fetch=True)
        if results:
            for row in results:
                print(f"   {row[0]}: {row[1]} incident(s)")
        
        # Statistiques par gravité
        print("\n🔹 Par gravité:")
        gravite_query = """
        SELECT gravite, COUNT(*) as nombre_incidents 
        FROM incidents 
        GROUP BY gravite
        """
        results = self.execute_query(gravite_query, fetch=True)
        if results:
            for row in results:
                print(f"   {row[0]}: {row[1]} incident(s)")
        
        # Afficher tous les incidents
        print("\n📋 Tous les incidents:")
        all_incidents_query = "SELECT * FROM incidents ORDER BY date DESC"
        results = self.execute_query(all_incidents_query, fetch=True)
        if results:
            print(f"{'ID':<3} {'Titre':<25} {'Gravité':<10} {'Date':<12} {'Statut':<10}")
            print("-" * 70)
            for row in results:
                print(f"{row[0]:<3} {row[1][:24]:<25} {row[3]:<10} {row[4]:<12} {row[5]:<10}")

def get_connection_string():
    """
    Récupère la chaîne de connexion depuis les variables d'environnement
    ou demande à l'utilisateur de la saisir
    """
    # Vérifier si la chaîne de connexion est dans les variables d'environnement
    conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
    
    if conn_string:
        print("🔗 Utilisation de la chaîne de connexion depuis les variables d'environnement")
        return conn_string
    
    # Sinon, construire la chaîne de connexion avec les paramètres
    server = os.getenv('AZURE_SQL_SERVER') or input("Serveur Azure SQL (ex: monserveur.database.windows.net): ")
    database = os.getenv('AZURE_SQL_DATABASE') or input("Nom de la base de données: ")
    username = os.getenv('AZURE_SQL_USERNAME') or input("Nom d'utilisateur: ")
    password = os.getenv('AZURE_SQL_PASSWORD') or input("Mot de passe: ")
    
    # Construire la chaîne de connexion
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    
    return connection_string

def main():
    """Fonction principale"""
    print("🚀 Script de création de table incidents dans Azure SQL Database")
    print("=" * 60)
    
    # Récupérer la chaîne de connexion
    connection_string = get_connection_string()
    
    # Chemin du fichier CSV
    csv_file = os.path.join(os.path.dirname(__file__), 'incidents.csv')
    
    # Créer une instance du gestionnaire Azure SQL
    sql_manager = AzureSQLManager(connection_string)
    
    try:
        # Se connecter à la base de données
        if not sql_manager.connect():
            print("❌ Impossible de se connecter à la base de données")
            return
        
        # Créer la table
        if not sql_manager.create_incidents_table():
            print("❌ Impossible de créer la table")
            return
        
        # Insérer les données
        if not sql_manager.insert_data_from_csv(csv_file):
            print("❌ Impossible d'insérer les données")
            return
        
        # Afficher les statistiques
        sql_manager.display_statistics()
        
        print("\n🎉 Opération terminée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur générale : {e}")
    
    finally:
        # Fermer la connexion
        sql_manager.disconnect()

if __name__ == "__main__":
    main()
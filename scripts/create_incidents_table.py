#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer la table incidents dans Azure SQL Database
"""

import os
import pyodbc
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def get_connection_string():
    """Récupère la chaîne de connexion depuis les variables d'environnement"""
    conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
    if conn_string:
        return conn_string
    else:
        raise ValueError("Variable d'environnement AZURE_SQL_CONNECTION_STRING manquante")

def create_incidents_table():
    """Crée la table incidents dans la base de données Azure SQL"""
    
    # SQL pour créer la table incidents
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='incidents' AND xtype='U')
    BEGIN
        CREATE TABLE incidents (
            id INT PRIMARY KEY,
            titre NVARCHAR(255) NOT NULL,
            description NVARCHAR(MAX),
            gravite NVARCHAR(50) NOT NULL,
            date DATE NOT NULL DEFAULT GETDATE(),
            statut NVARCHAR(50) NOT NULL DEFAULT 'Nouveau',
            date_creation DATETIME2 DEFAULT GETDATE(),
            date_modification DATETIME2 DEFAULT GETDATE()
        );
        
        -- Index pour améliorer les performances de recherche
        CREATE INDEX IX_incidents_date ON incidents(date DESC);
        CREATE INDEX IX_incidents_statut ON incidents(statut);
        CREATE INDEX IX_incidents_gravite ON incidents(gravite);
        
        PRINT 'Table incidents créée avec succès avec ses index';
    END
    ELSE
    BEGIN
        PRINT 'Table incidents existe déjà';
    END
    """
    
    connection = None
    try:
        print("🔧 Connexion à la base de données Azure SQL...")
        connection_string = get_connection_string()
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        
        print("🔄 Création de la table incidents...")
        cursor.execute(create_table_sql)
        connection.commit()
        
        # Vérifier que la table a bien été créée
        cursor.execute("SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'incidents'")
        result = cursor.fetchone()
        
        if result[0] == 1:
            print("✅ Table incidents créée ou vérifiée avec succès")
            
            # Afficher la structure de la table
            cursor.execute("""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE, 
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'incidents' 
                ORDER BY ORDINAL_POSITION
            """)
            
            print("\n📋 Structure de la table incidents:")
            print("-" * 60)
            for row in cursor.fetchall():
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {row[3]}" if row[3] else ""
                print(f"  {row[0]:<20} {row[1]:<15} {nullable}{default}")
            print("-" * 60)
            
        else:
            print("❌ Erreur : La table incidents n'a pas pu être créée")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table : {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    try:
        create_incidents_table()
        print("\n🎉 Script terminé avec succès!")
    except Exception as e:
        print(f"\n💥 Échec du script: {e}")
        exit(1)
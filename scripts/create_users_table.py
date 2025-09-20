#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer la table users dans Azure SQL Database
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer le gestionnaire de base de données de l'application
from app import DatabaseManager

def create_users_table():
    """Crée la table users dans Azure SQL Database"""
    print("📋 Création de la table users dans Azure SQL Database")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    try:
        # Créer une instance du gestionnaire de base de données
        db_manager = DatabaseManager()
        
        print("✅ Connexion à Azure SQL Database réussie")
        
        # Vérifier si la table users existe déjà
        check_table_query = """
        SELECT COUNT(*) as count 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'users'
        """
        
        result = db_manager.execute_query(check_table_query, fetch=True)
        if result and result[0]['count'] > 0:
            print("⚠️ La table 'users' existe déjà")
            response = input("Voulez-vous la recréer ? (y/N): ").lower()
            if response != 'y':
                print("🚫 Opération annulée")
                return True
            
            # Supprimer la table existante
            drop_table_query = "DROP TABLE users"
            db_manager.execute_query(drop_table_query)
            print("🗑️ Ancienne table users supprimée")
        
        # Créer la table users
        create_table_query = """
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(50) UNIQUE NOT NULL,
            email NVARCHAR(100) UNIQUE NOT NULL,
            password_hash NVARCHAR(255) NOT NULL,
            nom_complet NVARCHAR(100) NOT NULL,
            role NVARCHAR(50) DEFAULT 'user',
            date_creation DATETIME DEFAULT GETDATE(),
            actif BIT DEFAULT 1
        );
        """
        
        db_manager.execute_query(create_table_query)
        print("✅ Table 'users' créée avec succès")
        
        # Insérer un utilisateur administrateur par défaut
        insert_admin_query = """
        INSERT INTO users (username, email, password_hash, nom_complet, role) 
        VALUES (?, ?, ?, ?, ?)
        """
        
        # Mot de passe par défaut : admin123 (à changer en production)
        # En production, utilisez un hashage sécurisé comme bcrypt
        admin_params = (
            'admin',
            'admin@incidents.local',
            'admin123',  # À hasher en production
            'Administrateur Système',
            'admin'
        )
        
        db_manager.execute_query(insert_admin_query, admin_params)
        print("👤 Utilisateur administrateur par défaut créé (admin/admin123)")
        
        # Afficher la structure de la table
        print("\n📊 Structure de la table users :")
        structure_query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'users'
        ORDER BY ORDINAL_POSITION
        """
        
        columns = db_manager.execute_query(structure_query, fetch=True)
        if columns:
            print(f"{'Colonne':<20} {'Type':<15} {'Null':<8} {'Défaut':<15}")
            print("-" * 60)
            for col in columns:
                nullable = "OUI" if col['IS_NULLABLE'] == 'YES' else "NON"
                default = col['COLUMN_DEFAULT'] or ''
                print(f"{col['COLUMN_NAME']:<20} {col['DATA_TYPE']:<15} {nullable:<8} {default:<15}")
        
        print("\n🎉 Table users créée et configurée avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table users : {e}")
        return False
    
    # Pas besoin de disconnect avec DatabaseManager

def main():
    """Fonction principale"""
    if create_users_table():
        print("\n✅ Création de la table users réussie !")
        print("\n📝 Prochaines étapes :")
        print("1. Modifier app.py pour utiliser la base de données pour l'authentification")
        print("2. Créer la page d'enregistrement")
        print("3. Implémenter le hashage des mots de passe")
    else:
        print("\n❌ Création de la table users échouée !")
        sys.exit(1)

if __name__ == "__main__":
    main()
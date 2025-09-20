#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour migrer les utilisateurs du fichier CSV vers Azure SQL Database
"""

import os
import sys
import csv
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('.')

def migrate_users_from_csv():
    """Migre les utilisateurs depuis users.csv vers Azure SQL"""
    print("📋 Migration des utilisateurs CSV vers Azure SQL Database")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier si le fichier users.csv existe
    users_csv = 'users.csv'
    if not os.path.exists(users_csv):
        print(f"⚠️ Fichier {users_csv} non trouvé")
        print("🔄 Aucune migration nécessaire")
        return True
    
    try:
        # Importer les fonctions nécessaires
        from app import create_user, get_user_by_username, hash_password
        
        print(f"📖 Lecture du fichier {users_csv}...")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        with open(users_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', '').strip()
                nom_complet = row.get('nom_complet', '').strip()
                role = row.get('role', 'user').strip()
                
                if not all([username, email, password, nom_complet]):
                    print(f"⚠️ Données manquantes pour l'utilisateur {username}, ignoré")
                    skipped_count += 1
                    continue
                
                # Vérifier si l'utilisateur existe déjà
                existing_user = get_user_by_username(username)
                if existing_user:
                    print(f"⚠️ Utilisateur {username} existe déjà, ignoré")
                    skipped_count += 1
                    continue
                
                # Créer l'utilisateur (le mot de passe sera hashé automatiquement)
                success, message = create_user(username, email, password, nom_complet, role)
                
                if success:
                    print(f"✅ Utilisateur {username} migré avec succès")
                    migrated_count += 1
                else:
                    print(f"❌ Erreur pour {username}: {message}")
                    error_count += 1
        
        # Résumé de la migration
        print(f"\n📊 Résumé de la migration :")
        print(f"   ✅ Migrés : {migrated_count}")
        print(f"   ⚠️ Ignorés : {skipped_count}")
        print(f"   ❌ Erreurs : {error_count}")
        
        if migrated_count > 0:
            print(f"\n🎉 Migration terminée ! {migrated_count} utilisateur(s) migré(s)")
            
            # Optionnel : Renommer le fichier CSV
            backup_file = f"{users_csv}.backup"
            os.rename(users_csv, backup_file)
            print(f"📦 Fichier CSV sauvegardé vers {backup_file}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("💡 Assurez-vous que app.py est configuré correctement")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        return False

def create_sample_users():
    """Crée des utilisateurs d'exemple si aucun n'existe"""
    try:
        from app import get_user_by_username, create_user
        
        # Vérifier si des utilisateurs existent déjà
        if get_user_by_username('admin'):
            print("ℹ️ Des utilisateurs existent déjà")
            return True
        
        print("👥 Création d'utilisateurs d'exemple...")
        
        sample_users = [
            {
                'username': 'admin',
                'email': 'admin@incidents.local',
                'password': 'Admin123!',
                'nom_complet': 'Administrateur Système',
                'role': 'admin'
            },
            {
                'username': 'technicien',
                'email': 'tech@incidents.local',
                'password': 'Tech123!',
                'nom_complet': 'Technicien Réseau',
                'role': 'user'
            },
            {
                'username': 'manager',
                'email': 'manager@incidents.local',
                'password': 'Manager123!',
                'nom_complet': 'Manager IT',
                'role': 'admin'
            }
        ]
        
        for user_data in sample_users:
            success, message = create_user(
                user_data['username'],
                user_data['email'],
                user_data['password'],
                user_data['nom_complet'],
                user_data['role']
            )
            
            if success:
                print(f"✅ Utilisateur {user_data['username']} créé")
            else:
                print(f"❌ Erreur pour {user_data['username']}: {message}")
        
        print("\n👤 Comptes créés :")
        print("   admin / Admin123!")
        print("   technicien / Tech123!")
        print("   manager / Manager123!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs d'exemple : {e}")
        return False

def main():
    """Fonction principale"""
    print("🔄 Script de migration des utilisateurs")
    print("=" * 40)
    
    # Migrer depuis CSV s'il existe
    if not migrate_users_from_csv():
        print("❌ Migration échouée")
        return
    
    # Créer des utilisateurs d'exemple si nécessaire
    if not create_sample_users():
        print("❌ Création des utilisateurs d'exemple échouée")
        return
    
    print("\n🎉 Migration terminée avec succès !")

if __name__ == "__main__":
    main()
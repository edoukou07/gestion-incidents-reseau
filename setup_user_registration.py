#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuration pour l'enregistrement d'utilisateurs avec Azure SQL
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def install_dependencies():
    """Installe les nouvelles dépendances"""
    print("📦 Installation des nouvelles dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances : {e}")
        return False

def create_users_table():
    """Crée la table users via le script dédié"""
    print("🗃️ Création de la table users...")
    try:
        script_path = os.path.join("scripts", "create_users_table.py")
        if os.path.exists(script_path):
            subprocess.check_call([sys.executable, script_path])
            return True
        else:
            print(f"❌ Script {script_path} non trouvé")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création de la table users : {e}")
        return False

def test_authentication():
    """Test basique des fonctionnalités d'authentification"""
    print("🧪 Test des fonctionnalités d'authentification...")
    
    try:
        # Import local des fonctions
        sys.path.append('.')
        from app import hash_password, verify_password, validate_email, validate_password
        
        # Test du hashage
        password = "Test123!"
        hashed = hash_password(password)
        if verify_password(password, hashed):
            print("✅ Hashage et vérification des mots de passe : OK")
        else:
            print("❌ Problème avec le hashage des mots de passe")
            return False
        
        # Test de validation email
        if validate_email("test@example.com") and not validate_email("invalid-email"):
            print("✅ Validation des emails : OK")
        else:
            print("❌ Problème avec la validation des emails")
            return False
        
        # Test de validation mot de passe
        valid, _ = validate_password("Test123!")
        invalid, _ = validate_password("weak")
        if valid and not invalid:
            print("✅ Validation des mots de passe : OK")
        else:
            print("❌ Problème avec la validation des mots de passe")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("💡 Assurez-vous que toutes les dépendances sont installées")
        return False
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        return False

def display_usage_instructions():
    """Affiche les instructions d'utilisation"""
    print("\n" + "="*60)
    print("📋 SYSTÈME D'ENREGISTREMENT CONFIGURÉ")
    print("="*60)
    
    print("\n🎯 Nouvelles fonctionnalités :")
    print("✅ Page d'enregistrement des utilisateurs")
    print("✅ Authentification via Azure SQL Database")
    print("✅ Hashage sécurisé des mots de passe (bcrypt)")
    print("✅ Validation des données utilisateur")
    print("✅ Gestion des rôles (user/admin)")
    
    print("\n🌐 Pages disponibles :")
    print("• http://localhost:5000/login - Page de connexion")
    print("• http://localhost:5000/register - Page d'enregistrement")
    print("• http://localhost:5000/ - Tableau de bord (après connexion)")
    
    print("\n👤 Compte administrateur par défaut :")
    print("• Nom d'utilisateur : admin")
    print("• Mot de passe : admin123")
    print("• Rôle : admin")
    
    print("\n🔐 Exigences du mot de passe :")
    print("• Au moins 8 caractères")
    print("• Au moins une majuscule")
    print("• Au moins une minuscule")
    print("• Au moins un chiffre")
    
    print("\n🚀 Pour démarrer l'application :")
    print("   python app.py")
    
    print("\n⚠️ Notes importantes :")
    print("• Les mots de passe sont hashés avec bcrypt")
    print("• Les emails doivent être uniques")
    print("• Les noms d'utilisateur doivent être uniques")
    print("• La base de données Azure SQL est requise")

def main():
    """Fonction principale"""
    print("🔧 Configuration du système d'enregistrement utilisateur")
    print("=" * 60)
    
    # Vérifier les variables d'environnement
    load_dotenv()
    if not os.getenv('AZURE_SQL_CONNECTION_STRING'):
        print("⚠️ Fichier .env non configuré ou variable manquante")
        print("📝 Assurez-vous que AZURE_SQL_CONNECTION_STRING est configuré")
        print("📖 Consultez AZURE_SQL_README.md pour la configuration")
        return
    
    # Installer les dépendances
    if not install_dependencies():
        print("❌ Configuration échouée : problème d'installation")
        return
    
    # Créer la table users
    if not create_users_table():
        print("❌ Configuration échouée : problème de création de table")
        return
    
    # Tester les fonctionnalités
    if not test_authentication():
        print("❌ Configuration échouée : problème de test")
        return
    
    # Afficher les instructions
    display_usage_instructions()
    
    print("\n🎉 Configuration terminée avec succès !")

if __name__ == "__main__":
    main()
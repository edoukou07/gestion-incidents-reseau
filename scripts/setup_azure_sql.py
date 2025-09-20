#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation et de configuration pour Azure SQL Database
"""

import os
import subprocess
import sys

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print("📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation des dépendances : {e}")
        return False

def create_env_file():
    """Crée le fichier .env à partir du template"""
    env_file = ".env"
    env_example = ".env.example"
    
    if os.path.exists(env_file):
        print("⚠️  Le fichier .env existe déjà")
        response = input("Voulez-vous le remplacer ? (y/N): ").lower()
        if response != 'y':
            print("📝 Fichier .env conservé")
            return True
    
    try:
        with open(env_example, 'r') as example:
            content = example.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print(f"✅ Fichier .env créé à partir de {env_example}")
        print("📝 IMPORTANT: Éditez le fichier .env avec vos paramètres de connexion Azure SQL")
        return True
        
    except FileNotFoundError:
        print(f"❌ Fichier {env_example} non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env : {e}")
        return False

def update_gitignore():
    """Ajoute .env au .gitignore s'il n'y est pas déjà"""
    gitignore_file = ".gitignore"
    env_entry = ".env"
    
    try:
        # Lire le contenu existant du .gitignore
        existing_content = ""
        if os.path.exists(gitignore_file):
            with open(gitignore_file, 'r') as f:
                existing_content = f.read()
        
        # Vérifier si .env est déjà dans le .gitignore
        if env_entry in existing_content:
            print("✅ .env est déjà dans .gitignore")
            return True
        
        # Ajouter .env au .gitignore
        with open(gitignore_file, 'a') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write(f"{env_entry}\n")
        
        print("✅ .env ajouté au .gitignore")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du .gitignore : {e}")
        return False

def display_instructions():
    """Affiche les instructions d'utilisation"""
    print("\n" + "="*60)
    print("📋 INSTRUCTIONS D'UTILISATION")
    print("="*60)
    print("\n1. 📝 Configurez votre chaîne de connexion:")
    print("   - Ouvrez le fichier .env")
    print("   - Remplissez les paramètres de votre base Azure SQL")
    print("   - Exemple de chaîne de connexion:")
    print('   AZURE_SQL_CONNECTION_STRING="DRIVER={ODBC Driver 18 for SQL Server};SERVER=monserveur.database.windows.net;DATABASE=incidents_db;UID=admin_user;PWD=MotDePasse123!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"')
    
    print("\n2. 🔧 Vérifiez que ODBC Driver 18 for SQL Server est installé:")
    print("   - Windows: Téléchargez depuis le site Microsoft")
    print("   - Linux: sudo apt-get install msodbcsql18")
    print("   - macOS: brew install msodbcsql18")
    
    print("\n3. 🚀 Exécutez le script:")
    print("   python azure_sql_incidents.py")
    
    print("\n4. 📊 Le script va:")
    print("   - Se connecter à votre base Azure SQL")
    print("   - Créer la table incidents")
    print("   - Insérer les données du fichier incidents.csv")
    print("   - Afficher les statistiques")
    
    print("\n⚠️  SÉCURITÉ:")
    print("   - Ne jamais commiter le fichier .env")
    print("   - Utilisez des mots de passe forts")
    print("   - Configurez les règles de pare-feu Azure SQL")

def main():
    """Fonction principale d'installation"""
    print("🔧 Configuration pour Azure SQL Database")
    print("="*40)
    
    # Installer les dépendances
    if not install_dependencies():
        return
    
    # Créer le fichier .env
    if not create_env_file():
        return
    
    # Mettre à jour .gitignore
    update_gitignore()
    
    # Afficher les instructions
    display_instructions()
    
    print("\n🎉 Configuration terminée !")
    print("📝 N'oubliez pas de configurer votre fichier .env avant d'exécuter le script principal.")

if __name__ == "__main__":
    main()
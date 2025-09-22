# 🔄 Migration vers Azure SQL Database

## ✨ Modifications apportées

Votre application Flask a été modifiée pour utiliser **Azure SQL Database** au lieu du fichier CSV local.

## 📁 Nouveaux fichiers

### 🔧 Application modifiée :
- **`app_azure_sql.py`** - Version de l'application utilisant Azure SQL Database

### 🗄️ Gestion de base de données :
- **`azure_sql_incidents.py`** - Script autonome pour créer la table et insérer les données
- **`migrate_to_azure_sql.py`** - Script de migration des données CSV vers Azure SQL
- **`setup_azure_sql.py`** - Script d'installation et de configuration

### ⚙️ Configuration :
- **`.env.example`** - Template de configuration pour Azure SQL
- **`requirements.txt`** - Mis à jour avec `pyodbc==5.0.1`

## 🚀 Instructions d'utilisation

### 1. Configuration initiale :
```powershell
# Installation et configuration
python setup_azure_sql.py
```

### 2. Configurez votre fichier `.env` :
```env
AZURE_SQL_CONNECTION_STRING="DRIVER={ODBC Driver 18 for SQL Server};SERVER=votre-serveur.database.windows.net;DATABASE=votre-base;UID=votre-user;PWD=votre-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

### 3. Migration des données :
```powershell
# Créer la table et migrer les données
python migrate_to_azure_sql.py
```

### 4. Lancer l'application :
```powershell
# Version Azure SQL
python app_azure_sql.py
```

## 🔄 Principales modifications

### ✅ Fonctionnalités ajoutées :
- **Classe `DatabaseManager`** : Gestion complète de la connexion Azure SQL
- **Gestion d'erreurs** : Messages d'erreur informatifs pour l'utilisateur
- **Variables d'environnement** : Configuration sécurisée
- **Connexions sécurisées** : Chiffrement SSL/TLS activé

### 🔄 Fonctions modifiées :
- **`lire_incidents()`** : Lit depuis Azure SQL avec tri par date
- **`ajouter_incident()`** : Insère directement en base de données  
- **`obtenir_incident_par_id()`** : Nouvelle fonction pour récupérer un incident
- **Routes protégées** : Meilleure gestion des erreurs de base de données

### 🛡️ Sécurité améliorée :
- Connexions chiffrées (`Encrypt=yes`)
- Variables d'environnement pour les credentials
- Protection contre les injections SQL (requêtes paramétrées)
- Gestion des timeouts de connexion

## 📊 Structure de la base de données

```sql
CREATE TABLE incidents (
    id INT PRIMARY KEY,
    titre NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX),
    gravite NVARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    statut NVARCHAR(50) NOT NULL
);
```

## 🔧 Prérequis

### Driver ODBC :
- **Windows** : Microsoft ODBC Driver 18 for SQL Server
- **Linux** : `sudo apt-get install msodbcsql18`
- **macOS** : `brew install msodbcsql18`

### Python packages :
```
Flask==2.3.3
pandas==2.1.1
python-dotenv==1.0.0
pyodbc==5.0.1
```

## 🆚 Comparaison des versions

| Fonctionnalité | Version CSV | Version Azure SQL |
|---------------|-------------|-------------------|
| **Stockage** | Fichier local | Base de données cloud |
| **Performance** | Limitée | Optimisée |
| **Concurrence** | Problématique | Native |
| **Sécurité** | Basique | Avancée |
| **Backup** | Manuel | Automatique |
| **Scalabilité** | Limitée | Élastique |

## 🎯 Avantages d'Azure SQL

- **🌐 Accessibilité** : Données accessibles depuis n'importe où
- **🔒 Sécurité** : Chiffrement et authentification avancés  
- **📈 Performance** : Requêtes optimisées et indexation
- **🔄 Sauvegarde** : Sauvegardes automatiques et point-in-time recovery
- **📊 Monitoring** : Outils de surveillance intégrés
- **🔧 Maintenance** : Mise à jour automatique

## 🐛 Dépannage

### Erreur de connexion :
1. Vérifiez votre chaîne de connexion
2. Assurez-vous que votre IP est autorisée dans le firewall Azure SQL
3. Vérifiez que ODBC Driver 18 est installé

### Problème de performance :
1. Vérifiez la latence réseau
2. Optimisez vos requêtes
3. Considérez l'indexation

### Erreur d'authentification :
1. Vérifiez vos identifiants
2. Assurez-vous que l'utilisateur a les permissions nécessaires
3. Vérifiez l'expiration du mot de passe
# Intégration Azure Function - Migration Automatique des Utilisateurs

## Vue d'ensemble
L'application Flask est maintenant configurée pour appeler automatiquement votre Azure Function au démarrage afin de migrer les utilisateurs depuis Azure Blob Storage vers la base de données Azure SQL.

## Fonctionnement

### 1. Démarrage Automatique
Quand l'application Flask démarre, elle :
- ✅ Appelle automatiquement l'Azure Function de migration
- ✅ Migre les utilisateurs depuis `appfiles/users.csv` dans Azure Blob Storage
- ✅ Crée automatiquement la table `users` si elle n'existe pas
- ✅ Affiche les résultats de la migration dans la console

### 2. Configuration de l'Appel
```python
# URL de votre Azure Function
azure_function_url = "https://testhttpinc.azurewebsites.net/api/migrate-csv-from-blob"

# Paramètres utilisés
params = {
    "container_name": "appfiles",
    "blob_name": "users.csv"
}
```

### 3. Gestion des Erreurs
L'intégration gère plusieurs types d'erreurs :
- **Timeout** : Si l'appel prend plus de 60 secondes
- **Erreur de connexion** : Si l'Azure Function n'est pas accessible
- **Erreur HTTP** : Si la fonction retourne une erreur
- **Erreurs inattendues** : Toute autre exception

## Logs de Démarrage
Au démarrage de l'application, vous verrez des logs comme :

```
🔧 === INITIALISATION DE L'APPLICATION ===
📅 Démarrage de l'application de gestion des incidents réseau
🚀 Appel de la fonction Azure pour la migration des utilisateurs...
📡 URL: https://testhttpinc.azurewebsites.net/api/migrate-csv-from-blob
📦 Container: appfiles
📄 Fichier: users.csv
✅ Réponse de la fonction Azure reçue avec succès
📊 Utilisateurs migrés : 3
⚠️ Utilisateurs ignorés : 0
❌ Erreurs : 0
🎉 Migration des utilisateurs terminée avec succès !
   📡 Source: Azure Blob Storage (appfiles/users.csv)
   ✅ Utilisateurs migrés : 3
   ⚠️ Utilisateurs ignorés : 0
   ❌ Erreurs rencontrées : 0
   🎉 Migration terminée avec succès ! 3 utilisateur(s) ajouté(s) à la base de données
✅ === INITIALISATION TERMINÉE ===
```

## Route Administrative
Une route `/admin/migrate-users` a été ajoutée pour permettre aux administrateurs de déclencher manuellement la migration :

### Accès
- **URL** : `/admin/migrate-users`
- **Méthode** : GET
- **Autorisation** : Réservé aux utilisateurs avec le rôle `admin`
- **Redirection** : Vers la page principale après exécution

### Utilisation
```bash
# Accéder à l'URL depuis un navigateur (en étant connecté comme admin)
http://localhost:5000/admin/migrate-users
```

## Dépendances Ajoutées
La bibliothèque `requests` a été ajoutée pour effectuer les appels HTTP :

```python
import requests
import json
import time
```

### Installation
Si `requests` n'est pas installé, ajoutez-le à votre `requirements.txt` :
```
requests>=2.31.0
```

## Format du Fichier CSV Attendu
Le fichier `users.csv` dans le container `appfiles` doit avoir le format suivant :

```csv
username,email,password,nom_complet,role
admin_user,admin@example.com,admin123,Administrator,admin
john_doe,john@example.com,password123,John Doe,user
jane_smith,jane@example.com,secret456,Jane Smith,user
```

## Avantages de cette Intégration

### 1. **Automatisation Complète**
- Plus besoin d'appeler manuellement l'Azure Function
- Migration automatique à chaque démarrage de l'application
- Synchronisation automatique des utilisateurs

### 2. **Gestion Centralisée**
- Un seul point de vérité pour les utilisateurs (Azure Blob Storage)
- Mise à jour facile du fichier CSV dans Azure
- Déploiement simplifié

### 3. **Monitoring Intégré**
- Logs détaillés de la migration
- Gestion d'erreurs robuste
- Possibilité de migration manuelle pour les administrateurs

### 4. **Sécurité**
- Migration uniquement au démarrage (évite les appels répétés)
- Route administrative protégée
- Gestion des timeouts et erreurs

## Scénarios d'Utilisation

### 1. **Déploiement Initial**
- Déployez l'application Flask
- Elle créera automatiquement tous les utilisateurs depuis Azure Blob Storage
- Prêt à l'utilisation immédiatement

### 2. **Ajout de Nouveaux Utilisateurs**
- Mettez à jour le fichier `users.csv` dans Azure Blob Storage
- Redémarrez l'application Flask OU utilisez la route `/admin/migrate-users`
- Les nouveaux utilisateurs sont automatiquement créés

### 3. **Maintenance**
- Si un problème survient lors de la migration, consultez les logs
- Utilisez la route administrative pour retenter la migration
- Les utilisateurs existants sont automatiquement ignorés (pas de doublons)

## Configuration des Variables d'Environnement
Assurez-vous que votre Azure Function a accès aux bonnes variables d'environnement :

```
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=...
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

## Troubleshooting

### Problème : Timeout lors de l'appel
**Solution** : Augmentez le timeout ou vérifiez les performances de l'Azure Function

### Problème : Erreur de connexion
**Solution** : Vérifiez que l'URL de l'Azure Function est correcte et accessible

### Problème : Échec de la migration
**Solution** : Consultez les logs de l'Azure Function et vérifiez le format du fichier CSV

### Problème : Utilisateurs non créés
**Solution** : Vérifiez les variables d'environnement de l'Azure Function et la connexion à la base de données
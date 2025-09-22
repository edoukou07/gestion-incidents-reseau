# Migration des Incidents depuis Azure Blob Storage

## Vue d'ensemble

Cette application charge maintenant automatiquement les données d'incidents depuis un container Azure Blob Storage vers une base de données Azure SQL au démarrage de l'application, en utilisant un service principal Azure pour l'authentification.

## Architecture de la solution

```
Azure Blob Storage          Application Flask          Azure SQL Database
     (incidents.csv)    →    (Service Principal)    →     (Table incidents)
         ↓                         ↓                          ↓
    Fichier CSV              Migration automatique      Stockage persistant
    Container: incidents-data    au démarrage              & opérations CRUD
```

## Fonctionnement

### Au démarrage de l'application

1. **Initialisation** : L'application se connecte à Azure Blob Storage avec le service principal
2. **Vérification** : Recherche du fichier `incidents.csv` dans le container configuré
3. **Migration** : Si le fichier existe et que la table est vide, les données sont migrées
4. **Opérations** : L'application utilise ensuite uniquement la base de données pour toutes les opérations

### Prévention des doublons

- La migration ne s'exécute que si la table `incidents` est vide
- Si la table contient déjà des données, la migration est ignorée
- Cela évite les doublons lors des redémarrages de l'application

## Configuration requise

### 1. Service Principal Azure

Créez un service principal avec les permissions appropriées :

```bash
# Créer le service principal
az ad sp create-for-rbac --name "incidents-blob-reader" --role "Storage Blob Data Contributor"

# Assigner les permissions au storage account
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee <OBJECT_ID_DU_SERVICE_PRINCIPAL> \
    --scope "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Storage/storageAccounts/<STORAGE_ACCOUNT>"
```

### 2. Variables d'environnement

Configurez le fichier `.env` avec :

```env
# Azure SQL Database
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:votre-serveur.database.windows.net,1433;Database=votre-database;Uid=votre-username;Pwd=votre-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

# Service Principal Azure
AZURE_CLIENT_ID=votre-client-id
AZURE_CLIENT_SECRET=votre-client-secret
AZURE_TENANT_ID=votre-tenant-id

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=votre-storage-account
AZURE_STORAGE_CONTAINER_NAME=incidents-data
```

### 3. Structure du fichier CSV

Le fichier `incidents.csv` dans le blob storage doit avoir cette structure :

```csv
id,titre,description,gravite,date,statut
1,Perte de signal Wi-Fi,Intermittence sur le réseau Wi-Fi dans la zone A,Majeur,2025-09-18,Nouveau
2,Serveur de base de données lent,Lenteur observée sur les requêtes de base de données,Critique,2025-09-19,En cours
```

### 4. Table Azure SQL Database

La table `incidents` sera créée automatiquement avec la structure :

```sql
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
```

## Procédure de déploiement

### 1. Préparation de la base de données

```bash
# Exécuter le script de création de table
cd gestion-incidents-reseau
python scripts/create_incidents_table.py
```

### 2. Upload des données initiales

```powershell
# Uploader le fichier d'exemple vers blob storage
.\upload-incidents-to-blob.ps1 -StorageAccountName "votre-storage-account"
```

Ou utiliser le script Python :
```bash
python upload_incidents_to_blob.py
```

### 3. Configuration de l'application

1. Copiez `.env.example` vers `.env`
2. Remplissez toutes les variables d'environnement
3. Installez les dépendances : `pip install -r requirements.txt`

### 4. Démarrage

```bash
python app.py
```

## Logs et monitoring

L'application affiche des logs détaillés lors de la migration :

```
🔧 === INITIALISATION DE L'APPLICATION ===
📅 Démarrage de l'application de gestion des incidents réseau
🚀 Appel de la fonction Azure pour la migration des utilisateurs...
✅ Migration des utilisateurs terminée avec succès !
🔄 === MIGRATION DES INCIDENTS ===
📦 Recherche des fichiers d'incidents dans Azure Blob Storage...
⬇️ Téléchargement de incidents.csv...
📊 8 incidents trouvés dans le blob storage
🔄 Début de la migration des incidents...
📊 === RÉSUMÉ DE LA MIGRATION ===
✅ Incidents migrés avec succès : 8
❌ Incidents avec erreurs : 0
📈 Total traités : 8
🎉 Migration des incidents terminée avec succès !
✅ === INITIALISATION TERMINÉE ===
```

## Avantages de cette approche

1. **Automatisation** : Migration automatique au démarrage
2. **Sécurité** : Utilisation d'un service principal avec permissions minimales
3. **Performance** : Données en base pour des accès rapides
4. **Fiabilité** : Prévention des doublons et gestion d'erreurs
5. **Traçabilité** : Logs détaillés de toutes les opérations
6. **Flexibilité** : Possibilité de mettre à jour les données en rechargeant le fichier CSV

## Dépannage

### Erreurs communes

1. **"Variables d'environnement Azure manquantes"**
   - Vérifiez que le fichier `.env` existe et contient toutes les variables
   
2. **"Erreur lors de la vérification de la table incidents"**
   - Exécutez `python scripts/create_incidents_table.py`
   
3. **"Fichier incidents.csv non trouvé dans le blob storage"**
   - Uploadez le fichier avec `upload-incidents-to-blob.ps1` ou `upload_incidents_to_blob.py`
   
4. **"Migration terminée avec des avertissements"**
   - Vérifiez les logs pour identifier les incidents problématiques
   - Corrigez le fichier CSV et relancez l'application

### Réinitialisation

Pour forcer une nouvelle migration :

```sql
-- Vider la table incidents
DELETE FROM incidents;
```

Puis relancer l'application.
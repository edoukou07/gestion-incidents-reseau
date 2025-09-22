# Configuration Azure Blob Storage avec Service Principal

## Prérequis

1. **Compte Azure** avec permissions pour créer des ressources
2. **Azure Storage Account** créé
3. **Service Principal** avec les permissions appropriées
4. **Python 3.7+** avec les packages requis

## Configuration du Service Principal

### 1. Créer un Service Principal

```bash
# Via Azure CLI
az ad sp create-for-rbac --name "incidents-blob-reader" --role "Storage Blob Data Contributor"
```

Cette commande retournera :
```json
{
  "appId": "12345678-1234-5678-9012-123456789abc",
  "displayName": "incidents-blob-reader",
  "password": "your-secret-value",
  "tenant": "87654321-4321-8765-2109-987654321cba"
}
```

### 2. Assigner les permissions au Storage Account

```bash
# Remplacez les valeurs par les vôtres
STORAGE_ACCOUNT_NAME="votre-storage-account"
RESOURCE_GROUP="votre-resource-group"
SP_OBJECT_ID="object-id-du-service-principal"

# Assigner le rôle Storage Blob Data Contributor
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee $SP_OBJECT_ID \
    --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT_NAME"
```

## Configuration de l'application

### 1. Créer le fichier .env

Copiez `.env.example` vers `.env` et remplissez les valeurs :

```bash
cp .env.example .env
```

Modifiez le fichier `.env` :

```env
# Configuration pour Azure Blob Storage avec Service Principal
AZURE_CLIENT_ID=12345678-1234-5678-9012-123456789abc
AZURE_CLIENT_SECRET=your-secret-value
AZURE_TENANT_ID=87654321-4321-8765-2109-987654321cba

# Azure Storage Account configuration
AZURE_STORAGE_ACCOUNT_NAME=votre-storage-account
AZURE_STORAGE_CONTAINER_NAME=incidents-data
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Uploader le fichier d'exemple

```bash
python upload_incidents_to_blob.py
```

## Structure des données

Le fichier `incidents.csv` dans Azure Blob Storage doit avoir la structure suivante :

```csv
id,titre,description,gravite,date,statut
1,Perte de signal Wi-Fi,Intermittence sur le réseau Wi-Fi dans la zone A,Majeur,2025-09-18,Nouveau
2,Serveur de base de données lent,Lenteur observée sur les requêtes de base de données,Critique,2025-09-19,En cours
```

## Sécurité et Bonnes Pratiques

### 1. Gestion des secrets
- ✅ **Ne jamais** committer le fichier `.env` dans Git
- ✅ Utiliser Azure Key Vault pour la production
- ✅ Rotation régulière des secrets du service principal

### 2. Permissions minimales
- ✅ Le service principal a seulement les permissions `Storage Blob Data Contributor`
- ✅ Accès limité au container spécifique
- ✅ Pas d'accès aux autres ressources Azure

### 3. Monitoring et logs
- ✅ Logs détaillés dans l'application
- ✅ Mécanisme de fallback vers SQL Database
- ✅ Gestion d'erreurs robuste

## Fonctionnement de l'application

1. **Chargement des incidents** :
   - Essaie d'abord de charger depuis Azure Blob Storage
   - En cas d'échec, bascule vers SQL Database
   - Affiche des logs détaillés pour le diagnostic

2. **Format supporté** :
   - CSV avec séparateur virgule
   - Encodage UTF-8
   - Colonnes: id, titre, description, gravite, date, statut

3. **Resilience** :
   - Timeout configurable
   - Retry automatique avec exponential backoff
   - Fallback vers base de données

## Déploiement en production

### Azure App Service
```bash
# Variables d'environnement à configurer
az webapp config appsettings set --resource-group myResourceGroup --name myAppService --settings \
    AZURE_CLIENT_ID="12345678-1234-5678-9012-123456789abc" \
    AZURE_CLIENT_SECRET="your-secret-value" \
    AZURE_TENANT_ID="87654321-4321-8765-2109-987654321cba" \
    AZURE_STORAGE_ACCOUNT_NAME="votre-storage-account" \
    AZURE_STORAGE_CONTAINER_NAME="incidents-data"
```

### Azure Container Instances
```dockerfile
# Utiliser des variables d'environnement dans le dockerfile
ENV AZURE_CLIENT_ID=""
ENV AZURE_CLIENT_SECRET=""
ENV AZURE_TENANT_ID=""
ENV AZURE_STORAGE_ACCOUNT_NAME=""
ENV AZURE_STORAGE_CONTAINER_NAME=""
```

## Troubleshooting

### Erreurs courantes

1. **"Variables d'environnement Azure manquantes"**
   - Vérifiez que le fichier `.env` existe et contient toutes les variables
   - Vérifiez les noms des variables (pas d'espaces)

2. **"This request is not authorized"**
   - Vérifiez les permissions du service principal
   - Vérifiez que le rôle est bien assigné au storage account

3. **"Blob not found"**
   - Vérifiez que le fichier `incidents.csv` existe dans le container
   - Utilisez `upload_incidents_to_blob.py` pour uploader le fichier

4. **"Connection timeout"**
   - Vérifiez la connectivité réseau vers Azure
   - Vérifiez que le storage account est accessible

## Monitoring

L'application affiche des logs détaillés :
- ✅ Tentatives de connexion à Blob Storage
- ✅ Succès/échec du chargement des données  
- ✅ Basculement vers SQL Database
- ✅ Nombre d'incidents chargés

Surveillez ces logs pour détecter les problèmes potentiels.
# Commandes Rapides - Déploiement Azure App Service
# Application: Gestionnaire d'Incidents Réseau

## DÉPLOIEMENT AUTOMATIQUE 🚀
# Exécuter le script PowerShell automatisé
.\deploy-to-azure.ps1

## DÉPLOIEMENT MANUEL ÉTAPE PAR ÉTAPE 🛠️

### 1. Variables de base
```powershell
$resourceGroup = "rg-gestion-incidents"
$appName = "gestion-incidents-$(Get-Random -Minimum 1000 -Maximum 9999)"
$location = "canadacentral"
$planName = "plan-gestion-incidents"
```

### 2. Création des ressources Azure
```powershell
# Groupe de ressources
az group create --name $resourceGroup --location $location

# Plan App Service
az appservice plan create --name $planName --resource-group $resourceGroup --location $location --sku F1 --is-linux

# Application web
az webapp create --resource-group $resourceGroup --plan $planName --name $appName --runtime "PYTHON:3.11" --startup-file "gunicorn --bind=0.0.0.0 --workers=2 app:app"
```

### 3. Configuration
```powershell
# Variables d'environnement
az webapp config appsettings set --resource-group $resourceGroup --name $appName --settings FLASK_ENV=production SECRET_KEY="$(New-Guid)" SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

# Déploiement Git
az webapp deployment source config-local-git --resource-group $resourceGroup --name $appName
```

### 4. Déploiement
```powershell
# Configuration Git
git remote add azure https://$appName.scm.azurewebsites.net/$appName.git

# Déploiement depuis la branche azure-deployment
git add . && git commit -m "Azure deployment" && git push azure azure-deployment:master
```

## COMMANDES DE MAINTENANCE 🔧

### Logs en temps réel
```powershell
az webapp log tail --resource-group $resourceGroup --name $appName
```

### Redémarrage
```powershell
az webapp restart --resource-group $resourceGroup --name $appName
```

### Redéploiement rapide
```powershell
git add . && git commit -m "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')" && git push azure azure-deployment:master
```

### État de l'application
```powershell
az webapp show --resource-group $resourceGroup --name $appName --query "{name:name, state:state, defaultHostName:defaultHostName}" --output table
```

### Télécharger les logs
```powershell
az webapp log download --resource-group $resourceGroup --name $appName
```

## URLS D'ACCÈS 🌐

- **Application**: https://$appName.azurewebsites.net
- **Login**: https://$appName.azurewebsites.net/login
- **Health Check**: https://$appName.azurewebsites.net/health
- **Kudu Console**: https://$appName.scm.azurewebsites.net

## UTILISATEURS DE TEST 👥

- **admin** / admin123 (Administrateur)
- **technicien** / tech123 (Technicien)
- **manager** / manager123 (Manager)

## RÉSOLUTION PROBLÈMES 🔍

### Erreur 500
```powershell
# Vérifier les logs
az webapp log tail --resource-group $resourceGroup --name $appName

# Forcer la reconstruction
az webapp deployment source sync --resource-group $resourceGroup --name $appName
```

### Performance lente
```powershell
# Passer au plan Basic
az appservice plan update --resource-group $resourceGroup --name $planName --sku B1
```

### Problème de configuration
```powershell
# Vérifier les variables
az webapp config appsettings list --resource-group $resourceGroup --name $appName --output table
```
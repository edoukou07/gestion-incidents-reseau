# Procédure de Déploiement sur Azure App Service - Région Canada Central

## Application: Gestionnaire d'Incidents Réseau
**Date:** 19 septembre 2025
**Région cible:** Canada Central (canadacentral)

---

## Prérequis

### 1. Outils nécessaires
- Azure CLI 2.53.0+ installé
- Git configuré
- Compte Azure avec abonnement actif
- Python 3.8+ (pour tests locaux)

### 2. Vérification des prérequis
```powershell
# Vérifier Azure CLI
az --version

# Se connecter à Azure
az login

# Vérifier l'abonnement
az account show
```

---

## Phase 1: Préparation de l'Application

### 1.1 Validation des fichiers de configuration
Vérifiez que votre projet contient tous les fichiers nécessaires :

- ✅ `app.py` - Application Flask principale
- ✅ `requirements.txt` - Dépendances Python
- ✅ `config.py` - Configuration Azure
- ✅ `Procfile` - Configuration Gunicorn
- ✅ `.deployment` - Configuration de déploiement Azure
- ✅ `templates/` - Templates HTML Bootstrap
- ✅ `static/` - Fichiers CSS/JS
- ✅ `data/users.csv` - Utilisateurs par défaut
- ✅ `.gitignore` - Exclusions Git

### 1.2 Test local avant déploiement
```powershell
# Se placer dans le répertoire du projet
cd C:\Users\hynco\Desktop\DSG\AZURE_DEV\CODE\AppAz204\gestion_incidents

# Créer un environnement virtuel (recommandé)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Tester l'application localement
python app.py
```

Accédez à `http://localhost:5000` pour vérifier que l'application fonctionne.

---

## Phase 2: Configuration Azure

### 2.1 Création du groupe de ressources
```powershell
# Définir les variables
$resourceGroup = "rg-gestion-incidents"
$appName = "gestion-incidents-$(Get-Random -Minimum 1000 -Maximum 9999)"
$location = "canadacentral"
$planName = "plan-gestion-incidents"

# Créer le groupe de ressources
az group create --name $resourceGroup --location $location
```

### 2.2 Création du plan App Service
```powershell
# Créer le plan App Service (niveau gratuit pour commencer)
az appservice plan create `
    --name $planName `
    --resource-group $resourceGroup `
    --location $location `
    --sku F1 `
    --is-linux
```

### 2.3 Création de l'App Service
```powershell
# Créer l'application web
az webapp create `
    --resource-group $resourceGroup `
    --plan $planName `
    --name $appName `
    --runtime "PYTHON:3.11" `
    --startup-file "gunicorn --bind=0.0.0.0 --workers=2 app:app"
```

---

## Phase 3: Configuration de l'Application

### 3.1 Configuration des variables d'environnement
```powershell
# Configurer les variables d'environnement de production
az webapp config appsettings set `
    --resource-group $resourceGroup `
    --name $appName `
    --settings `
    FLASK_ENV=production `
    SECRET_KEY="$(New-Guid)" `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    ENABLE_ORYX_BUILD=true `
    POST_BUILD_SCRIPT_PATH="deployment.sh"
```

### 3.2 Configuration du déploiement depuis Git local
```powershell
# Configurer Git pour le déploiement
az webapp deployment source config-local-git `
    --resource-group $resourceGroup `
    --name $appName
```

Cette commande retournera une URL Git comme :
`https://$gestion-incidents-1234@gestion-incidents-1234.scm.azurewebsites.net/gestion-incidents-1234.git`

### 3.3 Obtenir les identifiants de déploiement
```powershell
# Obtenir les identifiants de déploiement
az webapp deployment list-publishing-credentials `
    --resource-group $resourceGroup `
    --name $appName `
    --query "{username:publishingUserName, password:publishingPassword}" `
    --output table
```

---

## Phase 4: Déploiement

### 4.1 Configuration Git locale
```powershell
# Ajouter le remote Azure
git remote add azure https://$appName.scm.azurewebsites.net/$appName.git

# Vérifier les remotes
git remote -v
```

### 4.2 Préparation et commit final
```powershell
# Créer une branche dédiée au déploiement
git checkout -b azure-deployment

# Ajouter tous les fichiers
git add .

# Commit final avant déploiement
git commit -m "Production deployment to Azure App Service - Canada Central"

# Vérifier le statut
git status
```

### 4.3 Déploiement vers Azure
```powershell
# Basculer sur la branche de déploiement
git checkout azure-deployment

# Déployer vers Azure depuis la branche azure-deployment
git push azure azure-deployment:master

# Suivre les logs de déploiement
az webapp log tail --resource-group $resourceGroup --name $appName
```

---

## Phase 5: Vérification et Tests

### 5.1 Vérification du déploiement
```powershell
# Obtenir l'URL de l'application
az webapp show --resource-group $resourceGroup --name $appName --query defaultHostName --output tsv
```

### 5.2 Tests de fonctionnement
1. **Test de connexion** : `https://$appName.azurewebsites.net/login`
2. **Test de santé** : `https://$appName.azurewebsites.net/health`
3. **Test des utilisateurs par défaut** :
   - admin / admin123
   - technicien / tech123  
   - manager / manager123

### 5.3 Surveillance des logs
```powershell
# Activer la journalisation
az webapp log config --application-logging filesystem `
    --resource-group $resourceGroup `
    --name $appName

# Voir les logs en temps réel
az webapp log tail --resource-group $resourceGroup --name $appName
```

---

## Phase 6: Configuration Post-Déploiement

### 6.1 Activation HTTPS uniquement
```powershell
# Forcer HTTPS
az webapp update --resource-group $resourceGroup --name $appName --https-only true
```

### 6.2 Configuration du domaine personnalisé (optionnel)
```powershell
# Si vous avez un domaine personnalisé
az webapp config hostname add --resource-group $resourceGroup --name $appName --hostname "incidents.votredomaine.com"
```

### 6.3 Sauvegarde automatique (recommandé)
```powershell
# Configurer la sauvegarde automatique
az webapp config backup create --resource-group $resourceGroup --name $appName --storage-account-url "https://yourstorageaccount.blob.core.windows.net/backups" --backup-name "daily-backup"
```

---

## Phase 7: Optimisation et Monitoring

### 7.1 Mise à l'échelle (si nécessaire)
```powershell
# Passer à un plan payant pour plus de performances
az appservice plan update --resource-group $resourceGroup --name $planName --sku B1

# Activer l'auto-scaling
az monitor autoscale create --resource-group $resourceGroup --resource $appName --min-count 1 --max-count 3 --count 1
```

### 7.2 Configuration Application Insights
```powershell
# Créer Application Insights
az monitor app-insights component create --app insights-gestion-incidents --location $location --resource-group $resourceGroup

# Lier à l'application
az webapp config appsettings set --resource-group $resourceGroup --name $appName --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-key"
```

---

## Commandes de Maintenance

### Redéploiement rapide
```powershell
# Basculer sur la branche de déploiement
git checkout azure-deployment

# Ajouter les modifications et redéployer
git add . && git commit -m "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')" && git push azure azure-deployment:master
```

### Logs de diagnostic
```powershell
az webapp log download --resource-group $resourceGroup --name $appName
```

### Redémarrage de l'application
```powershell
az webapp restart --resource-group $resourceGroup --name $appName
```

---

## Résolution de Problèmes

### Problèmes courants et solutions

1. **Erreur 500 au démarrage**
   ```powershell
   az webapp log tail --resource-group $resourceGroup --name $appName
   ```

2. **Problème de dépendances Python**
   - Vérifier `requirements.txt`
   - Forcer la reconstruction : `az webapp deployment source sync`

3. **Erreur de configuration**
   - Vérifier les variables d'environnement
   - Contrôler le fichier `config.py`

4. **Performance lente**
   - Passer à un plan supérieur
   - Activer Application Insights pour diagnostiquer

---

## URLs Importantes

- **Application** : `https://$appName.azurewebsites.net`
- **Kudu (SCM)** : `https://$appName.scm.azurewebsites.net`
- **Health Check** : `https://$appName.azurewebsites.net/health`
- **Portail Azure** : `https://portal.azure.com`

---

## Coûts Estimés (Région Canada Central)

- **Plan F1 (Gratuit)** : 0 CAD/mois (limité)
- **Plan B1 (Basic)** : ~15 CAD/mois
- **Plan S1 (Standard)** : ~75 CAD/mois
- **Application Insights** : Gratuit jusqu'à 5GB/mois

---

**Note** : Cette procédure a été testée avec l'application Flask de gestion d'incidents configurée avec Bootstrap, authentification CSV et optimisations pandas pour Azure App Service.

**Support** : En cas de problème, consultez la documentation Azure ou contactez le support technique.
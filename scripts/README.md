# 🔧 Scripts d'Automatisation - Gestion des Incidents

## 📋 Scripts Disponibles

### 🚀 **deploy-to-azure.ps1**
**Script principal de déploiement automatisé vers Azure App Service**

#### Usage
```powershell
.\scripts\deploy-to-azure.ps1
```

#### Paramètres optionnels
```powershell
.\scripts\deploy-to-azure.ps1 -ResourceGroupName "mon-rg" -Location "canadacentral" -AppNamePrefix "mon-app"
```

#### Fonctionnalités
- ✅ Création automatique du groupe de ressources
- ✅ Configuration du plan App Service
- ✅ Création de l'application web
- ✅ Configuration des variables d'environnement
- ✅ Déploiement Git automatique
- ✅ Configuration HTTPS forcé
- ✅ Activation des logs
- ✅ Tests de validation

---

### 🌿 **switch-branch.ps1**
**Gestionnaire de branches Git pour faciliter le workflow**

#### Usage
```powershell
# Basculer vers main
.\scripts\switch-branch.ps1 main

# Basculer vers azure-deployment
.\scripts\switch-branch.ps1 azure-deployment

# Déploiement complet avec synchronisation
.\scripts\switch-branch.ps1 deploy

# Synchroniser azure-deployment avec main
.\scripts\switch-branch.ps1 sync

# Voir l'état du repository
.\scripts\switch-branch.ps1 status
```

#### Fonctionnalités
- 🔄 Basculement facile entre branches
- 🚀 Déploiement automatique avec synchronisation
- 📊 État détaillé du repository Git
- 🔗 Synchronisation automatique des branches

---

## 🚀 Déploiement Rapide

### Option 1 - Déploiement direct
```powershell
git checkout azure-deployment
.\scripts\deploy-to-azure.ps1
```

### Option 2 - Avec gestion des branches
```powershell
.\scripts\switch-branch.ps1 deploy
```

---

## 🔧 Maintenance Courante

### Redéploiement après modifications
```powershell
git checkout azure-deployment
git add .
git commit -m "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push azure azure-deployment:master
```

### Synchronisation des branches
```powershell
.\scripts\switch-branch.ps1 sync
```

### Vérification de l'état
```powershell
.\scripts\switch-branch.ps1 status
```

---

## 📋 Prérequis pour les Scripts

### Outils requis
- **Azure CLI** installé et configuré
- **Git** configuré
- **PowerShell** 5.1+ ou PowerShell Core
- **Connexion Azure** active

### Vérification
```powershell
# Vérifier Azure CLI
az --version

# Vérifier la connexion
az account show

# Vérifier Git
git --version
```

---

## 🆘 Résolution de Problèmes

### Erreurs courantes

#### Script bloqué par la politique d'exécution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Erreur de connexion Azure
```powershell
az login
az account set --subscription "votre-subscription-id"
```

#### Problème de permissions Git
```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

---

## 📊 Logs et Debugging

### Activer le mode verbose
```powershell
# Pour PowerShell
$VerbosePreference = "Continue"
.\scripts\deploy-to-azure.ps1

# Pour voir les détails Git
git config --global http.verbose true
```

### Vérifier les logs Azure
```powershell
# Après déploiement
az webapp log tail --resource-group rg-gestion-incidents --name [app-name]
```

---

## 🔄 Workflow Recommandé

1. **Développement** sur `main`
2. **Synchronisation** avec `.\scripts\switch-branch.ps1 sync`
3. **Déploiement** avec `.\scripts\switch-branch.ps1 deploy`
4. **Validation** avec les guides dans `docs/`

---

**💡 Astuce**: Utilisez `.\scripts\switch-branch.ps1 status` pour toujours savoir où vous en êtes dans votre workflow !
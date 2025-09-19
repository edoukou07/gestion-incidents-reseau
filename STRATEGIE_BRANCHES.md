# 🌿 Stratégie de Branches Git pour Azure Deployment

## Structure des Branches

### 📋 **main** (Branche principale)
- **Usage** : Développement et intégration continue
- **Contenu** : Code source principal, tests, documentation
- **Protection** : Branche stable pour le développement collaboratif

### 🚀 **azure-deployment** (Branche de déploiement)
- **Usage** : Déploiement exclusif vers Azure App Service
- **Contenu** : Version optimisée avec configurations Azure
- **Spécificités** :
  - Fichiers de configuration Azure (`.deployment`, `Procfile`, `config.py`)
  - Optimisations pandas pour Azure
  - Variables d'environnement de production
  - Scripts de déploiement automatisés

## Workflow de Déploiement

### 1. Développement sur `main`
```powershell
# Travail habituel sur la branche principale
git checkout main
# ... développement ...
git add .
git commit -m "Feature: nouvelle fonctionnalité"
git push origin main
```

### 2. Préparation du déploiement
```powershell
# Basculer ou créer la branche de déploiement
git checkout azure-deployment

# Fusionner les derniers changements de main
git merge main

# Ajouter les optimisations Azure spécifiques
git add .
git commit -m "Azure deployment optimization"
```

### 3. Déploiement vers Azure
```powershell
# Déployer depuis azure-deployment vers Azure (qui utilise master)
git push azure azure-deployment:master

# Ou utiliser le script automatisé
.\deploy-to-azure.ps1
```

## Avantages de cette Approche

### ✅ **Séparation des Préoccupations**
- **main** : Code source pur, sans configuration cloud
- **azure-deployment** : Version déployable avec toutes les optimisations

### ✅ **Flexibilité**
- Possibilité de déployer sur différents environnements
- Configurations spécifiques par branche
- Tests sur différentes versions

### ✅ **Sécurité**
- Secrets et configurations sensibles uniquement sur la branche de déploiement
- Branche principale propre et générique

### ✅ **Maintenance**
- Rollback facile vers une version antérieure
- Historique clair des déploiements
- Possibilité de hot-fix en urgence

## Commandes Utiles

### Synchronisation des branches
```powershell
# Mettre à jour azure-deployment avec les derniers changements
git checkout azure-deployment
git merge main
git push origin azure-deployment
```

### Voir les différences
```powershell
# Comparer main et azure-deployment
git diff main azure-deployment

# Voir les commits spécifiques à azure-deployment
git log main..azure-deployment
```

### Déploiement d'urgence
```powershell
# Hot-fix directement sur azure-deployment
git checkout azure-deployment
# ... corrections ...
git add .
git commit -m "Hotfix: correction urgente"
git push azure azure-deployment:master
```

### Retour à une version antérieure
```powershell
# Voir l'historique des déploiements
git log --oneline

# Revenir à un commit spécifique
git checkout azure-deployment
git reset --hard <commit-hash>
git push azure azure-deployment:master --force
```

## Structure des Fichiers par Branche

### main
```
├── app.py (version générique)
├── templates/
├── static/
├── requirements.txt (développement)
├── README.md
└── tests/
```

### azure-deployment
```
├── app.py (optimisé Azure)
├── templates/
├── static/
├── requirements.txt (production Azure)
├── config.py (configuration Azure)
├── Procfile (Gunicorn config)
├── .deployment (Azure config)
├── deploy-to-azure.ps1
├── DEPLOY_AZURE_PROCEDURE.md
└── data/
    ├── users.csv
    └── incidents.csv
```

## Bonnes Pratiques

### 🔄 **Synchronisation Régulière**
- Fusionner `main` dans `azure-deployment` régulièrement
- Tester les déploiements avant la production

### 🔒 **Sécurité**
- Ne pas commiter de secrets dans `main`
- Utiliser les variables d'environnement Azure

### 📝 **Documentation**
- Documenter les changements spécifiques à Azure
- Maintenir un changelog des déploiements

### 🧪 **Tests**
- Tester sur `azure-deployment` avant déploiement
- Utiliser le health check après chaque déploiement

---

## Commandes Rapides de Déploiement

### Déploiement Complet
```powershell
# Tout en une commande
git checkout azure-deployment && git merge main && .\deploy-to-azure.ps1
```

### Mise à Jour Rapide
```powershell
# Redéploiement après modifications
git checkout azure-deployment
git add .
git commit -m "Update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push azure azure-deployment:master
```

Cette stratégie vous permet de maintenir un code source propre sur `main` tout en ayant une version optimisée et déployable sur `azure-deployment`. 🚀
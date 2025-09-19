# 🛠️ Gestion des Incidents Réseau

Une application web moderne pour la gestion des incidents réseau, développée avec Flask et Bootstrap.

## 🚀 Déploiement Rapide sur Azure App Service

```powershell
# 1. Basculer sur la branche de déploiement
git checkout azure-deployment

# 2. Lancer le déploiement automatique
.\scripts\deploy-to-azure.ps1
```

## 📁 Structure du Projet

```
gestion_incidents/
├── app.py              # Application Flask principale
├── config.py           # Configuration Azure
├── requirements.txt    # Dépendances Python
├── Procfile           # Configuration Gunicorn pour Azure
├── .deployment        # Configuration déploiement Azure
├── data/              # Données CSV (utilisateurs, incidents)
├── static/            # Fichiers CSS, JS
├── templates/         # Templates HTML Bootstrap
├── docs/              # 📚 Documentation complète
│   ├── README.md                    # Documentation détaillée
│   ├── DEPLOY_AZURE_PROCEDURE.md   # Procédure déploiement
│   ├── COMMANDES_RAPIDES.md        # Commandes essentielles
│   ├── STRATEGIE_BRANCHES.md       # Gestion des branches
│   ├── TESTS_POST_DEPLOIEMENT.md   # Guide de validation
│   └── RECAPITULATIF.md            # Vue d'ensemble
└── scripts/           # 🔧 Scripts d'automatisation
    ├── deploy-to-azure.ps1         # Déploiement automatique
    └── switch-branch.ps1           # Gestion des branches
```

## ⚡ Démarrage Rapide

### 1. Installation locale
```powershell
# Cloner et installer les dépendances
git clone https://github.com/edoukou07/gestion-incidents-reseau.git
cd gestion-incidents-reseau/gestion_incidents
pip install -r requirements.txt

# Lancer en local
python app.py
```

### 2. Déploiement Azure
```powershell
# Utiliser le script automatisé
.\scripts\deploy-to-azure.ps1

# Ou gestion avancée des branches
.\scripts\switch-branch.ps1 deploy
```

## 👥 Comptes de Test

| Utilisateur | Mot de passe | Rôle |
|-------------|-------------|------|
| `admin` | `admin123` | Administrateur |
| `technicien` | `tech123` | Technicien |
| `manager` | `manager123` | Manager |

## 🌟 Fonctionnalités

- 🔐 **Authentification sécurisée** avec sessions Flask
- 📊 **Dashboard** avec carrousel Bootstrap
- ➕ **Gestion CRUD** des incidents
- 👥 **Système de rôles** utilisateur
- 📱 **Interface responsive** Bootstrap 5.3
- ⚡ **Optimisé Azure** avec pandas 2.2.2
- 🔍 **Health Check** intégré (`/health`)

## 📚 Documentation

Toute la documentation détaillée se trouve dans le dossier [`docs/`](./docs/) :

- **[Déploiement Azure](./docs/DEPLOY_AZURE_PROCEDURE.md)** - Guide complet étape par étape
- **[Commandes Rapides](./docs/COMMANDES_RAPIDES.md)** - Commandes essentielles
- **[Stratégie Branches](./docs/STRATEGIE_BRANCHES.md)** - Gestion Git
- **[Tests Post-Déploiement](./docs/TESTS_POST_DEPLOIEMENT.md)** - Validation
- **[Récapitulatif](./docs/RECAPITULATIF.md)** - Vue d'ensemble

## 🔧 Scripts d'Automatisation

Le dossier [`scripts/`](./scripts/) contient :

- **`deploy-to-azure.ps1`** - Déploiement automatique vers Azure
- **`switch-branch.ps1`** - Gestion facile des branches Git

## 🚀 Technologies

- **Backend**: Python Flask 3.0.3
- **Frontend**: Bootstrap 5.3, HTML5, CSS3
- **Data**: Pandas 2.2.2 (optimisé Azure)
- **Serveur**: Gunicorn 22.0.0
- **Cloud**: Azure App Service (Canada Central)

## 🌿 Branches Git

- **`main`** : Développement principal
- **`azure-deployment`** : Version optimisée pour Azure

## 📞 Support

Pour toute question ou problème :
1. Consultez la documentation dans [`docs/`](./docs/)
2. Vérifiez les logs Azure avec les scripts fournis
3. Référez-vous aux guides de dépannage

---

**🎯 Prêt pour le déploiement professionnel sur Azure App Service !**
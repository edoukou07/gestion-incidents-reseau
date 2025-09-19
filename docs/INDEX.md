# 📚 Documentation - Gestion des Incidents Réseau

## 📋 Index de la Documentation

### 🚀 **Déploiement**
- **[DEPLOY_AZURE_PROCEDURE.md](./DEPLOY_AZURE_PROCEDURE.md)** - Procédure complète de déploiement sur Azure App Service
- **[COMMANDES_RAPIDES.md](./COMMANDES_RAPIDES.md)** - Commandes essentielles pour déploiement et maintenance
- **[RECAPITULATIF.md](./RECAPITULATIF.md)** - Vue d'ensemble et résumé du projet

### 🌿 **Gestion Git**
- **[STRATEGIE_BRANCHES.md](./STRATEGIE_BRANCHES.md)** - Stratégie de branches Git et workflow

### 🧪 **Tests et Validation**
- **[TESTS_POST_DEPLOIEMENT.md](./TESTS_POST_DEPLOIEMENT.md)** - Guide complet de validation après déploiement

### 📖 **Documentation Utilisateur**
- **[README.md](./README.md)** - Documentation détaillée de l'application

---

## 🔗 Liens Rapides

### Pour déployer immédiatement
```powershell
git checkout azure-deployment
..\scripts\deploy-to-azure.ps1
```

### Pour la gestion des branches
```powershell
..\scripts\switch-branch.ps1 --help
```

### Pour les tests post-déploiement
Consultez [TESTS_POST_DEPLOIEMENT.md](./TESTS_POST_DEPLOIEMENT.md)

---

## 📁 Structure des Fichiers

```
docs/
├── INDEX.md                     # Ce fichier - Index de la documentation
├── README.md                    # Documentation détaillée de l'application
├── DEPLOY_AZURE_PROCEDURE.md    # Procédure complète de déploiement
├── COMMANDES_RAPIDES.md         # Commandes essentielles
├── STRATEGIE_BRANCHES.md        # Gestion des branches Git
├── TESTS_POST_DEPLOIEMENT.md    # Guide de validation
└── RECAPITULATIF.md            # Vue d'ensemble du projet
```

## 🎯 Navigation Rapide

| Besoin | Fichier à consulter |
|--------|-------------------|
| Déployer sur Azure | [DEPLOY_AZURE_PROCEDURE.md](./DEPLOY_AZURE_PROCEDURE.md) |
| Commandes courantes | [COMMANDES_RAPIDES.md](./COMMANDES_RAPIDES.md) |
| Comprendre les branches | [STRATEGIE_BRANCHES.md](./STRATEGIE_BRANCHES.md) |
| Tester après déploiement | [TESTS_POST_DEPLOIEMENT.md](./TESTS_POST_DEPLOIEMENT.md) |
| Vue d'ensemble | [RECAPITULATIF.md](./RECAPITULATIF.md) |
| Documentation complète | [README.md](./README.md) |

---

**💡 Conseil**: Commencez par [RECAPITULATIF.md](./RECAPITULATIF.md) pour une vue d'ensemble, puis consultez [DEPLOY_AZURE_PROCEDURE.md](./DEPLOY_AZURE_PROCEDURE.md) pour le déploiement.
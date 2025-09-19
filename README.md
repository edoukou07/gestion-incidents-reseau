# 🛠️ Gestion des Incidents Réseau

Une application web moderne pour la gestion des incidents réseau, développée avec Flask et Bootstrap.

## ✨ Fonctionnalités

- 🔐 **Système d'authentification** sécurisé
- 📊 **Dashboard** avec carrousel informatif
- ➕ **Création d'incidents** avec formulaire intuitif
- 👁️ **Visualisation détaillée** des incidents
- 👥 **Gestion des utilisateurs** avec différents rôles
- 📱 **Interface responsive** avec Bootstrap 5
- 🎨 **Design moderne** avec animations CSS

## 🚀 Technologies utilisées

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Framework CSS:** Bootstrap 5.3
- **Icônes:** Font Awesome 6
- **Base de données:** CSV (pour la simplicité)

## 👥 Comptes de démonstration

| Utilisateur | Mot de passe | Rôle |
|-------------|-------------|------|
| `admin` | `admin123` | Administrateur |
| `technicien` | `tech123` | Technicien |
| `manager` | `manager123` | Manager |

## 🔧 Installation

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd gestion_incidents
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python app.py
   ```

4. **Accéder à l'application**
   - Ouvrir votre navigateur
   - Aller à `http://localhost:5000/login`
   - Utiliser un des comptes de démonstration

## 📁 Structure du projet

```
gestion_incidents/
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances Python
├── users.csv          # Base de données des utilisateurs
├── incidents.csv      # Base de données des incidents
├── templates/         # Templates HTML
│   ├── login.html     # Page de connexion
│   ├── index.html     # Page d'accueil
│   ├── ajouter.html   # Formulaire d'ajout
│   └── detail.html    # Détails d'incident
└── static/           # Ressources statiques
    └── style.css     # Styles personnalisés
```

## 🔐 Sécurité

- Sessions Flask sécurisées
- Protection des routes avec décorateurs
- Validation des formulaires
- Messages d'erreur/succès

## 🎨 Interface utilisateur

- Design responsive Bootstrap
- Carrousel d'information
- Menu de navigation intuitif
- Messages flash pour les notifications
- Animations CSS personnalisées

## 📝 Fonctionnalités détaillées

### Authentification
- Connexion sécurisée avec session
- Déconnexion avec confirmation
- Protection des routes sensibles

### Gestion des incidents
- Création d'incidents avec gravité
- Visualisation en tableau responsive
- Détails complets avec historique
- Badges colorés selon le statut

### Interface
- Carrousel informatif en page d'accueil
- Menu utilisateur avec profil
- Messages de notification
- Design moderne et professionnel

## 🚀 Développement futur

- [ ] Base de données PostgreSQL/MySQL
- [ ] API REST
- [ ] Notifications en temps réel
- [ ] Système de commentaires
- [ ] Export PDF des rapports
- [ ] Graphiques et statistiques

## 📄 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

Développé avec ❤️ pour la gestion efficace des incidents réseau.
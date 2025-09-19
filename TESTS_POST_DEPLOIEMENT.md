# 🧪 Guide de Test Post-Déploiement Azure

## Tests à effectuer après le déploiement sur Azure App Service

### 1. Tests de Connectivité de Base ✅

#### Test 1: Accès à l'application
```
URL: https://[votre-app-name].azurewebsites.net
Résultat attendu: Redirection vers /login
Status: 302 ou 200
```

#### Test 2: Health Check
```
URL: https://[votre-app-name].azurewebsites.net/health
Résultat attendu: 
{
  "status": "healthy",
  "timestamp": "2025-09-19T...",
  "pandas_available": true,
  "version": "1.0.0"
}
Status: 200
```

#### Test 3: Page de connexion
```
URL: https://[votre-app-name].azurewebsites.net/login
Résultat attendu: Formulaire de connexion Bootstrap
Status: 200
```

### 2. Tests d'Authentification 🔐

#### Test 4: Connexion Admin
```
Utilisateur: admin
Mot de passe: admin123
Résultat attendu: Connexion réussie, redirection vers dashboard
```

#### Test 5: Connexion Technicien
```
Utilisateur: technicien
Mot de passe: tech123
Résultat attendu: Connexion réussie, accès aux fonctionnalités
```

#### Test 6: Connexion Manager
```
Utilisateur: manager
Mot de passe: manager123
Résultat attendu: Connexion réussie, interface utilisateur
```

#### Test 7: Connexion invalide
```
Utilisateur: test
Mot de passe: invalid
Résultat attendu: Message d'erreur, reste sur /login
```

### 3. Tests Fonctionnels 📋

#### Test 8: Dashboard après connexion
```
Vérifications:
- Carrousel Bootstrap fonctionne
- Menu de navigation présent
- Nom d'utilisateur affiché
- Lien de déconnexion disponible
- Liste des incidents (vide au début)
```

#### Test 9: Ajout d'incident
```
URL: /ajouter (après connexion)
Données test:
- Titre: "Test incident Azure"
- Description: "Test de fonctionnement sur Azure"
- Priorité: "Haute"
Résultat attendu: Incident créé, redirection vers dashboard
```

#### Test 10: Visualisation d'incident
```
Cliquer sur un incident créé
Résultat attendu: Page de détail avec toutes les informations
URL: /incident/1
```

#### Test 11: Déconnexion
```
Cliquer sur "Se déconnecter"
Résultat attendu: Retour à /login, session supprimée
```

### 4. Tests de Performance 📊

#### Test 12: Temps de réponse
```
Outils: Browser DevTools, Postman
Pages à tester:
- /login (< 2s)
- / (dashboard) (< 3s)
- /ajouter (< 2s)
- /health (< 1s)
```

#### Test 13: Chargement des ressources
```
Vérifications:
- CSS Bootstrap charge correctement
- Images et icônes s'affichent
- JavaScript fonctionne (carrousel)
- Pas d'erreurs 404 dans la console
```

### 5. Tests de Sécurité 🔒

#### Test 14: Protection des routes
```
Tester sans être connecté:
- https://[app]/ -> Redirection vers /login
- https://[app]/ajouter -> Redirection vers /login
- https://[app]/incident/1 -> Redirection vers /login
```

#### Test 15: HTTPS forcé
```
Essayer: http://[app].azurewebsites.net
Résultat attendu: Redirection vers https://
```

#### Test 16: Session management
```
- Se connecter dans un onglet
- Ouvrir nouvel onglet sur l'app
- Vérifier que la session est partagée
- Se déconnecter, vérifier dans les deux onglets
```

### 6. Tests de Données CSV 📁

#### Test 17: Persistance des données
```
1. Créer un incident
2. Se déconnecter/reconnecter
3. Vérifier que l'incident existe toujours
```

#### Test 18: Intégrité des utilisateurs
```
Vérifier que les 3 utilisateurs par défaut fonctionnent:
- admin/admin123
- technicien/tech123
- manager/manager123
```

### 7. Tests de Monitoring Azure 📈

#### Test 19: Logs Azure
```powershell
# Vérifier les logs en temps réel
az webapp log tail --resource-group [rg-name] --name [app-name]

# Rechercher les erreurs
az webapp log download --resource-group [rg-name] --name [app-name]
```

#### Test 20: Métriques Azure
```
Dans le portail Azure:
- Vérifier les métriques de CPU
- Vérifier les métriques de mémoire
- Vérifier le nombre de requêtes
- Vérifier les temps de réponse
```

### 8. Tests de Charge Légère ⚡

#### Test 21: Requêtes multiples
```
Outils: Apache Bench, curl
Commande exemple:
curl -I https://[app-name].azurewebsites.net/health

Test avec 10 requêtes simultanées:
ab -n 10 -c 2 https://[app-name].azurewebsites.net/health
```

### 9. Checklist Final ✔️

- [ ] Application accessible via HTTPS
- [ ] Health check répond correctement  
- [ ] Les 3 utilisateurs peuvent se connecter
- [ ] Dashboard s'affiche correctement
- [ ] Carrousel fonctionne
- [ ] Création d'incident fonctionne
- [ ] Visualisation des incidents fonctionne
- [ ] Déconnexion fonctionne
- [ ] Protection des routes activée
- [ ] Données persistent après redémarrage
- [ ] Logs Azure configurés
- [ ] Performance acceptable (< 3s)
- [ ] Aucune erreur JavaScript
- [ ] Interface responsive sur mobile

### 10. Commandes de Diagnostic 🔍

```powershell
# État de l'application
az webapp show --resource-group [rg] --name [app] --query "{name:name, state:state, defaultHostName:defaultHostName}"

# Redémarrer si nécessaire
az webapp restart --resource-group [rg] --name [app]

# Forcer une reconstruction
az webapp deployment source sync --resource-group [rg] --name [app]

# Vérifier la configuration
az webapp config appsettings list --resource-group [rg] --name [app] --output table
```

### 11. Support et Dépannage 🆘

En cas de problème:

1. **Vérifier les logs**: `az webapp log tail`
2. **Vérifier la configuration**: Variables d'environnement
3. **Redémarrer l'app**: `az webapp restart`
4. **Forcer le redéploiement**: `git push azure main --force`
5. **Contacter le support Azure** si problème persistant

---

**Date de test**: _____________________  
**Testeur**: _____________________  
**Résultats**: ✅ Tous les tests passés / ⚠️ Tests partiels / ❌ Tests échoués

**Notes supplémentaires**:
_________________________________________________
_________________________________________________
_________________________________________________
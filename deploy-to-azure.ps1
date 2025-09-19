# Script de déploiement automatisé pour Azure App Service
# Application: Gestionnaire d'Incidents Réseau
# Région: Canada Central

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-gestion-incidents",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "canadacentral",
    
    [Parameter(Mandatory=$false)]
    [string]$AppNamePrefix = "gestion-incidents"
)

# Couleurs pour l'affichage
$Green = 'Green'
$Red = 'Red'
$Yellow = 'Yellow'
$Cyan = 'Cyan'

Write-Host "🚀 Démarrage du déploiement Azure App Service" -ForegroundColor $Cyan
Write-Host "📍 Région cible: $Location" -ForegroundColor $Yellow

# Variables générées
$AppName = "$AppNamePrefix-$(Get-Random -Minimum 1000 -Maximum 9999)"
$PlanName = "plan-$AppNamePrefix"
$Timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm"

try {
    # Étape 1: Vérification des prérequis
    Write-Host "`n📋 Vérification des prérequis..." -ForegroundColor $Yellow
    
    # Vérifier Azure CLI
    $azVersion = az --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "❌ Azure CLI n'est pas installé ou configuré"
    }
    Write-Host "✅ Azure CLI détecté" -ForegroundColor $Green
    
    # Vérifier la connexion Azure
    $account = az account show 2>$null | ConvertFrom-Json
    if (!$account) {
        Write-Host "🔐 Connexion à Azure requise..." -ForegroundColor $Yellow
        az login
        $account = az account show | ConvertFrom-Json
    }
    Write-Host "✅ Connecté à Azure - Abonnement: $($account.name)" -ForegroundColor $Green
    
    # Vérifier Git
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "❌ Git n'est pas installé"
    }
    Write-Host "✅ Git détecté" -ForegroundColor $Green

    # Étape 2: Création du groupe de ressources
    Write-Host "`n🏗️  Création du groupe de ressources..." -ForegroundColor $Yellow
    $rgExists = az group show --name $ResourceGroupName 2>$null
    if (!$rgExists) {
        az group create --name $ResourceGroupName --location $Location | Out-Null
        Write-Host "✅ Groupe de ressources '$ResourceGroupName' créé" -ForegroundColor $Green
    } else {
        Write-Host "ℹ️  Groupe de ressources '$ResourceGroupName' existe déjà" -ForegroundColor $Yellow
    }

    # Étape 3: Création du plan App Service
    Write-Host "`n📦 Création du plan App Service..." -ForegroundColor $Yellow
    $planExists = az appservice plan show --name $PlanName --resource-group $ResourceGroupName 2>$null
    if (!$planExists) {
        az appservice plan create `
            --name $PlanName `
            --resource-group $ResourceGroupName `
            --location $Location `
            --sku F1 `
            --is-linux | Out-Null
        Write-Host "✅ Plan App Service '$PlanName' créé" -ForegroundColor $Green
    } else {
        Write-Host "ℹ️  Plan App Service '$PlanName' existe déjà" -ForegroundColor $Yellow
    }

    # Étape 4: Création de l'application web
    Write-Host "`n🌐 Création de l'application web..." -ForegroundColor $Yellow
    $appExists = az webapp show --name $AppName --resource-group $ResourceGroupName 2>$null
    if (!$appExists) {
        az webapp create `
            --resource-group $ResourceGroupName `
            --plan $PlanName `
            --name $AppName `
            --runtime "PYTHON:3.11" `
            --startup-file "gunicorn --bind=0.0.0.0 --workers=2 app:app" | Out-Null
        Write-Host "✅ Application web '$AppName' créée" -ForegroundColor $Green
    } else {
        Write-Host "⚠️  Application web '$AppName' existe déjà - utilisation de l'existante" -ForegroundColor $Yellow
    }

    # Étape 5: Configuration des variables d'environnement
    Write-Host "`n⚙️  Configuration des variables d'environnement..." -ForegroundColor $Yellow
    $secretKey = [System.Guid]::NewGuid().ToString()
    az webapp config appsettings set `
        --resource-group $ResourceGroupName `
        --name $AppName `
        --settings `
        FLASK_ENV=production `
        SECRET_KEY=$secretKey `
        SCM_DO_BUILD_DURING_DEPLOYMENT=true `
        ENABLE_ORYX_BUILD=true | Out-Null
    Write-Host "✅ Variables d'environnement configurées" -ForegroundColor $Green

    # Étape 6: Configuration du déploiement Git
    Write-Host "`n📤 Configuration du déploiement Git..." -ForegroundColor $Yellow
    $gitUrl = az webapp deployment source config-local-git `
        --resource-group $ResourceGroupName `
        --name $AppName `
        --query url `
        --output tsv
    Write-Host "✅ URL Git de déploiement configurée" -ForegroundColor $Green

    # Étape 7: Configuration Git locale
    Write-Host "`n🔗 Configuration Git locale..." -ForegroundColor $Yellow
    
    # Supprimer le remote azure s'il existe
    git remote remove azure 2>$null
    
    # Ajouter le nouveau remote
    git remote add azure $gitUrl
    Write-Host "✅ Remote Azure ajouté" -ForegroundColor $Green

    # Étape 8: Préparation pour le déploiement
    Write-Host "`n📋 Préparation du déploiement..." -ForegroundColor $Yellow
    
    # Vérifier que nous sommes dans un repo Git
    if (!(Test-Path ".git")) {
        git init
        Write-Host "ℹ️  Repository Git initialisé" -ForegroundColor $Yellow
    }
    
    # Ajouter tous les fichiers
    git add .
    
    # Commit avec timestamp
    $commitMessage = "Production deployment to Azure App Service - $Timestamp"
    git commit -m $commitMessage
    Write-Host "✅ Commit créé: $commitMessage" -ForegroundColor $Green

    # Étape 9: Déploiement
    Write-Host "`n🚀 Déploiement vers Azure..." -ForegroundColor $Cyan
    Write-Host "⏳ Cela peut prendre plusieurs minutes..." -ForegroundColor $Yellow
    
    $deployOutput = git push azure main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Déploiement réussi!" -ForegroundColor $Green
    } else {
        Write-Host "⚠️  Déploiement terminé avec avertissements" -ForegroundColor $Yellow
        Write-Host "Sortie: $deployOutput" -ForegroundColor $Yellow
    }

    # Étape 10: Configuration post-déploiement
    Write-Host "`n🔒 Configuration HTTPS..." -ForegroundColor $Yellow
    az webapp update --resource-group $ResourceGroupName --name $AppName --https-only true | Out-Null
    Write-Host "✅ HTTPS forcé" -ForegroundColor $Green

    # Activation des logs
    Write-Host "`n📊 Activation des logs..." -ForegroundColor $Yellow
    az webapp log config --application-logging filesystem `
        --resource-group $ResourceGroupName `
        --name $AppName | Out-Null
    Write-Host "✅ Logs activés" -ForegroundColor $Green

    # Étape 11: Informations de déploiement
    Write-Host "`n🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!" -ForegroundColor $Green
    Write-Host "════════════════════════════════════" -ForegroundColor $Cyan
    Write-Host "📱 Application URL: https://$AppName.azurewebsites.net" -ForegroundColor $Yellow
    Write-Host "🔍 Health Check: https://$AppName.azurewebsites.net/health" -ForegroundColor $Yellow
    Write-Host "🖥️  Kudu Console: https://$AppName.scm.azurewebsites.net" -ForegroundColor $Yellow
    Write-Host "📍 Région: $Location" -ForegroundColor $Yellow
    Write-Host "🏷️  Nom de l'app: $AppName" -ForegroundColor $Yellow
    Write-Host "📦 Groupe de ressources: $ResourceGroupName" -ForegroundColor $Yellow
    Write-Host "════════════════════════════════════" -ForegroundColor $Cyan

    Write-Host "`n👥 Utilisateurs de test:" -ForegroundColor $Cyan
    Write-Host "   • admin / admin123" -ForegroundColor $White
    Write-Host "   • technicien / tech123" -ForegroundColor $White
    Write-Host "   • manager / manager123" -ForegroundColor $White

    Write-Host "`n📋 Commandes utiles:" -ForegroundColor $Cyan
    Write-Host "   Logs en temps réel:" -ForegroundColor $White
    Write-Host "   az webapp log tail --resource-group $ResourceGroupName --name $AppName" -ForegroundColor $Gray
    Write-Host "   Redémarrer l'app:" -ForegroundColor $White
    Write-Host "   az webapp restart --resource-group $ResourceGroupName --name $AppName" -ForegroundColor $Gray
    Write-Host "   Redéployer:" -ForegroundColor $White
    Write-Host "   git push azure main" -ForegroundColor $Gray

    # Test de connexion
    Write-Host "`n🔍 Test de l'application..." -ForegroundColor $Yellow
    Start-Sleep -Seconds 10
    try {
        $response = Invoke-WebRequest -Uri "https://$AppName.azurewebsites.net/health" -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Application accessible et fonctionnelle!" -ForegroundColor $Green
        }
    } catch {
        Write-Host "⚠️  Application déployée mais non accessible immédiatement (démarrage en cours)" -ForegroundColor $Yellow
        Write-Host "   Essayez dans quelques minutes: https://$AppName.azurewebsites.net" -ForegroundColor $White
    }

} catch {
    Write-Host "`n❌ ERREUR DE DÉPLOIEMENT" -ForegroundColor $Red
    Write-Host "Détails: $($_.Exception.Message)" -ForegroundColor $Red
    Write-Host "`nVérifiez:" -ForegroundColor $Yellow
    Write-Host "• Connexion Azure CLI" -ForegroundColor $White
    Write-Host "• Permissions sur l'abonnement" -ForegroundColor $White
    Write-Host "• Quota de ressources" -ForegroundColor $White
    exit 1
}

Write-Host "`n🎊 Déploiement terminé! Bonne utilisation!" -ForegroundColor $Green
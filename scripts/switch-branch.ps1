# Script de gestion des branches - Gestion Incidents
# Usage: .\switch-branch.ps1 [main|azure-deployment|deploy|sync|status]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("main", "azure-deployment", "deploy", "sync", "status")]
    [string]$Action
)

$Green = 'Green'
$Yellow = 'Yellow'
$Cyan = 'Cyan'
$White = 'White'

switch ($Action) {
    "main" {
        Write-Host "Basculement vers la branche main..." -ForegroundColor $Yellow
        git checkout main
        Write-Host "Maintenant sur la branche main (developpement)" -ForegroundColor $Green
    }
    
    "azure-deployment" {
        Write-Host "Basculement vers la branche azure-deployment..." -ForegroundColor $Yellow
        git checkout azure-deployment
        Write-Host "Maintenant sur la branche azure-deployment (deploiement)" -ForegroundColor $Green
    }
    
    "deploy" {
        Write-Host "Deploiement automatique depuis azure-deployment..." -ForegroundColor $Cyan
        git checkout azure-deployment
        
        # Synchroniser avec main si necessaire
        $confirm = Read-Host "Voulez-vous synchroniser avec main d'abord? (y/n)"
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            Write-Host "Synchronisation avec main..." -ForegroundColor $Yellow
            git merge main
        }
        
        # Lancer le deploiement
        .\scripts\deploy-to-azure.ps1
    }
    
    "sync" {
        Write-Host "Synchronisation azure-deployment avec main..." -ForegroundColor $Yellow
        $currentBranch = git branch --show-current
        
        git checkout azure-deployment
        git merge main
        git add .
        git commit -m "Sync with main - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        
        Write-Host "azure-deployment synchronisee avec main" -ForegroundColor $Green
        
        if ($currentBranch -ne "azure-deployment") {
            git checkout $currentBranch
            Write-Host "Retour a la branche: $currentBranch" -ForegroundColor $Yellow
        }
    }
    
    "status" {
        Write-Host "Etat du repository Git:" -ForegroundColor $Cyan
        Write-Host "=========================" -ForegroundColor $Cyan
        
        $currentBranch = git branch --show-current
        Write-Host "Branche actuelle: $currentBranch" -ForegroundColor $Green
        
        Write-Host "`nBranches disponibles:" -ForegroundColor $Yellow
        git branch -v
        
        Write-Host "`nEtat des fichiers:" -ForegroundColor $Yellow
        git status --porcelain
        
        Write-Host "`nRemotes configures:" -ForegroundColor $Yellow
        git remote -v
        
        Write-Host "`nDerniers commits:" -ForegroundColor $Yellow
        git log --oneline -5
    }
}

Write-Host "`nCommandes disponibles:" -ForegroundColor $Cyan
Write-Host "   .\scripts\switch-branch.ps1 main              - Basculer vers main" -ForegroundColor $White
Write-Host "   .\scripts\switch-branch.ps1 azure-deployment  - Basculer vers azure-deployment" -ForegroundColor $White
Write-Host "   .\scripts\switch-branch.ps1 deploy            - Deployer automatiquement" -ForegroundColor $White
Write-Host "   .\scripts\switch-branch.ps1 sync              - Synchroniser les branches" -ForegroundColor $White
Write-Host "   .\scripts\switch-branch.ps1 status            - Voir l'etat du repository" -ForegroundColor $White
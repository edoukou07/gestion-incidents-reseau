# Script PowerShell pour uploader le fichier d'incidents vers Azure Blob Storage
# Nécessite Azure PowerShell (Install-Module -Name Az)

param(
    [string]$StorageAccountName,
    [string]$ContainerName = "incidents-data",
    [string]$FilePath = "./incidents_example.csv",
    [string]$BlobName = "incidents.csv"
)

# Vérifier si les paramètres sont fournis
if (-not $StorageAccountName) {
    Write-Host "❌ Paramètre StorageAccountName requis" -ForegroundColor Red
    Write-Host "Usage: .\upload-incidents-to-blob.ps1 -StorageAccountName 'votre-storage-account'" -ForegroundColor Yellow
    exit 1
}

# Vérifier si le fichier existe
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ Fichier $FilePath non trouvé" -ForegroundColor Red
    exit 1
}

try {
    Write-Host "🔧 Upload des incidents vers Azure Blob Storage..." -ForegroundColor Blue
    Write-Host "📦 Storage Account: $StorageAccountName" -ForegroundColor Gray
    Write-Host "🗂️ Container: $ContainerName" -ForegroundColor Gray
    Write-Host "📄 Fichier local: $FilePath" -ForegroundColor Gray
    Write-Host "🎯 Nom du blob: $BlobName" -ForegroundColor Gray
    
    # Se connecter à Azure si nécessaire
    $context = Get-AzContext
    if (-not $context) {
        Write-Host "🔐 Connexion à Azure..." -ForegroundColor Yellow
        Connect-AzAccount
    }
    
    # Obtenir le contexte du compte de stockage
    Write-Host "🔗 Connexion au compte de stockage..." -ForegroundColor Yellow
    $storageAccount = Get-AzStorageAccount | Where-Object { $_.StorageAccountName -eq $StorageAccountName }
    
    if (-not $storageAccount) {
        Write-Host "❌ Compte de stockage '$StorageAccountName' non trouvé" -ForegroundColor Red
        exit 1
    }
    
    $ctx = $storageAccount.Context
    
    # Créer le container s'il n'existe pas
    Write-Host "📁 Vérification du container..." -ForegroundColor Yellow
    $container = Get-AzStorageContainer -Name $ContainerName -Context $ctx -ErrorAction SilentlyContinue
    if (-not $container) {
        Write-Host "📁 Création du container $ContainerName..." -ForegroundColor Yellow
        New-AzStorageContainer -Name $ContainerName -Context $ctx -Permission Off
    }
    
    # Uploader le fichier
    Write-Host "⬆️ Upload du fichier..." -ForegroundColor Yellow
    Set-AzStorageBlobContent -File $FilePath -Container $ContainerName -Blob $BlobName -Context $ctx -Force
    
    Write-Host "✅ Fichier uploadé avec succès!" -ForegroundColor Green
    Write-Host "🌐 URL du blob: https://$StorageAccountName.blob.core.windows.net/$ContainerName/$BlobName" -ForegroundColor Gray
    
    # Afficher les propriétés du blob
    $blob = Get-AzStorageBlob -Container $ContainerName -Blob $BlobName -Context $ctx
    Write-Host "📊 Taille du fichier: $($blob.Length) bytes" -ForegroundColor Gray
    Write-Host "📅 Dernière modification: $($blob.LastModified)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Erreur lors de l'upload: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 Upload terminé avec succès!" -ForegroundColor Green
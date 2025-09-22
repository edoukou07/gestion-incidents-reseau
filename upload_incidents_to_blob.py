#!/usr/bin/env python3
"""
Script pour uploader le fichier incidents.csv vers Azure Blob Storage
Utilise le service principal pour l'authentification
"""

import os
import sys
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential

def upload_incidents_to_blob():
    """Upload le fichier incidents_example.csv vers Azure Blob Storage"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    try:
        # Récupérer les variables d'environnement
        storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        # Validation des variables d'environnement
        if not all([storage_account_name, container_name, client_id, client_secret, tenant_id]):
            raise ValueError("Variables d'environnement Azure manquantes. Vérifiez votre fichier .env")
        
        print("🔑 Authentification avec le service principal...")
        
        # Créer les credentials du service principal
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # URL du compte de stockage
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        
        # Créer le client Blob Service
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        print(f"✅ Connexion établie avec le storage account: {storage_account_name}")
        
        # Vérifier que le container existe
        try:
            container_client = blob_service_client.get_container_client(container_name)
            container_exists = container_client.exists()
            
            if not container_exists:
                print(f"⚠️ Container '{container_name}' n'existe pas. Création en cours...")
                container_client.create_container()
                print(f"✅ Container '{container_name}' créé avec succès")
            else:
                print(f"✅ Container '{container_name}' trouvé")
                
        except Exception as e:
            print(f"❌ Erreur lors de la vérification/création du container: {e}")
            return False
        
        # Chemin du fichier CSV
        csv_file_path = "incidents_example.csv"
        blob_name = "incidents.csv"
        
        if not os.path.exists(csv_file_path):
            print(f"❌ Fichier {csv_file_path} non trouvé")
            return False
        
        print(f"📤 Upload du fichier {csv_file_path} vers le blob {blob_name}...")
        
        # Uploader le fichier
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        with open(csv_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        print(f"✅ Fichier uploadé avec succès vers {blob_name}")
        
        # Vérifier que l'upload a réussi
        if blob_client.exists():
            properties = blob_client.get_blob_properties()
            print(f"📊 Taille du blob: {properties.size} bytes")
            print(f"📅 Dernière modification: {properties.last_modified}")
            
            # Lister tous les blobs pour confirmation
            print("\n📋 Blobs dans le container:")
            container_client = blob_service_client.get_container_client(container_name)
            for blob in container_client.list_blobs():
                print(f"   - {blob.name} ({blob.size} bytes)")
            
            return True
        else:
            print("❌ Erreur: le blob n'a pas été créé correctement")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de l'upload des incidents vers Azure Blob Storage")
    print("=" * 60)
    
    success = upload_incidents_to_blob()
    
    if success:
        print("\n🎉 Upload terminé avec succès !")
        print("💡 Vous pouvez maintenant tester votre application Flask")
    else:
        print("\n❌ Échec de l'upload")
        print("💡 Vérifiez votre configuration et les permissions du service principal")
        sys.exit(1)
# src/data_loader/loader.py
import os
import pandas as pd
from sqlalchemy import create_engine
import zipfile
import kaggle
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DATASET_NAME = 'olistbr/brazilian-ecommerce'
DATA_DIR = './data'
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = 'localhost'
DB_PORT = '5432'

# --- Connexion à la base de données ---
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def download_and_unzip_dataset():
    """Télécharge et dézippe le dataset Olist depuis Kaggle."""
    print("Téléchargement du dataset depuis Kaggle...")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(DATASET_NAME, path=DATA_DIR, unzip=False)
    
    zip_path = os.path.join(DATA_DIR, f"{DATASET_NAME.split('/')[1]}.zip")
    
    print("Décompression du dataset...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
    print("Nettoyage du fichier zip...")
    os.remove(zip_path)
    print("Dataset prêt.")

def load_csv_to_postgres():
    """Charge tous les fichiers CSV du dossier data dans PostgreSQL."""
    print("Chargement des données dans PostgreSQL...")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    for file in files:
        table_name = os.path.splitext(file)[0].replace('olist_', '').replace('_dataset', '')
        file_path = os.path.join(DATA_DIR, file)
        
        print(f"  - Traitement de {file} -> table '{table_name}'...")
        
        df = pd.read_csv(file_path)
        
        # Nettoyage simple des noms de colonnes pour être compatibles SQL
        df.columns = [col.replace('-', '_') for col in df.columns]
        
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
    print("Chargement des données terminé.")

if __name__ == '__main__':
    download_and_unzip_dataset()
    load_csv_to_postgres()

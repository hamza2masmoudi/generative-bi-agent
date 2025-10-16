# src/agent/tools.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import plotly.express as px
import streamlit as st
import re

# Charger les variables d'environnement
load_dotenv()

# --- Configuration de la connexion à la BDD ---
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = 'localhost'
DB_PORT = '5432'
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# --- Définition des Outils ---

def execute_sql_query(query: str) -> pd.DataFrame:
    """
    Exécute une requête SQL SELECT sur la base de données PostgreSQL et retourne le résultat sous forme de DataFrame Pandas.
    IMPORTANT: La requête doit être une requête de LECTURE SEULE (SELECT).
    Ne pas utiliser pour modifier la base de données.
    """
    print(f"--- Executing SQL Query --- \n{query}")
    try:
        with engine.connect() as connection:
            result_df = pd.read_sql_query(text(query), connection)
        print("--- Query Successful ---")
        return result_df
    except Exception as e:
        print(f"--- Query Failed: {e} ---")
        return f"Erreur lors de l'exécution de la requête: {str(e)}"

def create_chart(data: str, chart_type: str, title: str, **kwargs) -> str:
    """
    Génère un graphique à partir d'un DataFrame Pandas (passé en string) en utilisant Plotly et le sauvegarde en tant qu'image.
    Retourne le chemin du fichier de l'image.
    
    Args:
        data (str): Le DataFrame Pandas sérialisé en string.
        chart_type (str): Le type de graphique ('bar', 'line', 'scatter', 'pie').
        title (str): Le titre du graphique.
        **kwargs: Arguments supplémentaires pour la fonction de graphique Plotly (ex: x='colonne_x', y='colonne_y', x_label='Label X', y_label='Label Y').
    """
    print(f"--- Creating Chart --- \nTitle: {title}, Type: {chart_type}, kwargs: {kwargs}")
    if not os.path.exists('charts'):
        os.makedirs('charts')

    try:
        # Convertir la chaîne de caractères en DataFrame Pandas
        from io import StringIO
        df = pd.read_csv(StringIO(data))
        # Nettoyage des noms de colonnes (supprimer les espaces superflus)
        df.columns = df.columns.str.strip()

        fig = None
        
        # Préparer les labels pour Plotly Express
        labels = {}
        if 'x_label' in kwargs and kwargs['x_label'] is not None:
            labels[kwargs['x']] = kwargs.pop('x_label')
        if 'y_label' in kwargs and kwargs['y_label'] is not None:
            labels[kwargs['y']] = kwargs.pop('y_label')

        if chart_type == 'bar':
            fig = px.bar(df, title=title, labels=labels, **kwargs)
        elif chart_type == 'line':
            fig = px.line(df, title=title, labels=labels, **kwargs)
        elif chart_type == 'scatter':
            fig = px.scatter(df, title=title, labels=labels, **kwargs)
        elif chart_type == 'pie':
            # Pour les pie charts, 'x' devient 'names' et 'y' devient 'values'
            names_col = kwargs.pop('x', None)
            values_col = kwargs.pop('y', None)
            if names_col and values_col:
                fig = px.pie(df, names=names_col, values=values_col, title=title, **kwargs)
            else:
                return "Erreur: Pour un graphique en secteurs, 'x' (noms) et 'y' (valeurs) sont requis."
        else:
            return "Erreur: Type de graphique non supporté. Utilisez 'bar', 'line', 'scatter', ou 'pie'."
        
        # Nettoyage du titre pour créer un nom de fichier valide
        safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', title).lower()
        filepath = f'charts/{safe_title}.png'
        
        # Nécessite 'kaleido' installé (dans requirements.txt) et Google Chrome
        fig.write_image(filepath) 
        print(f"--- Chart saved to {filepath} ---")
        return filepath
    except Exception as e:
        print(f"--- Chart Creation Failed: {e} ---")
        return f"Erreur lors de la création du graphique: {str(e)}"

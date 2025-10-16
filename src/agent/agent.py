# src/agent/agent.py
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import Tool, StructuredTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .tools import execute_sql_query, create_chart

load_dotenv()

# --- 1. Initialisation du LLM ---
# Décommentez le LLM de votre choix
# llm = ChatOpenAI(temperature=0, model="gpt-4-turbo")
#llm = ChatAnthropic(temperature=0, model_name="claude-3-sonnet-20240229")
llm = ChatMistralAI(temperature=0, model="mistral-large-latest")

# --- 2. Définition des outils pour LangChain ---
# On "enveloppe" nos fonctions Python dans la classe Tool de LangChain

class ChartInput(BaseModel):
    data: str = Field(description="Le DataFrame Pandas sérialisé en string.")
    chart_type: str = Field(description="Le type de graphique ('bar', 'line', 'scatter', 'pie').")
    title: str = Field(description="Le titre du graphique.")
    x: str | None = Field(default=None, description="Le nom de la colonne pour l'axe des X (utilisé comme 'names' pour les pie charts).")
    y: str | None = Field(default=None, description="Le nom de la colonne pour l'axe des Y (utilisé comme 'values' pour les pie charts).")
    x_label: str | None = Field(default=None, description="Le label pour l'axe des X.")
    y_label: str | None = Field(default=None, description="Le label pour l'axe des Y.")

tools = [
    Tool(
        name="SQLQueryExecutor",
        func=execute_sql_query,
        description="""
        Utilisez cet outil pour exécuter une requête SQL SELECT afin de récupérer des informations depuis la base de données.
        Entrée: une requête SQL complète et valide.
        Sortie: un DataFrame Pandas avec les résultats ou un message d'erreur.
        Le schéma de la base de données contient les tables suivantes : 
        'customers', 'geolocation', 'order_items', 'order_payments', 'order_reviews', 'orders', 'products', 'sellers', 'product_category_name_translation'.
        Pour la table 'order_items', la quantité d'articles vendus peut être calculée en utilisant COUNT(order_item_id).
        Examinez les colonnes de chaque table pour construire vos requêtes.
        """
    ),
    StructuredTool(
        name="ChartGenerator",
        func=create_chart,
        description="""
        Utilisez cet outil pour générer un graphique à partir de données.
        Entrée: un DataFrame Pandas sérialisé en string, un type de graphique ('bar', 'line', 'pie', 'scatter'), un titre, et les arguments de mapping pour les axes (x, y, x_label, y_label).
        Sortie: le chemin vers le fichier image du graphique généré.
        """,
        args_schema=ChartInput
    )
]

# --- 3. Le Prompt de l'Agent (sa "Constitution") ---
prompt_template = """
Vous êtes un analyste de données expert nommé "BI-Agent". Votre mission est de répondre aux questions business en utilisant les outils à votre disposition.

Vous devez procéder étape par étape de la manière suivante :
1.  **Réflexion (Thought)**: Analysez la question de l'utilisateur. Décomposez-la en sous-problèmes. Élaborez un plan d'action clair. Pensez aux données dont vous avez besoin et comment les obtenir.
2.  **Action (Action)**: Choisissez l'outil le plus approprié pour la prochaine étape de votre plan. Spécifiez les paramètres d'entrée pour cet outil.
3.  **Observation (Observation)**: Examinez le résultat de l'action.
4.  **Itération**: Répétez les étapes de Réflexion, Action et Observation jusqu'à ce que vous ayez rassemblé toutes les informations nécessaires pour répondre à la question de l'utilisateur.

**Directives importantes :**
-   Si vous devez utiliser le résultat d'un outil comme entrée pour un autre, vous devez d'abord exécuter le premier outil et utiliser sa sortie.
-   Lorsque vous avez toutes les données et les graphiques nécessaires, terminez votre travail en fournissant une réponse finale et complète à l'utilisateur.
-   Votre réponse finale doit être une synthèse claire et concise, en incluant les chemins vers les graphiques que vous avez générés.
-   Lorsque vous utilisez l'outil ChartGenerator, assurez-vous de fournir les arguments 'chart_type' et 'title' explicitement, ainsi que 'x_label' et 'y_label' pour les axes.

**Début de l'analyse !**

**Question de l'utilisateur :** {input}

**Journal de bord (vos étapes de réflexion et d'action) :**
{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# --- 4. Création de l'Agent ---
agent = create_tool_calling_agent(llm, tools, prompt)

# --- 5. L'Exécuteur de l'Agent ---
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # TRÈS important pour le débug et pour montrer le raisonnement !
    handle_parsing_errors=True # Gère les erreurs si le LLM formate mal sa sortie
)

def run_agent(user_query: str, callbacks=None): # Ajout de l'argument callbacks pour Streamlit
    """Fonction principale pour lancer l'agent avec une question."""
    response = agent_executor.invoke({"input": user_query}, {"callbacks": callbacks}) # Passage des callbacks à invoke
    return response

# Generative BI Agent 🤖

## Project Overview

This project develops an autonomous Business Intelligence (BI) agent capable of answering complex business questions through natural language interaction. Leveraging the power of Large Language Models (LLMs) and a robust tool-use framework (LangChain), the agent can query a PostgreSQL database, perform data analysis using Pandas, and generate insightful visualizations with Plotly. The entire application is containerized using Docker for easy deployment and reproducibility, with a user-friendly interface built with Streamlit.

The agent's core functionality revolves around analyzing the Olist Brazilian E-commerce Public Dataset, providing a practical demonstration of how generative AI can empower business users to extract actionable insights without requiring deep technical knowledge of SQL or data science programming.

## Features

*   **Natural Language Querying**: Interact with the BI agent using plain English (or French, as configured).
*   **Intelligent SQL Generation**: The LLM translates natural language questions into precise SQL queries to retrieve data from a PostgreSQL database.
*   **Data Analysis Capabilities**: Utilizes Pandas for in-depth data manipulation and analysis of query results.
*   **Dynamic Chart Generation**: Creates various types of charts (bar, line, scatter, pie) using Plotly to visualize data insights, saved as PNG images.
*   **Interactive Web Interface**: A Streamlit application provides a conversational chat interface to interact with the agent and display results, including generated charts.
*   **Containerized Deployment**: Full project setup with Docker and Docker Compose for isolated, reproducible, and scalable deployment.
*   **Configurable LLM Backend**: Easily switch between different LLM providers (Mistral AI, OpenAI, Anthropic) by configuring environment variables.

## Architecture

The Generative BI Agent follows a modular architecture, primarily composed of:

1.  **Streamlit Application (`app.py`)**: The frontend interface where users submit questions and view the agent's responses and visualizations. It uses `StreamlitCallbackHandler` for real-time display of the agent's thought process.
2.  **LangChain Agent (`src/agent/agent.py`)**: The "brain" of the system. It orchestrates the interaction between the LLM and the tools. It uses a ReAct (Reason-Act) prompting strategy to enable robust reasoning.
    *   **LLM**: Configurable Large Language Model (e.g., Mistral Large, GPT-4, Claude 3) for natural language understanding and tool orchestration.
    *   **Tools (`src/agent/tools.py`)**: A set of specialized Python functions exposed to the LLM, including:
        *   `SQLQueryExecutor`: Executes read-only SQL queries against the PostgreSQL database.
        *   `ChartGenerator`: Creates Plotly charts from Pandas DataFrames and saves them as PNG images.
3.  **PostgreSQL Database**: Stores the Olist e-commerce dataset. Managed via Docker Compose for easy setup.
4.  **Data Loader (`src/data_loader/loader.py`)**: A Python script responsible for downloading the Olist dataset from Kaggle, processing CSV files, and loading them into the PostgreSQL database.
5.  **Docker & Docker Compose**: Used for containerizing the PostgreSQL database and the Streamlit application, ensuring a consistent development and deployment environment.


## Setup & Installation

Follow these steps to get the Generative BI Agent up and running on your local machine.

### Prerequisites

*   **Docker Desktop**: Ensure Docker Desktop is installed and running. [Download for Mac](https://docs.docker.com/desktop/install/mac-install/) / [Download for Windows](https://docs.docker.com/desktop/install/windows-install/) / [Download for Linux](https://docs.docker.com/desktop/install/linux-install/)
*   **Python 3.10+**: Installed on your system.
*   **Kaggle Account & API Key**: Required to download the Olist dataset.
    *   Go to [Kaggle](https://www.kaggle.com/).
    *   Navigate to your profile, then "Account".
    *   Under "API", click "Create New API Token" to download `kaggle.json`.
    *   Place `kaggle.json` in `~/.kaggle/kaggle.json` (create the `.kaggle` directory if it doesn't exist). Ensure its permissions are `chmod 600 ~/.kaggle/kaggle.json`.
*   **LLM API Key**: An API key for your chosen LLM (Mistral AI, OpenAI, or Anthropic).

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone git@github.com:hamza2masmoudi/generative-bi-agent.git
cd generative-bi-agent
```

### 2. Environment Setup

Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root of the `generative-bi-agent/` directory:

```
# Choose the LLM service you want to use
# OPENAI_API_KEY="sk-..."
# ANTHROPIC_API_KEY="sk-ant-..."
MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY" # Replace with your actual Mistral API Key

# Database information (used in docker-compose)
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=olist_db
```
Replace `YOUR_MISTRAL_API_KEY` with your actual Mistral AI API key. If using OpenAI or Anthropic, uncomment the respective line and provide your key.

### 4. Launch PostgreSQL Database

Use Docker Compose to start the PostgreSQL database:

```bash
docker compose --env-file .env up -d
```
Verify the container is running: `docker ps`

### 5. Load Data into PostgreSQL

Run the data loading script to populate the database with the Olist dataset:

```bash
python3 src/data_loader/loader.py
```
This script will download the dataset (requires `kaggle.json`), unzip it, and insert the CSV data into your PostgreSQL database.

### 6. Install Google Chrome (for Chart Generation)

The `kaleido` library, used by Plotly to save charts as images, requires Google Chrome to be installed. If you don't have it, run:

```bash
plotly_get_chrome
```
Or manually install Google Chrome.

## Usage

To start the Streamlit application, ensure your Python virtual environment is active and run:

```bash
.venv/bin/streamlit run app.py
```
Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501` or similar).

You can now interact with the BI Agent by typing your business questions in the chat interface.

**Example Queries:**

*   "Quels sont les 10 produits les plus vendus en termes de quantité ?"
*   "Montre-moi la répartition des commandes par état des clients."
*   "Quel est le revenu total par catégorie de produit ?"
*   "Crée un graphique à barres des 5 meilleures catégories de produits par revenu."
*   "Combien de commandes ont été passées chaque mois en 2018 ?"

## Tools & Technologies

*   **Python 3.10+**
*   **LangChain**: Framework for developing LLM-powered applications.
*   **Mistral AI (or OpenAI/Anthropic)**: Large Language Model for natural language processing and reasoning.
*   **Streamlit**: For building interactive web applications.
*   **PostgreSQL**: Relational database for data storage.
*   **Docker & Docker Compose**: For containerization and orchestration.
*   **Pandas**: Data manipulation and analysis.
*   **Plotly & Kaleido**: For dynamic and static chart generation.
*   **python-dotenv**: For managing environment variables.
*   **Kaggle API**: For dataset download.

## Future Enhancements

*   **Advanced Data Cleaning & Preprocessing**: Implement more sophisticated data validation and cleaning routines.
*   **More Sophisticated Charting**: Allow for more complex chart types, customization options, and interactive Plotly charts directly in Streamlit.
*   **Multi-turn Conversation & Memory**: Enhance the agent's memory to better handle follow-up questions and maintain context over longer conversations.
*   **Error Handling & Robustness**: Improve error handling for SQL queries and API calls, providing more user-friendly feedback.
*   **Security**: Implement best practices for securing API keys and database access in production environments.
*   **Deployment to Cloud Platforms**: Provide instructions or scripts for deploying the agent to cloud services like AWS, GCP, or Azure.
*   **Integration with other Data Sources**: Extend the agent's capabilities to connect to other databases, data warehouses, or APIs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

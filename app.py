# app.py
import streamlit as st
import os
import re
from src.agent.agent import run_agent
from langchain.callbacks import StreamlitCallbackHandler

st.set_page_config(page_title="Agent BI Autonome", page_icon="🤖")

st.title("🤖 Agent d'Analyse Business Autonome")
st.caption("Posez une question sur la base de données e-commerce Olist et l'agent tentera d'y répondre.")

# Initialiser l'historique de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Bonjour ! Quelle question business souhaitez-vous explorer ?"}]

# Afficher les messages de l'historique
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Gérer l'entrée utilisateur
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Afficher la pensée de l'agent en temps réel dans un conteneur dédié
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        
        # Exécuter l'agent
        response = run_agent(prompt, callbacks=[st_callback])
        
        output = response.get('output', 'Désolé, je n\'ai pas pu traiter votre demande.')

        # Mettre à jour l'historique avec la réponse finale
        st.session_state.messages.append({"role": "assistant", "content": output})
        
        # Afficher la réponse finale (qui peut inclure des chemins d'images)
        st.write(output)

        # Chercher et afficher les images de graphiques mentionnées dans la sortie
        image_paths = re.findall(r'charts/[a-zA-Z0-9_]+\.png', output)
        for image_path in image_paths:
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)

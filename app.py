import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import re
import os

# 1. Configuration de l'API (à mettre dans vos Secrets Streamlit en prod)
API_KEY = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else ""

st.set_page_config(page_title="Dashboard Qualité & Bible Gemini", layout="centered")

# --- SECTION 1 : VOTRE INDEX ACTUEL ---
st.markdown("### 📂 Table des Rapports CPS")

# On encapsule votre HTML dans un composant Streamlit
index_html = """
<style>
    body { font-family: sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; padding: 20px; border-radius: 10px; }
    h2 { font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05rem; margin-top: 1rem; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; }
    ul { list-style: none; padding: 0; }
    li { margin-bottom: 0.5rem; }
    a { text-decoration: none; color: #0066cc; font-weight: bold; }
    a:hover { text-decoration: underline; }
</style>
<body>
  <h2>Rapports CPS Existants</h2>
  <ul>
    <li><a href="karambolage_768_Analyse.html" target="_blank">Karambolage_768</a></li>
    <li><a href="karambolage_769_Analyse.html" target="_blank">Karambolage_769</a></li>
    <li><a href="robe_peau_Analyse.html" target="_blank">robe_peau</a></li>
  </ul>
</body>
"""
components.html(index_html, height=250)

st.divider()

# --- SECTION 2 : GÉNÉRATEUR DE BIBLE GEMINI ---
st.markdown("### 🤖 Générateur de 'Bible' (Fact-checking 2026)")
st.caption("Utilise Gemini 2.0 Flash + Google Search pour vérifier Richard Werly, Lecornu, etc.")

if not API_KEY:
    api_input = st.text_input("Entrez votre clé API Gemini pour activer l'analyse :", type="password")
    if api_input:
        API_KEY = api_input

uploaded_file = st.file_uploader("Glissez un fichier SRT pour analyse corrective", type="srt")

if uploaded_file and API_KEY:
    genai.configure(api_key=API_KEY)
    
    if st.button("Lancer l'Analyse Intelligente"):
        with st.spinner("Recherche Google en cours..."):
            try:
                # Lecture et nettoyage
                content = uploaded_file.read().decode("utf-8")
                transcript = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
                
                # Utilisation de la syntaxe native "Tool" pour forcer la reconnaissance du moteur de recherche
                from google.generativeai import types

                # Configuration du modèle
                model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash',
                    tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]
                )

                prompt = f"""
                DATE : 05/01/2026. Premier Ministre : Sébastien Lecornu.
                MISSION : Secrétaire de rédaction expert. Analyse cette transcription.
                
                CONSIGNES :
                - RECHERCHE GOOGLE : Vérifie l'orthographe de Richard Werly (journaliste).
                - NOMENCLATURE : Gizeh, Saqqarah, Méhémet-Ali.
                - TABLEAU HTML : [Nom original | Correction | Justification basée sur le web].
                
                TRANSCRIPTION :
                {transcript[:5000]}  # Limite pour éviter les dépassements de token
                """

                response = model.generate_content(prompt)
                
                st.success("Analyse terminée !")
                st.download_button("📥 Télécharger la Bible de travail", response.text, "BIBLE_GENERE.html", "text/html")
                
                with st.expander("Voir le résultat"):
                    st.components.v1.html(response.text, height=500, scrolling=True)
                    
            except Exception as e:
                st.error(f"Erreur : {e}")

import streamlit as st

def render(fhir_client):
    st.markdown("# ➕ Patient erstellen")
    st.info("Hier integrieren wir die Textfelder und den Button, um die Ressource auf dem FHIR Testserver zu erstellen[cite: 1].")
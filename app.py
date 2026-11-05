import streamlit as st
from apis.patient_api import FhirClient
from views import home, retrieve_patient, create_patient

st.set_page_config(page_title="FHIR Patienten-Portal", page_icon="🏥", layout="centered")

# 1. Session State initialisieren, falls er noch nicht existiert
if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 Startseite"

fhir_client = FhirClient()

with st.sidebar:
    st.title("Navigation")
    # 2. Key="menu" verknüpft die Auswahl direkt mit dem Session State
    st.radio(
        "Aktion wählen:",
        ["🏠 Startseite", "🔍 Patient abrufen", "➕ Patient erstellen"],
        key="menu"
    )

# 3. Routing über den Session State steuern
if st.session_state.menu == "🏠 Startseite":
    home.render()
elif st.session_state.menu == "🔍 Patient abrufen":
    retrieve_patient.render(fhir_client)
elif st.session_state.menu == "➕ Patient erstellen":
    create_patient.render(fhir_client)
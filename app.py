import streamlit as st
from apis.patient_api import FhirClient
from views import home
from views.patient import patient_hub

st.set_page_config(page_title="FHIR Explorer", page_icon="🏥", layout="centered")

if "resource" not in st.session_state:
    st.session_state.resource = "🏠 Startseite"

patient_api = FhirClient()

# Hauptmenü: Ressourcen als Items
with st.sidebar:
    st.title("FHIR Ressourcen")
    st.radio(
        "Ressource auswählen:",
        ["🏠 Startseite", "👤 Patient", "📋 DiagnosticReport", "🔬 Observation"],
        key="resource"
    )

# Routing auf Ressource-Ebene
if st.session_state.resource == "🏠 Startseite":
    home.render()

elif st.session_state.resource == "👤 Patient":
    patient_hub.render(patient_api)

elif st.session_state.resource == "📋 DiagnosticReport":
    st.markdown("# 📋 Ressource: DiagnosticReport")
    st.info("Platzhalter: Hier können künftig Befundberichte abgerufen oder erstellt werden.")

elif st.session_state.resource == "🔬 Observation":
    st.markdown("# 🔬 Ressource: Observation")
    st.info("Platzhalter: Hier können künftig Messwerte und Beobachtungen verwaltet werden.")
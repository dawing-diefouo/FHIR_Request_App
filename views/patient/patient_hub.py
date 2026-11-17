import streamlit as st
from views.patient import retrieve_patient, create_patient


def render(patient_api):
    st.markdown("# 👤 Ressource: Patient")
    st.write("Wählen Sie eine Aktion für die Patienten-Ressource auf dem FHIR-Testserver.")

    # Aktionen innerhalb der Ressource
    tab_retrieve, tab_create = st.tabs([
        "🔍 Patient abrufen (GET)",
        "➕ Patient erstellen (POST)"
    ])

    with tab_retrieve:
        retrieve_patient.render(patient_api)

    with tab_create:
        create_patient.render(patient_api)
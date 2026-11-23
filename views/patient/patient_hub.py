import streamlit as st
from views.patient import retrieve_patient, create_patient, update_patient, delete_patient

def render(patient_api):
    st.markdown("# 👤 Ressource: Patient")
    st.write("Verwalten Sie Patientenressourcen auf dem FHIR-Testserver (CRUD).")

    aktion = st.segmented_control(
        "Aktion wählen:",
        options=[
            "🔍 Abrufen (GET)",
            "➕ Erstellen (POST)",
            "✏️ Aktualisieren (PUT)",
            "🗑️ Löschen (DELETE)"
        ],
        default="🔍 Abrufen (GET)",
        label_visibility="collapsed"
    )

    st.divider()

    if aktion == "🔍 Abrufen (GET)":
        retrieve_patient.render(patient_api)
    elif aktion == "➕ Erstellen (POST)":
        create_patient.render(patient_api)
    elif aktion == "✏️ Aktualisieren (PUT)":
        update_patient.render(patient_api)
    elif aktion == "🗑️ Löschen (DELETE)":
        delete_patient.render(patient_api)
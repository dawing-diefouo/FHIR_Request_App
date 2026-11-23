import streamlit as st
from views.patient import retrieve_patient, create_patient, update_patient, delete_patient

def render(patient_api):
    # --- Festes Aktionsmenü innerhalb der Ressource Patient ---
    col_title, col_menu = st.columns([1, 2], vertical_alignment="center")
    with col_title:
        st.markdown("### 👤 Patient (CRUD)")
    with col_menu:
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

    # --- Nur dieser Bereich scrollt; beide Menüleisten darüber bleiben immer stehen ---
    with st.container(height=550, border=False):
        if aktion == "🔍 Abrufen (GET)":
            retrieve_patient.render(patient_api)
        elif aktion == "➕ Erstellen (POST)":
            create_patient.render(patient_api)
        elif aktion == "✏️ Aktualisieren (PUT)":
            update_patient.render(patient_api)
        elif aktion == "🗑️ Löschen (DELETE)":
            delete_patient.render(patient_api)
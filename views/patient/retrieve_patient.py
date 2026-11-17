# views/patient/retrieve_patient.py
import streamlit as st

# Zuordnung: Was der Nutzer sieht -> Welches FHIR-Feld dahintersteckt
FILTER_OPTIONEN = {
    "👤 Stammdaten (Name, Geschlecht, Geburtsdatum)": ["name", "gender", "birthDate", "active", "maritalStatus"],
    "🪪 Identifikatoren": ["identifier"],
    "📍 Adressen & Kontaktdaten": ["address", "telecom"],
    "🔗 Referenzen & Angehörige": ["generalPractitioner", "managingOrganization", "contact"],
    "ℹ️ Metadaten & Profile": ["meta"]
}


def render(fhir_client):
    st.markdown("### Patient vom Server abrufen")

    patient_id = st.text_input("Bitte Patienten-ID eingeben (z.B. 591953):")

    # Mehrfachauswahl für gewünschte Informationen
    ausgewaehlte_bereiche = st.multiselect(
        "Welche Informationen sollen abgerufen/angezeigt werden?",
        options=list(FILTER_OPTIONEN.keys()),
        default=list(FILTER_OPTIONEN.keys())  # Standardmäßig alles ausgewählt
    )

    if st.button("Patient abrufen", type="primary"):
        if not patient_id:
            st.warning("Bitte geben Sie eine ID ein, bevor Sie suchen.")
        elif not ausgewaehlte_bereiche:
            st.warning("Bitte wählen Sie mindestens einen Informationsbereich aus.")
        else:
            # Alle benötigten FHIR-Felder aus der Auswahl sammeln
            fhir_elements = []
            for bereich in ausgewaehlte_bereiche:
                fhir_elements.extend(FILTER_OPTIONEN[bereich])

            with st.spinner(f"Lade ausgewählte Daten für Patient {patient_id}..."):
                try:
                    patient = fhir_client.fetch_patient(patient_id, elements=fhir_elements)
                    # Im Session State speichern, damit Filteränderungen danach erhalten bleiben
                    st.session_state["current_patient"] = patient
                    st.success("Patient erfolgreich gefunden!")
                except (ValueError, ConnectionError) as e:
                    st.session_state.pop("current_patient", None)
                    st.error(e)

    # Anzeige nur für die im Filter gewählten Bereiche rendern
    if "current_patient" in st.session_state:
        patient = st.session_state["current_patient"]
        tab1, tab2 = st.tabs(["📇 Gefiltertes Profil", "⚙️ JSON-Rohdaten"])

        with tab1:
            if "👤 Stammdaten (Name, Geschlecht, Geburtsdatum)" in ausgewaehlte_bereiche:
                st.subheader("👤 Stammdaten")
                col1, col2 = st.columns(2)
                col1.markdown(f"**Vorname:** {patient.first_name}")
                col2.markdown(f"**Nachname:** {patient.last_name}")
                col1.markdown(f"**Geschlecht:** `{patient.gender}`")
                col2.markdown(f"**Geburtsdatum:** `{patient.birth_date}`")
                st.divider()

            if "🪪 Identifikatoren" in ausgewaehlte_bereiche:
                st.subheader("🪪 Identifikatoren")
                st.markdown(f"**Logische Server-ID:** `{patient.id}`")
                if patient.identifiers:
                    st.dataframe(patient.identifiers, use_container_width=True, hide_index=True)
                st.divider()

            if "📍 Adressen & Kontaktdaten" in ausgewaehlte_bereiche:
                st.subheader("📍 Adressen & Kontaktdaten")
                for addr in patient.addresses:
                    st.markdown(f"- {addr['Straße']}, {addr['PLZ']} {addr['Ort']}")
                if patient.telecoms:
                    st.dataframe(patient.telecoms, use_container_width=True, hide_index=True)
                st.divider()

            if "🔗 Referenzen & Angehörige" in ausgewaehlte_bereiche:
                st.subheader("🔗 Referenzen & Angehörige")
                st.markdown(f"**Organisation:** {patient.managing_organization or 'Keine Angabe'}")
                st.markdown(f"**Hausarzt:** {', '.join(patient.general_practitioners) or 'Keine Angabe'}")
                st.divider()

            if "ℹ️ Metadaten & Profile" in ausgewaehlte_bereiche:
                st.subheader("ℹ️ Metadaten")
                st.markdown(f"**Zuletzt aktualisiert:** `{patient.last_updated}`")

        with tab2:
            st.json(patient.raw_data)
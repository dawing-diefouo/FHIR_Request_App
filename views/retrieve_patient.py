import streamlit as st


def render(fhir_client):
    st.markdown("# 🔍 Patient abrufen")

    # Textfeld und Button aus Aufgabe 1
    patient_id = st.text_input("Bitte Patienten-ID eingeben (z.B. 591953):")

    if st.button("Patient abrufen"):
        if patient_id:
            with st.spinner(f"Lade Daten für Patient {patient_id}..."):
                try:
                    patient = fhir_client.fetch_patient(patient_id)
                    st.success("Patient erfolgreich gefunden!")

                    tab1, tab2 = st.tabs(["📇 Profilübersicht", "⚙️ JSON-Rohdaten"])

                    with tab1:
                        st.subheader("Persönliche Daten")
                        st.divider()

                        with st.container():
                            col1, col2 = st.columns(2)
                            # Profilanzeige für abgerufenen Patienten in einzelnen Feldern
                            col1.markdown(f"**Vorname:** {patient.first_name}")
                            col2.markdown(f"**Nachname:** {patient.last_name}")

                            col3, col4 = st.columns(2)
                            col3.markdown(f"**Geschlecht:** `{patient.gender}`")
                            col4.markdown(f"**Geburtsdatum:** `{patient.birth_date}`")

                            st.markdown(f"**Logische Patienten-ID:** `{patient.id}`")

                    with tab2:
                        st.markdown("#### Antwort vom FHIR-Server")
                        # Anzeigen der abgefragten Resource vom Server[cite: 1]
                        st.json(patient.raw_data)

                except ValueError as ve:
                    st.error(ve)
                except ConnectionError as ce:
                    st.error(ce)
        else:
            st.warning("Bitte geben Sie eine ID ein, bevor Sie suchen.")
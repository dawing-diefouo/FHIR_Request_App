import streamlit as st
from apis.patient_api import FhirClient

# 1. Instanz des API-Clients erstellen
fhir_client = FhirClient()

# Titel mit Markdown formatieren
st.markdown("# 🏥 FHIR - Patientenabfrage")

# 2. UI-Elemente: Textfeld und Button integrieren
patient_id = st.text_input("Bitte Patienten-ID eingeben:", placeholder="z.B. 591953")

if st.button("Patient abrufen"):
    if patient_id:

        # 3. Ladeanimation starten
        with st.spinner(f"Lade Daten für Patient {patient_id}..."):
            try:
                # OOP: Objektorientierter Abruf über die ausgelagerte API-Klasse
                patient = fhir_client.fetch_patient(patient_id)

                # Status-Meldung bei Erfolg
                st.success("Patient erfolgreich auf dem FHIR-Testserver gefunden!")

                # --- Bessere Formatierung der Ausgabe ---

                # Tabs für eine aufgeräumte Darstellung
                tab1, tab2 = st.tabs(["📇 Profilübersicht", "⚙️ JSON-Rohdaten"])

                with tab1:
                    st.subheader("Persönliche Daten")
                    st.divider()  # Optische Trennlinie

                    # Container und Spalten für die Profilanzeige in einzelnen Feldern
                    with st.container():
                        col1, col2 = st.columns(2)
                        col1.markdown(f"**Vorname:** {patient.first_name}")
                        col2.markdown(f"**Nachname:** {patient.last_name}")

                        col3, col4 = st.columns(2)
                        col3.markdown(f"**Geschlecht:** `{patient.gender}`")
                        col4.markdown(f"**Geburtsdatum:** `{patient.birth_date}`")

                        st.markdown(f"**Logische Patienten-ID:** `{patient.id}`")

                with tab2:
                    st.markdown("#### Antwort vom FHIR-Server")
                    # Anzeigen der roh abgefragten Resource vom FHIR-Testserver
                    st.json(patient.raw_data)

            except ValueError as ve:
                st.error(ve)
            except ConnectionError as ce:
                st.error(ce)
    else:
        st.warning("Bitte geben Sie eine ID ein, bevor Sie suchen.")
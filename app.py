# app.py
import streamlit as st
from apis.patient_api import FhirClient

# Instanz des API-Clients erstellen
fhir_client = FhirClient()

st.title("FHIR - Patientenabfrage")

# UI-Elemente für die Abfrage[cite: 1]
patient_id = st.text_input("Bitte Patienten-ID eingeben:")

if st.button("Patient abrufen"):
    if patient_id:

        # 1. Ladeanimation starten
        with st.spinner(f"Lade Daten für Patient {patient_id}..."):
            try:
                # 2. OOP: Objektorientierter Abruf
                patient = fhir_client.fetch_patient(patient_id)

                # 3. Erfolgsanimation abspielen
                st.balloons()
                st.success("Patient erfolgreich gefunden!")

                # 4. Profilanzeige aus dem Model in einzelnen Feldern[cite: 1]
                st.subheader("Patientenprofil")
                col1, col2 = st.columns(2)
                col1.metric("Vorname", patient.first_name)
                col2.metric("Nachname", patient.last_name)

                col3, col4 = st.columns(2)
                col3.write(f"**Geschlecht:** {patient.gender}")
                col4.write(f"**Geburtsdatum:** {patient.birth_date}")

                st.write(f"**Logische ID:** {patient.id}")

                with st.expander("Rohdaten (JSON) anzeigen"):
                    st.json(patient.raw_data)

            except ValueError as ve:
                st.error(ve)
            except ConnectionError as ce:
                st.error(ce)
    else:
        st.warning("Bitte geben Sie eine ID ein, bevor Sie suchen.")
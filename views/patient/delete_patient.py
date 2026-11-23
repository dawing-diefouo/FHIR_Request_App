import streamlit as st

def render(fhir_client):
    st.markdown("### Patienten vom Server löschen (`DELETE`)")
    st.write("Prüfen Sie den Datensatz vor dem endgültigen Löschen anhand seiner logischen ID.")

    col_id, col_btn = st.columns([3, 1])
    patient_id = col_id.text_input("Patienten-ID eingeben:", key="delete_id_input")
    check_clicked = col_btn.button("Patient prüfen", use_container_width=True)

    if check_clicked:
        if not patient_id.strip():
            st.warning("Bitte geben Sie eine Patienten-ID ein.")
        else:
            with st.spinner(f"Suche Patient {patient_id.strip()}..."):
                try:
                    patient = fhir_client.fetch_patient(patient_id.strip())
                    st.session_state["delete_preview"] = patient
                except (ValueError, ConnectionError) as e:
                    st.session_state.pop("delete_preview", None)
                    st.error(e)

    if "delete_preview" in st.session_state:
        patient = st.session_state["delete_preview"]
        st.warning(f"Soll folgende Ressource wirklich gelöscht werden? (`Patient/{patient.id}`)")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Name:** {patient.first_name} {patient.last_name}")
            c2.markdown(f"**Logische ID:** `{patient.id}`")
            c1.markdown(f"**Geschlecht:** `{patient.gender}`")
            c2.markdown(f"**Geburtsdatum:** `{patient.birth_date}`")

        confirm = st.checkbox(
            "Ja, ich möchte diesen Patienten endgültig vom FHIR-Server entfernen.",
            key="confirm_delete_checkbox"
        )

        if st.button("🗑️ Patient endgültig löschen", type="primary", disabled=not confirm):
            with st.spinner(f"Lösche Patient/{patient.id}..."):
                try:
                    outcome = fhir_client.delete_patient(patient.id)
                    deleted_id = patient.id
                    # Caches für diesen Patienten bereinigen
                    st.session_state.pop("delete_preview", None)
                    if st.session_state.get("edit_patient") and st.session_state["edit_patient"].id == deleted_id:
                        st.session_state.pop("edit_patient", None)
                    if st.session_state.get("current_patient") and st.session_state["current_patient"].id == deleted_id:
                        st.session_state.pop("current_patient", None)

                    st.success(f"`Patient/{deleted_id}` wurde erfolgreich vom Server gelöscht.")
                    if outcome:
                        with st.expander("Server-Antwort (OperationOutcome) anzeigen"):
                            st.json(outcome)
                except (ValueError, ConnectionError) as e:
                    st.error(e)
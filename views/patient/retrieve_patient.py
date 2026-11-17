# views/patient/retrieve_patient.py
import streamlit as st


def render(fhir_client):
    st.markdown("### Patient vom Server abrufen")

    patient_id = st.text_input("Bitte Patienten-ID eingeben (z.B. 591953):")

    if st.button("Patient abrufen", type="primary"):
        if patient_id:
            with st.spinner(f"Lade alle Daten für Patient {patient_id}..."):
                try:
                    patient = fhir_client.fetch_patient(patient_id)
                    st.success("Patient erfolgreich gefunden!")

                    tab1, tab2 = st.tabs(["📇 Vollständiges Profil", "⚙️ JSON-Rohdaten"])

                    with tab1:
                        # --- 1. Stammdaten ---
                        st.subheader("👤 Stammdaten")
                        col1, col2 = st.columns(2)
                        titel_anzeige = f"{patient.prefix} " if patient.prefix else ""
                        col1.markdown(f"**Vorname:** {titel_anzeige}{patient.first_name}")
                        col2.markdown(f"**Nachname:** {patient.last_name}")

                        if patient.maiden_name:
                            st.markdown(f"**Geburtsname:** {patient.maiden_name}")
                        if len(patient.all_names) > 1:
                            st.markdown(f"**Alle hinterlegten Namen:** {', '.join(patient.all_names)}")

                        col3, col4 = st.columns(2)
                        col3.markdown(f"**Geschlecht:** `{patient.gender}`")
                        col4.markdown(f"**Geburtsdatum:** `{patient.birth_date}`")

                        col5, col6 = st.columns(2)
                        aktiv_text = "Ja" if patient.active is True else (
                            "Nein" if patient.active is False else "Keine Angabe")
                        col5.markdown(f"**Aktiv-Status:** {aktiv_text}")
                        col6.markdown(f"**Familienstand:** {patient.marital_status}")

                        col7, col8 = st.columns(2)
                        col7.markdown(f"**Verstorben:** {patient.deceased}")
                        sprachen = ", ".join(patient.languages) if patient.languages else "Keine Angabe"
                        col8.markdown(f"**Sprachen:** {sprachen}")

                        st.divider()

                        # --- 2. Identifikatoren (z. B. Versichertennummer, KIS-ID) ---
                        st.subheader("🪪 Identifikatoren")
                        st.markdown(f"**Logische Server-ID:** `{patient.id}`")
                        if patient.identifiers:
                            st.dataframe(patient.identifiers, use_container_width=True, hide_index=True)
                        else:
                            st.caption("Keine weiteren Identifikatoren hinterlegt.")

                        st.divider()

                        # --- 3. Adressen & Kontaktdaten ---
                        st.subheader("📍 Adressen & Kontaktdaten")
                        if patient.addresses:
                            for idx, addr in enumerate(patient.addresses, start=1):
                                st.markdown(
                                    f"**Adresse {idx} ({addr['Verwendung']}):** "
                                    f"{addr['Straße']}, {addr['PLZ']} {addr['Ort']} ({addr['Land']})"
                                )
                        else:
                            st.caption("Keine Adressdaten hinterlegt.")

                        if patient.telecoms:
                            st.dataframe(patient.telecoms, use_container_width=True, hide_index=True)
                        else:
                            st.caption("Keine Telefonnummern oder E-Mail-Adressen hinterlegt.")

                        st.divider()

                        # --- 4. Referenzen & Kontaktpersonen ---
                        st.subheader("🔗 Referenzen & Angehörige")
                        st.markdown(
                            f"**Zuständige Organisation:** "
                            f"{patient.managing_organization if patient.managing_organization else 'Keine Angabe'}"
                        )
                        if patient.general_practitioners:
                            st.markdown(
                                f"**Behandelnde Ärzte (General Practitioner):** {', '.join(patient.general_practitioners)}")
                        else:
                            st.markdown("**Behandelnde Ärzte (General Practitioner):** Keine Angabe")

                        if patient.contacts:
                            st.markdown("**Kontaktpersonen / Angehörige:**")
                            st.dataframe(patient.contacts, use_container_width=True, hide_index=True)

                        st.divider()

                        # --- 5. Metadaten, Profile & übrige Felder ---
                        st.subheader("ℹ️ Metadaten & weitere Felder")
                        st.markdown(f"**Zuletzt aktualisiert:** `{patient.last_updated}`")
                        if patient.profiles:
                            st.markdown("**Hinterlegte FHIR-Profile:**")
                            for prof in patient.profiles:
                                st.markdown(f"- `{prof}`")

                        if patient.extra_fields:
                            with st.expander("Weitere spezifische Felder / Extensions anzeigen"):
                                for key, val in patient.extra_fields.items():
                                    st.markdown(f"**{key}:**")
                                    st.write(val)

                    with tab2:
                        st.markdown("#### Antwort vom FHIR-Server")
                        st.json(patient.raw_data)

                except ValueError as ve:
                    st.error(ve)
                except ConnectionError as ce:
                    st.error(ce)
        else:
            st.warning("Bitte geben Sie eine ID ein, bevor Sie suchen.")
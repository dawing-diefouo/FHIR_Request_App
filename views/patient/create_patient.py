import datetime
import streamlit as st

GENDER_MAP = {
    "Männlich (male)": "male",
    "Weiblich (female)": "female",
    "Divers / Andere (other)": "other",
    "Unbekannt (unknown)": "unknown"
}

def render(fhir_client):
    st.markdown("### Neuen Patienten auf dem FHIR-Server erstellen")
    st.write("Füllen Sie die Felder aus, um eine neue `Patient`-Ressource per `POST` anzulegen.")

    with st.form("create_patient_form"):
        # --- 1. Stammdaten ---
        st.subheader("👤 Stammdaten")
        col1, col2, col3 = st.columns([1, 2, 2])
        prefix = col1.text_input("Titel (optional)", placeholder="z.B. Dr.")
        first_name = col2.text_input("Vorname *", placeholder="Max")
        last_name = col3.text_input("Nachname *", placeholder="Mustermann")

        col4, col5 = st.columns(2)
        gender_label = col4.selectbox("Geschlecht *", options=list(GENDER_MAP.keys()))
        birth_date = col5.date_input(
            "Geburtsdatum *",
            value=datetime.date(1990, 1, 1),
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today()
        )

        # --- 2. Identifikator & Status ---
        st.subheader("🪪 Identifikator & Status")
        col6, col7 = st.columns(2)
        kvid = col6.text_input("Versicherten-ID / Identifier (optional)", placeholder="A123456789")
        active = col7.checkbox("Patientendatensatz ist aktiv", value=True)

        # --- 3. Adresse (optional) ---
        st.subheader("📍 Adresse (optional)")
        street = st.text_input("Straße und Hausnummer", placeholder="Musterstraße 12")
        col8, col9, col10 = st.columns([1, 2, 1])
        postal_code = col8.text_input("PLZ", placeholder="14770")
        city = col9.text_input("Stadt", placeholder="Brandenburg an der Havel")
        country = col10.text_input("Land", value="DE")

        # --- 4. Kontaktdaten (optional) ---
        st.subheader("📞 Kontaktdaten (optional)")
        col11, col12 = st.columns(2)
        phone = col11.text_input("Telefon", placeholder="+49 170 1234567")
        email = col12.text_input("E-Mail", placeholder="max.mustermann@example.de")

        submitted = st.form_submit_button("➕ Patient auf Server erstellen", type="primary", use_container_width=True)

    # Verarbeitung nach Klick auf den Button
    if submitted:
        if not first_name.strip() or not last_name.strip():
            st.warning("Bitte geben Sie mindestens Vorname und Nachname ein.")
            return

        # FHIR-konformes Name-Objekt zusammenbauen
        name_entry = {
            "use": "official",
            "family": last_name.strip(),
            "given": [first_name.strip()]
        }
        if prefix.strip():
            name_entry["prefix"] = [prefix.strip()]

        # Basis-Payload für FHIR R4 Patient
        patient_payload = {
            "resourceType": "Patient",
            "active": active,
            "name": [name_entry],
            "gender": GENDER_MAP[gender_label],
            "birthDate": birth_date.isoformat()
        }

        # Optionale Identifikatoren ergänzen
        if kvid.strip():
            patient_payload["identifier"] = [{
                "system": "http://fhir.de/sid/gkv/kvid-10",
                "value": kvid.strip()
            }]

        # Optionale Adresse ergänzen
        if street.strip() or postal_code.strip() or city.strip():
            addr_entry = {"use": "home"}
            if street.strip():
                addr_entry["line"] = [street.strip()]
            if postal_code.strip():
                addr_entry["postalCode"] = postal_code.strip()
            if city.strip():
                addr_entry["city"] = city.strip()
            if country.strip():
                addr_entry["country"] = country.strip()
            patient_payload["address"] = [addr_entry]

        # Optionale Kontaktdaten ergänzen
        telecom_list = []
        if phone.strip():
            telecom_list.append({"system": "phone", "value": phone.strip(), "use": "home"})
        if email.strip():
            telecom_list.append({"system": "email", "value": email.strip(), "use": "home"})
        if telecom_list:
            patient_payload["telecom"] = telecom_list

        # POST-Request an den FHIR-Server senden
        with st.spinner("Sende Patientenressource an den FHIR-Testserver..."):
            try:
                created_patient = fhir_client.create_patient(patient_payload)
                st.success("Patient erfolgreich auf dem FHIR-Testserver erstellt!")

                # Vom Server vergebene logische ID hervorheben
                st.info(f"**Vom Server vergebene logische Patienten-ID:** `{created_patient.id}`")

                tab1, tab2 = st.tabs(["📇 Erstelltes Profil", "⚙️ Server-Antwort (JSON)"])

                with tab1:
                    c1, c2 = st.columns(2)
                    titel = f"{created_patient.prefix} " if created_patient.prefix else ""
                    c1.markdown(f"**Name:** {titel}{created_patient.first_name} {created_patient.last_name}")
                    c2.markdown(f"**Logische ID:** `{created_patient.id}`")

                    c3, c4 = st.columns(2)
                    c3.markdown(f"**Geschlecht:** `{created_patient.gender}`")
                    c4.markdown(f"**Geburtsdatum:** `{created_patient.birth_date}`")

                    if created_patient.identifiers:
                        st.markdown(f"**Identifier:** `{created_patient.identifiers[0]['Wert']}`")
                    if created_patient.addresses:
                        addr = created_patient.addresses[0]
                        st.markdown(f"**Adresse:** {addr['Straße']}, {addr['PLZ']} {addr['Ort']} ({addr['Land']})")
                    if created_patient.telecoms:
                        kontakte = ", ".join(f"{t['Kanal']}: {t['Wert']}" for t in created_patient.telecoms)
                        st.markdown(f"**Kontakt:** {kontakte}")

                with tab2:
                    st.json(created_patient.raw_data)

            except (ValueError, ConnectionError) as e:
                st.error(e)
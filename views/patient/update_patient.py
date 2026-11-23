import copy
import datetime
import streamlit as st

GENDER_MAP = {
    "Männlich (male)": "male",
    "Weiblich (female)": "female",
    "Divers / Andere (other)": "other",
    "Unbekannt (unknown)": "unknown"
}
REVERSE_GENDER_MAP = {v: k for k, v in GENDER_MAP.items()}

def render(fhir_client):
    st.markdown("### Bestehenden Patienten aktualisieren ")
    st.write("Laden Sie zuerst den Patienten über seine logische ID, um die aktuellen Daten zu bearbeiten.")

    col_id, col_btn = st.columns([3, 1])
    patient_id = col_id.text_input("Patienten-ID eingeben:", key="update_id_input")
    load_clicked = col_btn.button("Daten laden", use_container_width=True)

    if load_clicked:
        if not patient_id.strip():
            st.warning("Bitte geben Sie eine Patienten-ID ein.")
        else:
            with st.spinner(f"Lade Patient {patient_id.strip()}..."):
                try:
                    patient = fhir_client.fetch_patient(patient_id.strip())
                    st.session_state["edit_patient"] = patient
                except (ValueError, ConnectionError) as e:
                    st.session_state.pop("edit_patient", None)
                    st.error(e)

    # Formular anzeigen, sobald ein Patient geladen wurde
    if "edit_patient" in st.session_state:
        patient = st.session_state["edit_patient"]
        st.info(f"Bearbeite **Patient/{patient.id}** (Letzte Änderung: `{patient.last_updated}`)")

        # Vorhandene Werte für die Formularfelder vorbereiten
        default_gender_label = REVERSE_GENDER_MAP.get(patient.gender, "Unbekannt (unknown)")
        try:
            default_dob = datetime.date.fromisoformat(patient.birth_date)
        except ValueError:
            default_dob = datetime.date(1990, 1, 1)

        default_active = True if patient.active is None else bool(patient.active)
        default_kvid = patient.identifiers[0]["Wert"] if patient.identifiers and patient.identifiers[0]["Wert"] != "-" else ""

        addr = patient.addresses[0] if patient.addresses else {}
        default_street = "" if addr.get("Straße") in (None, "-") else addr["Straße"]
        default_plz = "" if addr.get("PLZ") in (None, "-") else addr["PLZ"]
        default_city = "" if addr.get("Ort") in (None, "-") else addr["Ort"]
        default_country = "DE" if addr.get("Land") in (None, "-") else addr["Land"]

        default_phone = next((t["Wert"] for t in patient.telecoms if t["Kanal"] == "phone" and t["Wert"] != "-"), "")
        default_email = next((t["Wert"] for t in patient.telecoms if t["Kanal"] == "email" and t["Wert"] != "-"), "")

        with st.form("update_patient_form"):
            st.subheader("👤 Stammdaten")
            c1, c2, c3 = st.columns([1, 2, 2])
            prefix = c1.text_input("Titel", value=patient.prefix)
            first_name = c2.text_input("Vorname *", value="" if patient.first_name == "N/A" else patient.first_name)
            last_name = c3.text_input("Nachname *", value="" if patient.last_name == "N/A" else patient.last_name)

            c4, c5 = st.columns(2)
            gender_options = list(GENDER_MAP.keys())
            gender_label = c4.selectbox("Geschlecht *", options=gender_options, index=gender_options.index(default_gender_label))
            birth_date = c5.date_input(
                "Geburtsdatum *",
                value=default_dob,
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today()
            )

            st.subheader("🪪 Identifikator & Status")
            c6, c7 = st.columns(2)
            kvid = c6.text_input("Versicherten-ID / Identifier", value=default_kvid)
            active = c7.checkbox("Patientendatensatz ist aktiv", value=default_active)

            st.subheader("📍 Adresse")
            street = st.text_input("Straße und Hausnummer", value=default_street)
            c8, c9, c10 = st.columns([1, 2, 1])
            postal_code = c8.text_input("PLZ", value=default_plz)
            city = c9.text_input("Stadt", value=default_city)
            country = c10.text_input("Land", value=default_country)

            st.subheader("📞 Kontaktdaten")
            c11, c12 = st.columns(2)
            phone = c11.text_input("Telefon", value=default_phone)
            email = c12.text_input("E-Mail", value=default_email)

            submitted = st.form_submit_button("💾 Änderungen speichern (PUT)", type="primary", use_container_width=True)

        if submitted:
            if not first_name.strip() or not last_name.strip():
                st.warning("Vorname und Nachname dürfen nicht leer sein.")
                return

            # Bestehende Rohdaten kopieren, um unberührte Felder zu erhalten
            updated_payload = copy.deepcopy(patient.raw_data)
            updated_payload["active"] = active
            updated_payload["gender"] = GENDER_MAP[gender_label]
            updated_payload["birthDate"] = birth_date.isoformat()

            name_entry = {
                "use": "official",
                "family": last_name.strip(),
                "given": [first_name.strip()]
            }
            if prefix.strip():
                name_entry["prefix"] = [prefix.strip()]
            updated_payload["name"] = [name_entry]

            if kvid.strip():
                updated_payload["identifier"] = [{
                    "system": "http://fhir.de/sid/gkv/kvid-10",
                    "value": kvid.strip()
                }]
            else:
                updated_payload.pop("identifier", None)

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
                updated_payload["address"] = [addr_entry]
            else:
                updated_payload.pop("address", None)

            telecom_list = []
            if phone.strip():
                telecom_list.append({"system": "phone", "value": phone.strip(), "use": "home"})
            if email.strip():
                telecom_list.append({"system": "email", "value": email.strip(), "use": "home"})
            if telecom_list:
                updated_payload["telecom"] = telecom_list
            else:
                updated_payload.pop("telecom", None)

            with st.spinner("Aktualisiere Patientenressource auf dem Server..."):
                try:
                    updated_patient = fhir_client.update_patient(patient.id, updated_payload)
                    st.session_state["edit_patient"] = updated_patient
                    st.success(f"Patient/{updated_patient.id} erfolgreich aktualisiert!")
                    with st.expander("Aktualisierte Server-Antwort (JSON) anzeigen"):
                        st.json(updated_patient.raw_data)
                except (ValueError, ConnectionError) as e:
                    st.error(e)
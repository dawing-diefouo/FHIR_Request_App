# models/patient_model.py

class PatientModel:
    # Felder, die wir explizit und strukturiert verarbeiten
    HANDLED_KEYS = {
        "resourceType", "id", "meta", "text", "active", "name", "telecom",
        "gender", "birthDate", "deceasedBoolean", "deceasedDateTime",
        "address", "maritalStatus", "contact", "communication",
        "generalPractitioner", "managingOrganization", "identifier"
    }

    def __init__(self, fhir_json: dict):
        self.raw_data = fhir_json
        self.id = fhir_json.get("id", "N/A")
        self.active = fhir_json.get("active", None)
        self.gender = fhir_json.get("gender", "N/A")
        self.birth_date = fhir_json.get("birthDate", "N/A")

        # Metadaten & hinterlegte Profile (z. B. deutsches Basisprofil)
        meta = fhir_json.get("meta", {})
        self.last_updated = meta.get("lastUpdated", "N/A")
        self.profiles = meta.get("profile", [])

        # Namen (inkl. aller Vornamen, Titel und ggf. Geburtsname)
        self._parse_names(fhir_json.get("name", []))

        # Verstorben-Status
        self.deceased = self._parse_deceased(fhir_json)

        # Familienstand & Sprachen
        self.marital_status = self._parse_codeable_concept(fhir_json.get("maritalStatus"))
        self.languages = self._parse_languages(fhir_json.get("communication", []))

        # Listen-Strukturen: Identifier, Kontaktdaten, Adressen, Angehörige
        self.identifiers = self._parse_identifiers(fhir_json.get("identifier", []))
        self.telecoms = self._parse_telecoms(fhir_json.get("telecom", []))
        self.addresses = self._parse_addresses(fhir_json.get("address", []))
        self.contacts = self._parse_contacts(fhir_json.get("contact", []))

        # Referenzen auf andere FHIR-Ressourcen (z. B. Hausarzt, Organisation)
        self.general_practitioners = self._parse_references(fhir_json.get("generalPractitioner", []))
        self.managing_organization = self._parse_single_reference(fhir_json.get("managingOrganization"))

        # Alle übrigen Felder dynamisch auffangen, damit nichts verloren geht
        self.extra_fields = {
            k: v for k, v in fhir_json.items() if k not in self.HANDLED_KEYS
        }

    def _parse_names(self, name_list: list):
        self.first_name = "N/A"
        self.last_name = "N/A"
        self.prefix = ""
        self.maiden_name = None
        self.all_names = []

        if not name_list:
            return

        # Offiziellen Namen bevorzugen, sonst ersten Eintrag nehmen
        official = next((n for n in name_list if n.get("use") == "official"), name_list[0])
        given_list = official.get("given", [])
        self.first_name = " ".join(given_list) if given_list else official.get("text", "N/A")
        self.last_name = official.get("family", "N/A")
        self.prefix = " ".join(official.get("prefix", []))

        # Nach weiteren Namenseinträgen suchen (z. B. Geburtsname / use="maiden")
        for n in name_list:
            if n.get("use") == "maiden" and "family" in n:
                self.maiden_name = n["family"]
            formatted = f"{' '.join(n.get('prefix', []))} {' '.join(n.get('given', []))} {n.get('family', '')}".strip()
            if not formatted and "text" in n:
                formatted = n["text"]
            if formatted:
                use_label = f" ({n['use']})" if "use" in n else ""
                self.all_names.append(f"{formatted}{use_label}")

    def _parse_deceased(self, fhir_json: dict) -> str:
        if "deceasedDateTime" in fhir_json:
            return f"Ja ({fhir_json['deceasedDateTime']})"
        if "deceasedBoolean" in fhir_json:
            return "Ja" if fhir_json["deceasedBoolean"] else "Nein"
        return "Keine Angabe"

    def _parse_codeable_concept(self, cc: dict | None) -> str:
        if not cc:
            return "N/A"
        if "text" in cc:
            return cc["text"]
        codings = cc.get("coding", [])
        if codings:
            return codings[0].get("display") or codings[0].get("code") or "N/A"
        return "N/A"

    def _parse_languages(self, comm_list: list) -> list[str]:
        result = []
        for entry in comm_list:
            lang = self._parse_codeable_concept(entry.get("language"))
            if lang != "N/A":
                pref = " (bevorzugt)" if entry.get("preferred") else ""
                result.append(f"{lang}{pref}")
        return result

    def _parse_identifiers(self, id_list: list) -> list[dict]:
        parsed = []
        for item in id_list:
            parsed.append({
                "Typ": self._parse_codeable_concept(item.get("type")),
                "System": item.get("system", "-"),
                "Wert": item.get("value", "-"),
                "Verwendung": item.get("use", "-")
            })
        return parsed

    def _parse_telecoms(self, telecom_list: list) -> list[dict]:
        parsed = []
        for item in telecom_list:
            parsed.append({
                "Kanal": item.get("system", "-"),
                "Wert": item.get("value", "-"),
                "Verwendung": item.get("use", "-")
            })
        return parsed

    def _parse_addresses(self, addr_list: list) -> list[dict]:
        parsed = []
        for item in addr_list:
            lines = ", ".join(item.get("line", []))
            parsed.append({
                "Verwendung": item.get("use", "-"),
                "Straße": lines or "-",
                "PLZ": item.get("postalCode", "-"),
                "Ort": item.get("city", "-"),
                "Bundesland": item.get("state", "-"),
                "Land": item.get("country", "-")
            })
        return parsed

    def _parse_contacts(self, contact_list: list) -> list[dict]:
        parsed = []
        for c in contact_list:
            rels = [self._parse_codeable_concept(r) for r in c.get("relationship", [])]
            name_obj = c.get("name", {})
            c_name = f"{' '.join(name_obj.get('given', []))} {name_obj.get('family', '')}".strip() or name_obj.get("text", "-")
            phones = [t.get("value", "") for t in c.get("telecom", []) if t.get("value")]
            parsed.append({
                "Name": c_name,
                "Beziehung": ", ".join(rels) if rels else "-",
                "Kontakt": ", ".join(phones) if phones else "-"
            })
        return parsed

    def _parse_references(self, ref_list: list) -> list[str]:
        refs = []
        for r in ref_list:
            formatted = self._parse_single_reference(r)
            if formatted:
                refs.append(formatted)
        return refs

    def _parse_single_reference(self, ref: dict | None) -> str | None:
        if not ref:
            return None
        display = ref.get("display", "")
        target = ref.get("reference", "")
        if display and target:
            return f"{display} (`{target}`)"
        return display or f"`{target}`" if target else None
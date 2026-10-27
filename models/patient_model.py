# models.py
class PatientModel:
    def __init__(self, fhir_json):
        self.id = fhir_json.get("id", "N/A")

        # Namensextraktion
        name_list = fhir_json.get("name", [{}])
        self.first_name = name_list[0].get("given", ["N/A"])[0] if name_list and "given" in name_list[0] else "N/A"
        self.last_name = name_list[0].get("family", "N/A") if name_list else "N/A"

        # Weitere Profildaten
        self.gender = fhir_json.get("gender", "N/A")
        self.birth_date = fhir_json.get("birthDate", "N/A")

        # Rohdaten für spätere Verwendung speichern
        self.raw_data = fhir_json
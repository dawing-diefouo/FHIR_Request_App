import requests
from models.patient_model import PatientModel

class FhirClient:
    def __init__(self, base_url="https://hapi.fhir.org/baseR4"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }

    def fetch_patient(self, patient_id: str, elements: list[str] | None = None) -> PatientModel:
        req_url = f"{self.base_url}/Patient/{patient_id}"
        params = {"_elements": ",".join(elements)} if elements else {}

        response = requests.get(req_url, params=params, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("resourceType") != "Patient":
                raise ValueError(f"Unerwarteter Ressourcentyp erhalten: {data.get('resourceType')}")
            return PatientModel(data)
        elif response.status_code == 404:
            raise ValueError("Patient nicht gefunden.")
        elif response.status_code == 410:
            raise ValueError("Dieser Patient wurde bereits vom Server gelöscht (410 Gone).")
        else:
            raise ConnectionError(f"HTTP-Fehler beim Abrufen: {response.status_code}")

    def create_patient(self, patient_payload: dict) -> PatientModel:
        req_url = f"{self.base_url}/Patient"
        response = requests.post(req_url, json=patient_payload, headers=self.headers)

        if response.status_code == 201:
            data = response.json()
            if data.get("resourceType") != "Patient":
                raise ValueError(f"Unerwartete Server-Antwort: {data.get('resourceType')}")
            return PatientModel(data)
        elif response.status_code in (400, 422):
            raise ValueError(f"Server hat die Ressource abgelehnt ({response.status_code}): {response.text}")
        else:
            raise ConnectionError(f"HTTP-Fehler beim Erstellen (Status {response.status_code}): {response.text}")

    def update_patient(self, patient_id: str, patient_payload: dict) -> PatientModel:
        req_url = f"{self.base_url}/Patient/{patient_id}"
        # FHIR-Pflicht: resourceType und id im Body müssen zur URL passen
        patient_payload["resourceType"] = "Patient"
        patient_payload["id"] = patient_id

        response = requests.put(req_url, json=patient_payload, headers=self.headers)

        if response.status_code in (200, 201):
            data = response.json()
            if data.get("resourceType") != "Patient":
                raise ValueError(f"Unerwartete Server-Antwort: {data.get('resourceType')}")
            return PatientModel(data)
        elif response.status_code == 404:
            raise ValueError("Patient für Update nicht gefunden.")
        elif response.status_code in (400, 422):
            raise ValueError(f"Validierungsfehler beim Update ({response.status_code}): {response.text}")
        else:
            raise ConnectionError(f"HTTP-Fehler beim Aktualisieren (Status {response.status_code}): {response.text}")

    def delete_patient(self, patient_id: str) -> dict | None:
        req_url = f"{self.base_url}/Patient/{patient_id}"
        response = requests.delete(req_url, headers=self.headers)

        if response.status_code in (200, 202, 204):
            # 204 No Content hat keinen Antwort-Body
            return response.json() if response.text.strip() else None
        elif response.status_code == 404:
            raise ValueError("Patient nicht gefunden oder bereits gelöscht.")
        else:
            raise ConnectionError(f"HTTP-Fehler beim Löschen (Status {response.status_code}): {response.text}")
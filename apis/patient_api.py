# api.py
import requests
from models.patient_model import PatientModel


class FhirClient:
    def __init__(self, base_url="http://hapi.fhir.org/baseR4"):
        self.base_url = base_url

    def fetch_patient(self, patient_id):
        req_url = f"{self.base_url}/Patient/{patient_id}"
        response = requests.get(req_url)

        if response.status_code == 200:
            return PatientModel(response.json())
        elif response.status_code == 404:
            raise ValueError("Patient nicht gefunden.")
        else:
            raise ConnectionError(f"HTTP-Fehler: {response.status_code}")
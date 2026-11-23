import streamlit as st
from apis.patient_api import FhirClient
from views import home
from views.patient import patient_hub

st.set_page_config(page_title="FHIR Explorer", page_icon="🏥", layout="wide")

# Oberen Standard-Abstand etwas verringern, damit die Menüs kompakt oben sitzen
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2.8rem;
            padding-bottom: 0.5rem;
        }
        hr {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "resource" not in st.session_state:
    st.session_state.resource = "🏠 Startseite"

def set_resource(name: str):
    st.session_state.resource = name

patient_api = FhirClient()

MENU_ITEMS = [
    "🏠 Startseite",
    "👤 Patient",
    "📋 DiagnosticReport",
    "🔬 Observation",
]

# --- Festes Hauptmenü ---
nav_cols = st.columns(len(MENU_ITEMS))
for col, item in zip(nav_cols, MENU_ITEMS):
    is_active = st.session_state.resource == item
    with col:
        st.button(
            item,
            key=f"nav_{item}",
            use_container_width=True,
            type="primary" if is_active else "tertiary",
            on_click=set_resource,
            args=(item,)
        )

st.divider()

# --- Routing ---
if st.session_state.resource == "👤 Patient":
    # Patient-Hub verwaltet sein eigenes festes Untermenü + Scroll-Bereich
    patient_hub.render(patient_api)
else:
    # Alle übrigen Seiten in einem eigenen Scroll-Bereich rendern
    with st.container(height=620, border=False):
        if st.session_state.resource == "🏠 Startseite":
            home.render()
        elif st.session_state.resource == "📋 DiagnosticReport":
            st.markdown("## 📋 Ressource: DiagnosticReport")
            st.info("Platzhalter für Befundberichte.")
        elif st.session_state.resource == "🔬 Observation":
            st.markdown("## 🔬 Ressource: Observation")
            st.info("Platzhalter für Messwerte.")
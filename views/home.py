import streamlit as st


# Diese Callback-Funktion ändert den Status, bevor die Seite neu lädt
def switch_page(page_name):
    st.session_state.menu = page_name


def render():
    st.markdown("# 🏥 FHIR Patienten-Portal")
    st.write("Willkommen! Über dieses Portal können Sie Patientenressourcen auf dem FHIR-Testserver verwalten.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 Abrufen")
        st.write("Vorhandene Patienten über ihre logische ID auf dem Server suchen und das Patientenprofil anzeigen.")

        # Aufruf der Callback-Funktion über on_click und Übergabe des Ziel-Namens über args
        st.button(
            "➔ Zum Abruf-Bereich",
            use_container_width=True,
            type="primary",
            on_click=switch_page,
            args=("🔍 Patient abrufen",)
        )

    with col2:
        st.markdown("### ➕ Erstellen")
        st.write("Neue Patientenressourcen anlegen und strukturiert an den FHIR-Server senden.")

        # Aufruf der Callback-Funktion für die Erstellen-Seite
        st.button(
            "➔ Zum Erstellen-Bereich",
            use_container_width=True,
            type="primary",
            on_click=switch_page,
            args=("➕ Patient erstellen",)
        )
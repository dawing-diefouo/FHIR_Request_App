import streamlit as st


def select_resource(resource_name):
    st.session_state.resource = resource_name


def render():
    st.markdown("# 🏥 FHIR Ressourcen-Portal")
    st.write("Wählen Sie eine FHIR-Ressource aus, um Daten vom Testserver abzurufen oder neu anzulegen.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Patient")
        st.write("Stammdaten verwalten: Patienten per ID abrufen oder neue Patienten anlegen.")
        st.button(
            "Patient öffnen ➔",
            use_container_width=True,
            type="primary",
            on_click=select_resource,
            args=("👤 Patient",)
        )

    with col2:
        st.markdown("### 📋 DiagnosticReport")
        st.write("Klinische Befundberichte und deren Referenzen auf Patienten einsehen.")
        st.button(
            "DiagnosticReport öffnen ➔",
            use_container_width=True,
            on_click=select_resource,
            args=("📋 DiagnosticReport",)
        )
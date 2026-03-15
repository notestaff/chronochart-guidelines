import streamlit as st
import json
from rag_search import clinical_decision_support

# Configure the page
st.set_page_config(page_title="IRIS Clinical AI", page_icon="🏥", layout="centered")

st.title("🏥 FHIR-Native Clinical Decision Support")
st.markdown("**Powered by InterSystems IRIS Vector Search & Gemini 3 Flash**")
st.divider()

# The 3 test scenarios we built into the FHIR server
patients = {
    "Ashleigh Collins (Major Depressive Disorder)": "19-year-old female with Major Depressive Disorder. She has been on Sertraline 50mg for 12 weeks. Her recent PHQ-9 score is 18 (severe).",
    "Denae Mohr (Schizophrenia)": "16-year-old female with Schizophrenia. On Olanzapine 10mg for 6 months. Recent HbA1c is 6.2% (pre-diabetes), and she exhibits significant weight gain.",
    "Eldridge Lowe (Generalized Anxiety)": "51-year-old male with Generalized Anxiety Disorder. On Escitalopram 10mg for 14 months. Recent GAD-7 score is 4 (remission). Reports feeling calm and sleeping well."
}

# UI: Patient Selection
st.subheader("1. Extract Patient Data (FHIR)")
selected_patient = st.selectbox("Select a patient from the InterSystems server:", list(patients.keys()))
patient_summary = patients[selected_patient]

st.info(f"**Synthesized Clinical Record:**\n\n{patient_summary}")

# UI: Analysis Button
if st.button("🧠 Run AI Clinical Analysis", type="primary"):
    with st.spinner("Executing InterSystems IRIS Vector Search & Gemini Reasoning..."):
        try:
            # Call the backend function we just perfected
            result = clinical_decision_support(patient_summary)
            
            st.divider()
            st.subheader("2. AI Recommendation")
            
            # Display the results based on the status
            status = result.get("status", "UNKNOWN")
            if status == "CHANGE_RECOMMENDED":
                st.warning(f"**Status:** {status} ⚠️")
            else:
                st.success(f"**Status:** {status} ✅")
                
            st.write(f"**Recommended Action:** {result.get('action')}")
            st.write(f"**Rationale:** {result.get('rationale')}")
            
            st.write("**Literature Citations (Retrieved from IRIS):**")
            for citation in result.get("citations", []):
                st.markdown(f"- 📄 `{citation}`")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

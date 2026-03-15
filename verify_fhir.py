import requests
import json

# --- InterSystems Configuration ---
FHIR_BASE_URL = "http://localhost:32783/csp/healthshare/demo/fhir/r4/" 
AUTH = ("_SYSTEM", "ISCDEMO")
HEADERS = {
    "Accept": "application/fhir+json"
}

def verify_data():
    print("🔍 Checking InterSystems FHIR Server...\n")
    
    # 1. Fetch all patients
    url = f"{FHIR_BASE_URL}Patient"
    response = requests.get(url, auth=AUTH, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Error connecting to FHIR server: {response.status_code}")
        print(response.text)
        return
        
    data = response.json()
    entries = data.get("entry", [])
    
    print(f"✅ Found {len(entries)} patients in the database.")
    print("-" * 50)
    
    for entry in entries:
        patient = entry["resource"]
        patient_id = patient["id"]
        
        # Safely extract the patient's name
        name_list = patient.get("name", [{}])[0]
        first_name = " ".join(name_list.get("given", ["Unknown"]))
        last_name = name_list.get("family", "Unknown")
        
        print(f"👤 Patient: {first_name} {last_name} (ID: {patient_id})")
        
        # 2. Check Conditions (Diagnoses)
        cond_url = f"{FHIR_BASE_URL}Condition?patient={patient_id}"
        cond_resp = requests.get(cond_url, auth=AUTH, headers=HEADERS).json()
        cond_count = len(cond_resp.get("entry", []))
        print(f"   ↳ Conditions found: {cond_count}")
        
        # 3. Check Medications
        med_url = f"{FHIR_BASE_URL}MedicationRequest?patient={patient_id}"
        med_resp = requests.get(med_url, auth=AUTH, headers=HEADERS).json()
        med_count = len(med_resp.get("entry", []))
        print(f"   ↳ Medications found: {med_count}")
        
        # 4. Check Observations (Labs/Assessments)
        obs_url = f"{FHIR_BASE_URL}Observation?patient={patient_id}"
        obs_resp = requests.get(obs_url, auth=AUTH, headers=HEADERS).json()
        obs_count = len(obs_resp.get("entry", []))
        print(f"   ↳ Observations found: {obs_count}")
        print("-" * 50)

if __name__ == "__main__":
    verify_data()

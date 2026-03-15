import os
import json
import requests

# --- InterSystems Configuration ---
FHIR_BASE_URL = "http://localhost:32783/csp/healthshare/demo/fhir/r4/" 
AUTH = ("_SYSTEM", "ISCDEMO")
HEADERS = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}

def upload_bundle(filepath, filename):
    with open(filepath, 'r') as file:
        bundle_data = json.load(file)
        
    print(f"Uploading {filename}...")
    response = requests.post(FHIR_BASE_URL, auth=AUTH, headers=HEADERS, json=bundle_data)
    
    if response.status_code in [200, 201]:
        print(f"✅ Success!")
    else:
        print(f"❌ Failed. Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

def load_all_in_order(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' not found.")
        return

    # 1. Upload Hospitals & Locations FIRST
    for filename in os.listdir(directory_path):
        if filename.startswith("hospital") and filename.endswith(".json"):
            upload_bundle(os.path.join(directory_path, filename), filename)
            
    # 2. Upload Practitioners (Doctors) SECOND
    for filename in os.listdir(directory_path):
        if filename.startswith("practitioner") and filename.endswith(".json"):
            upload_bundle(os.path.join(directory_path, filename), filename)
            
    # 3. Upload Groomed Patients LAST
    for filename in os.listdir(directory_path):
        if not filename.startswith("hospital") and not filename.startswith("practitioner") and filename.endswith(".json"):
            upload_bundle(os.path.join(directory_path, filename), filename)

if __name__ == "__main__":
    load_all_in_order("./groomed_patients")
    

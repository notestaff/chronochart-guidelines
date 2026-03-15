print("=== RAG Search Script v1.2 ===")

import iris
import json
import os
from sentence_transformers import SentenceTransformer

# The new, modern Gemini SDK
from google import genai
from google.genai import types

# --- CONFIGURATION ---
HOST = "localhost"
PORT = 32782  
NAMESPACE = "USER"
DB_USER = "_SYSTEM"
PASSWORD = "ISCDEMO"

# The new SDK automatically picks up the GEMINI_API_KEY environment variable
client = genai.Client()

MODEL_NAME = 'all-MiniLM-L6-v2'

def get_relevant_guidelines(query_text, top_k=2):
    """Embeds the query and uses InterSystems IRIS Vector Search to find the best guidelines."""
    model = SentenceTransformer(MODEL_NAME)
    
    # 1. Convert the search query into a vector
    query_vector = model.encode(query_text, normalize_embeddings=True).tolist()
    vector_string = str(query_vector)

    # 2. Connect to IRIS and perform the Vector Search
    conn = iris.connect(hostname=HOST, port=PORT, namespace=NAMESPACE, username=DB_USER, password=PASSWORD)
    cursor = conn.cursor()
    
    sql = """
        SELECT TOP ? DocumentTitle, ChunkText, VECTOR_DOT_PRODUCT(VectorEmbed, TO_VECTOR(?, DOUBLE)) AS Score 
        FROM ClinicalGuidelines 
        ORDER BY Score DESC
    """
    
    cursor.execute(sql, [top_k, vector_string])
    results = cursor.fetchall()
    conn.close()
    
    # Format the results into a string for the LLM
    context = ""
    for row in results:
        title, text, score = row
        # THE FIX: Cast the IRIS return value to a float before formatting
        score_val = float(score) 
        context += f"\n--- Source: {title} (Relevance Score: {score_val:.3f}) ---\n{text}\n"
        
    return context

def clinical_decision_support(patient_summary):
    """Feeds the patient summary and the IRIS-retrieved guidelines to Gemini."""
    
    print(f"\n🔍 Searching IRIS Vector DB for guidelines matching patient state...")
    guideline_context = get_relevant_guidelines(patient_summary)
    print(f"📚 Retrieved Guidelines:\n{guideline_context}")
    
    print("🧠 Analyzing context with Gemini...")
    
    system_instruction = """
    You are an expert psychiatric clinical supervisor. Review the patient's clinical summary and consult the provided guidelines.
    
    RULES:
    1. If the current treatment is working, optimal, and without severe side effects, output 'NO_CHANGE'.
    2. If the patient is experiencing unmanaged side effects, or is not responding to an adequate trial, output 'CHANGE_RECOMMENDED'.
    3. Cite the specific provided guideline to justify your pivot.
    
    Respond in strict JSON format: {"status": "...", "rationale": "...", "action": "...", "citations": ["..."]}
    """
    
    prompt = f"PATIENT SUMMARY:\n{patient_summary}\n\nRELEVANT CLINICAL GUIDELINES (From IRIS):\n{guideline_context}"
    
    # New SDK Syntax for generation
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    return json.loads(response.text)

if __name__ == "__main__":
    # Testing Ashleigh's Scenario
    test_patient_state = "Patient is a 19-year-old female with Major Depressive Disorder. She has been on Sertraline 50mg for 12 weeks. Her recent PHQ-9 score is 18 (severe)."
    
    print(f"PATIENT STATE: {test_patient_state}")
    
    result = clinical_decision_support(test_patient_state)
    print("\n================ SYSTEM OUTPUT ================")
    print(json.dumps(result, indent=2))
    print("===============================================")

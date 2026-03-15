import os
import iris
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

# --- 1. CONFIGURATION ---
HOST = "localhost"
PORT = 32782  # Or 1972, depending on how your Docker mapped the port
NAMESPACE = "USER"
USER = "_SYSTEM"
PASSWORD = "ISCDEMO"

PDF_DIRECTORY = "./guidelines"
MODEL_NAME = 'all-MiniLM-L6-v2' 

def setup_database(cursor):
    """Create the table in IRIS with the specialized VECTOR datatype."""
    print("Setting up IRIS table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ClinicalGuidelines (
            DocumentTitle VARCHAR(255),
            ChunkText VARCHAR(5000),
            VectorEmbed VECTOR(DOUBLE, 384)
        )
    """)

def chunk_text(text, chunk_size=1000, overlap=100):
    """Splits a large PDF into overlapping chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def process_and_load_pdfs():
    print("Connecting to InterSystems IRIS...")
    # The official DB-API connection method
    conn = iris.connect(hostname=HOST, port=PORT, namespace=NAMESPACE, username=USER, password=PASSWORD)
    
    try:
        cursor = conn.cursor()
        setup_database(cursor)
        
        print(f"Loading embedding model: {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        
        for filename in os.listdir(PDF_DIRECTORY):
            if filename.endswith(".pdf"):
                print(f"Processing {filename}...")
                filepath = os.path.join(PDF_DIRECTORY, filename)
                
                reader = PdfReader(filepath)
                full_text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text += extracted + " "
                    
                chunks = chunk_text(full_text)
                
                for chunk in chunks:
                    # Generate vector
                    vector_list = model.encode(chunk, normalize_embeddings=True).tolist()
                    vector_string = str(vector_list) 
                    
                    # Insert into the IRIS database
                    cursor.execute(
                        "INSERT INTO ClinicalGuidelines (DocumentTitle, ChunkText, VectorEmbed) VALUES (?, ?, TO_VECTOR(?))",
                        [filename, chunk, vector_string]
                    )
                print(f"✅ Successfully vectorized and loaded {filename}")
        
        conn.commit()
        print("🎉 All guidelines loaded into InterSystems IRIS!")
        
    finally:
        # Always ensure the connection closes safely
        conn.close()

if __name__ == "__main__":
    if not os.path.exists(PDF_DIRECTORY):
        os.makedirs(PDF_DIRECTORY)
        print(f"Created '{PDF_DIRECTORY}' directory. Please drop your PDFs in here and run again.")
    else:
        process_and_load_pdfs()

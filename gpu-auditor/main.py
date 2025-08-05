import os
import json
import glob
from datetime import datetime

# Import Google Cloud Storage client if available
try:
    from google.cloud import storage
except ImportError:
    storage = None

# === CONFIGURATION ===
CONTRACTS_DIR = "/workspace/gpu-auditor/contracts/"
OUTPUT_DIR = "/workspace/gpu-auditor/output/"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.json")

# If using GCS, specify your bucket name here
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")  # Example: "my-gpu-auditor-bucket"
GCS_DESTINATION_BLOB = "results.json"

# === FUNCTIONS ===

def list_contracts():
    """List all .sol contracts in the configured directory."""
    return glob.glob(os.path.join(CONTRACTS_DIR, "*.sol"))

def analyze_contract(contract_path):
    """Placeholder analysis for a contract."""
    with open(contract_path, "r", encoding="utf-8") as f:
        code = f.read()
    # For now, generate only a dummy analysis
    return {
        "contract_name": os.path.basename(contract_path),
        "analysis_time": datetime.utcnow().isoformat() + "Z",
        "findings": [
            {"type": "info", "message": "Placeholder analysis - DeepSeek integration pending"}
        ],
        "code_preview": code[:200]  # first 200 characters
    }

def save_results(results):
    """Save results to a JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[INFO] Results saved to {OUTPUT_FILE}")

def upload_to_gcs(local_path, bucket_name, destination_blob):
    """Upload a file to Google Cloud Storage."""
    if not storage:
        print("[WARN] google-cloud-storage is not installed. Skipping GCS upload.")
        return
    if not bucket_name:
        print("[WARN] GCS_BUCKET_NAME is not configured. Skipping GCS upload.")
        return
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(local_path)
    print(f"[INFO] File {local_path} uploaded to gs://{bucket_name}/{destination_blob}")

# === MAIN ===

def main():
    print("[INFO] Starting GPU Auditor - Placeholder Mode")
    contracts = list_contracts()
    
    if not contracts:
        print(f"[ERROR] No contracts found in {CONTRACTS_DIR}")
        return
    
    print(f"[INFO] Contracts found: {len(contracts)}")
    for c in contracts:
        print(f"  - {os.path.basename(c)}")
    
    results = []
    for contract in contracts:
        print(f"[INFO] Analyzing contract: {os.path.basename(contract)}")
        analysis = analyze_contract(contract)
        results.append(analysis)
    
    save_results(results)

    if GCS_BUCKET_NAME:
        upload_to_gcs(OUTPUT_FILE, GCS_BUCKET_NAME, GCS_DESTINATION_BLOB)
    else:
        print("[INFO] GCS upload disabled (GCS_BUCKET_NAME not configured).")

if __name__ == "__main__":
    main()

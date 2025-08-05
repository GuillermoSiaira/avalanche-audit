import subprocess
import os
import json
import glob
from datetime import datetime

try:
    from google.cloud import storage
except ImportError:
    storage = None

# === CONFIGURATION ===
CONTRACTS_DIR = "/workspace/gpu-auditor/contracts/"
OUTPUT_DIR = "/workspace/gpu-auditor/output/"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.json")

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
GCS_DESTINATION_BLOB = "results.json"

# === FUNCTIONS ===

def list_contracts():
    """List all .sol contracts in the configured directory."""
    return glob.glob(os.path.join(CONTRACTS_DIR, "*.sol"))

def analyze_contract(contract_path):
    """Analyze a smart contract using DeepSeek via Ollama in RunPod."""
    with open(contract_path, "r", encoding="utf-8") as f:
        code = f.read()

    print(f"[INFO] Sending {os.path.basename(contract_path)} to DeepSeek model...")
    
    # Run DeepSeek model via Ollama
    result = subprocess.run(
        ["ollama", "run", "deepseek-coder:6.7b", f"Analyze the following Solidity smart contract for vulnerabilities and potential issues:\n\n{code}"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] DeepSeek model failed: {result.stderr}")
        analysis_text = "Error running DeepSeek model"
    else:
        analysis_text = result.stdout.strip()

    return {
        "contract_name": os.path.basename(contract_path),
        "analysis_time": datetime.utcnow().isoformat() + "Z",
        "findings": [{"type": "ai_analysis", "message": analysis_text}]
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
    print("[INFO] Starting GPU Auditor - DeepSeek Mode")
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


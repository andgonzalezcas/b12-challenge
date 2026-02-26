import json
import hmac
import hashlib
import requests
import os
from datetime import datetime, timezone
from typing import Dict

B12_API_URL = os.environ.get("B12_API_URL", "https://url_de_la_api.com")

b12_secret_str = os.environ.get("B12_SECRET", "el_secreto_de_la_api")
B12_SECRET = b12_secret_str.encode('utf-8') # Lo pasamos a bytes

def get_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def build_payload(repo: str, run_id: str) -> Dict[str, str]:
    return {
        "action_run_link": f"https://github.com/{repo}/actions/runs/{run_id}",
        "email": os.environ.get("MY_EMAIL", "email@gmail.com"), 
        "name": os.environ.get("MY_NAME", "User Name"),           
        "repository_link": f"https://github.com/{repo}",
        "resume_link": os.environ.get("MY_RESUME_LINK", "https://www.linkedin.com"),
        "timestamp": get_iso_timestamp()
    }

def generate_hmac_signature(payload_bytes: bytes, secret: bytes) -> str:
    return hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

def submit_to_api(payload: Dict[str, str]) -> None:
    payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    payload_bytes = payload_str.encode('utf-8')
    
    signature = generate_hmac_signature(payload_bytes, B12_SECRET)
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}"
    }

    try:
        response = requests.post(B12_API_URL, data=payload_bytes, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success"):
            print(f"¡Éxito! El receipt es: {data.get('receipt')}")
        else:
            print(f"Error en la API: {data}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error en la request: {e}")

def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "usuario/repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "12345")
    
    payload = build_payload(repo, run_id)
    submit_to_api(payload)

if __name__ == "__main__":
    main()
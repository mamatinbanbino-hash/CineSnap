from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from acrcloud.recognizer import ACRCloudRecognizer
import json
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG = {
    'host': 'identify-eu-west-1.acrcloud.com',
    'access_key': '67388071b2642a01936c84b925f7d249',
    'access_secret': 'JFbYHp01v3zdtLJJANelNSQAX5NXbQ0wFZfbPT4T',
    'timeout': 15
}

@app.post("/api/identify")
async def identify(file: UploadFile = File(...)):
    # Vercel utilise /tmp pour l'écriture de fichiers temporaires
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        re = ACRCloudRecognizer(CONFIG)
        result = re.recognize_by_file(temp_path, 0)
        data = json.loads(result)

        if data.get("status", {}).get("code") == 0:
            metadata = data["metadata"]["music"][0] if "music" in data["metadata"] else data["metadata"]["custom_files"][0]
            return {
                "status": "success",
                "title": metadata.get("title"),
                "year": metadata.get("release_date", "N/A")
            }
        return {"status": "error", "message": "Non reconnu"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

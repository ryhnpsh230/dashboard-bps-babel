from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="BPS Receiver API", version="1.0.0")

# CORS: biar extension & streamlit bisa akses.
# Untuk aman: ganti allow_origins jadi [ "https://<streamlit-app>.streamlit.app" ] dan/atau chrome-extension://<id>
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("/data")  # mount persistent disk di Render ke /data
DATA_DIR.mkdir(parents=True, exist_ok=True)
LATEST = DATA_DIR / "latest.csv"

class IngestPayload(BaseModel):
    csv: str
    source: str | None = None

@app.get("/health")
def health():
    return {"ok": True, "has_latest": LATEST.exists()}

@app.post("/ingest")
def ingest(p: IngestPayload):
    # Simpan CSV apa adanya. UTF-8 BOM biar Excel Indonesia rapi.
    LATEST.write_text(p.csv, encoding="utf-8-sig")
    return {"ok": True, "saved": "latest.csv", "bytes": len(p.csv), "source": p.source}

@app.get("/latest.csv")
def latest_csv():
    if not LATEST.exists():
        return Response("No data yet. POST /ingest first.", media_type="text/plain", status_code=404)
    return Response(LATEST.read_text(encoding="utf-8-sig"), media_type="text/csv; charset=utf-8")

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.detectron_predictor import DetectronPredictor


logging.basicConfig(
    level=logging.INFO,
    filename="server.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

predictor = DetectronPredictor()

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API ROUTE ----------
def parse_float(text):
    try:
        return float(text)
    except:
        return 1.0


@app.post("/upload")
async def create_upload_file(request: Request):
    request = await request.form()
    image = request["image_file"]
    brigntness = parse_float(request["brightness"])
    contrast = parse_float(request["contrast"])
    scale = parse_float(request.get("scale", 1))
    unit = request.get("unit", "nm")  # <-- FIX: don't parse unit as float

    logging.info("received mime type %s", image.content_type)

    image_bytes = await image.read()

    results = predictor.work(
        "",
        image_bytes,
        {"brightness": brigntness, "contrast": contrast, "scale": scale, "unit": unit},
    )
    return ORJSONResponse(results)


# ---------- SERVE FRONTEND ----------
FRONTEND_DIR = "frontend_dist"

if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

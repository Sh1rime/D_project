from fastapi import FastAPI, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests, io, json, base64, zipfile, uuid, os, tempfile, aiofiles

PDF_CONVERTER_URL = "http://pdf_converter:9000/convert"
OCR_SERVICE_URL   = "http://ocr_service:9100/ocr"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ——————————————————— UI ——————————————————— #
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# —————————————————— API ——————————————————— #
@app.post("/analyze")
async def analyze(pdf: UploadFile):
    # 1) pdf → pages
    r = requests.post(PDF_CONVERTER_URL, files={"pdf": (pdf.filename, await pdf.read(), pdf.content_type)})
    if r.status_code != 200:
        return JSONResponse({"detail": "convert error"}, status_code=500)

    pdf_json = r.json()
    result_pages = []

    # 2) OCR каждую страницу
    for p in pdf_json["pages"]:
        r_ocr = requests.post(OCR_SERVICE_URL, json=p, timeout=120)
        if r_ocr.status_code != 200:
            return JSONResponse({"detail": "OCR error"}, status_code=500)
        result_pages.append(r_ocr.json())

    full = {"file_name": pdf.filename, "pages": result_pages}

    # 3) сохранить во временный файл и отдать ссылку
    tmpdir = tempfile.mkdtemp()
    out_path = os.path.join(tmpdir, pdf.filename + ".json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)

    return FileResponse(out_path, filename=pdf.filename + ".json", media_type="application/json")

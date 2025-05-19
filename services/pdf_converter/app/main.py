from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import fitz               # PyMuPDF
import base64, io, uuid, json

app = FastAPI(title="PDF → PNG converter")

@app.post("/convert")
async def convert(pdf: UploadFile):
    if not pdf.filename.lower().endswith(".pdf"):
        return JSONResponse({"detail": "Not a PDF"}, status_code=400)

    data = await pdf.read()
    doc  = fitz.open(stream=data, filetype="pdf")

    pages_json = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)                 # 300 dpi
        img_bytes = pix.tobytes("png")
        pages_json.append({
            "page_index": page.number,
            "width":  pix.width,
            "height": pix.height,
            "image_b64": base64.b64encode(img_bytes).decode()
        })

    return {"pages": pages_json, "source_file": pdf.filename}

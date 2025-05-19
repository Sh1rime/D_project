from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import pytesseract, cv2, numpy as np, base64, io, json, uuid
from PIL import Image

lang = "rus+eng"
pytesseract.pytesseract.tesseract_cmd = "tesseract"   # внутри контейнера в $PATH

app = FastAPI(title="OCR service (rus+eng)")

def detect_tables(img):
    """Грубо ищем таблицы через морфологию + контуры"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr  = cv2.adaptiveThreshold(~gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY,15,-2)

    # горизонтали
    hori = thr.copy()
    hsize = int(img.shape[1] / 20)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(hsize,1))
    hori = cv2.erode(hori,kernel)
    hori = cv2.dilate(hori,kernel)

    # вертикали
    vert = thr.copy()
    vsize = int(img.shape[0] / 20)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,vsize))
    vert = cv2.erode(vert,kernel)
    vert = cv2.dilate(vert,kernel)

    mask = cv2.add(hori, vert)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    tables = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w*h > 10_000:   # отсечь мусор
            tables.append({"x":x,"y":y,"w":w,"h":h})
    return tables

def ocr_page(img_b64):
    raw = base64.b64decode(img_b64)
    img = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

    # pytesseract таблица данных
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

    words = []
    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        if not txt: continue
        words.append({
            "text"      : txt,
            "conf"      : float(data["conf"][i]),
            "bbox"      : [int(data[k][i]) for k in ("left","top","width","height")],
            "font_size" : None,            # Tesseract 5 это не возвращает
            "angle"     : 0                # ориентация одного слова обычно 0
        })

    # общая ориентация страницы
    osd   = pytesseract.image_to_osd(img, lang=lang, output_type=pytesseract.Output.DICT)
    angle = int(osd.get("rotate", 0))

    # таблицы
    tables = detect_tables(img)

    return {"angle": angle, "words": words, "tables": tables}

@app.post("/ocr")
async def ocr_page_endpoint(payload: dict):
    try:
        page_json = ocr_page(payload["image_b64"])
        page_json["page_index"] = payload["page_index"]
        page_json["width"]      = payload["width"]
        page_json["height"]     = payload["height"]
        return page_json
    except Exception as e:
        return JSONResponse({"detail": "OCR error"}, status_code=400)

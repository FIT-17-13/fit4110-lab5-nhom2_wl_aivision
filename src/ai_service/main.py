import logging
import base64
import numpy as np
import cv2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ultralytics import YOLO

app = FastAPI(title="AI Inference Worker", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logging.info("Đang tải model YOLOv8n...")
model = YOLO('yolov8n.pt')

class PredictRequest(BaseModel):
    image_data: str
    is_url: bool

@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}

@app.post("/predict", status_code=200)
async def predict(request: PredictRequest):
    try:
        # YOLOv8 hỗ trợ đọc trực tiếp từ URL, nếu là base64 thì cần decode
        if request.is_url:
            source = request.image_data
        else:
            img_data = base64.b64decode(request.image_data)
            np_arr = np.frombuffer(img_data, np.uint8)
            source = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Chạy inference
        results = model(source)
        
        detections = []
        has_person = False

        # Bóc tách kết quả bounding box từ YOLO
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = float(box.conf[0])
                
                # Tọa độ [x_center, y_center, width, height] -> chuyển về chuẩn
                x_c, y_c, w, h = box.xywh[0].tolist()
                
                if label == "person":
                    has_person = True

                detections.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": {
                        "x": int(x_c - w/2),
                        "y": int(y_c - h/2),
                        "width": int(w),
                        "height": int(h)
                    }
                })

        # Logic đánh giá mức độ rủi ro dựa trên object nhận được
        risk_level = "warning" if has_person else "low"

        return {
            "detections": detections,
            "unknown_person": has_person, # Giả lập logic nhận diện người lạ
            "risk_level": risk_level
        }
        
    except Exception as e:
        logging.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi khi chạy Model YOLO")
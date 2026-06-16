import os
import httpx
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI(title="AI Vision API Gateway", version="1.0.0")
logging.basicConfig(level=logging.INFO)

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:9000")

# --- SCHEMA NHẬN TỪ NHÓM CAMERA (Chuẩn mục 7 và 6.7) ---
class DetectRequest(BaseModel):
    request_id: str
    camera_id: str
    timestamp: str
    location: Optional[str] = None
    motion_score: Optional[float] = None
    snapshot_url: Optional[str] = None
    image_base64: Optional[str] = None

# --- XỬ LÝ LỖI (Giữ nguyên cấu trúc 422) ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Sai định dạng dữ liệu từ Camera"})

@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "service": "AI Vision API Gateway"}

# --- ENDPOINT CHÍNH CHỜ NHÓM CAMERA GỌI ---
@app.post("/api/v1/detect", status_code=200)
@app.post("/detect", status_code=200) # Hỗ trợ cả URL cũ cho test
async def detect_objects(request: DetectRequest):
    # Ưu tiên dùng url, nếu không có thì dùng base64
    image_source = request.snapshot_url or request.image_base64
    if not image_source:
        raise HTTPException(status_code=422, detail="Phải có snapshot_url hoặc image_base64")

    ai_payload = {
        "image_data": image_source,
        "is_url": bool(request.snapshot_url)
    }

    try:
        # Gửi ảnh sang container AI nội bộ để chạy YOLO
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AI_SERVICE_URL}/predict", json=ai_payload, timeout=20.0)
            response.raise_for_status()
            ai_result = response.json()
            
    except Exception as e:
        logging.error(f"Lỗi AI Service: {e}")
        raise HTTPException(status_code=500, detail="AI Service không phản hồi")

    # Format trả về ĐÚNG CHUẨN MỤC 7 CHO NHÓM CAMERA
    return {
        "request_id": request.request_id,
        "camera_id": request.camera_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detections": ai_result.get("detections", []),
        "unknown_person": ai_result.get("unknown_person", True),
        "risk_level": ai_result.get("risk_level", "warning")
    }
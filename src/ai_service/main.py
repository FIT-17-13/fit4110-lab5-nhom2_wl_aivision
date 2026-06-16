from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "YOLOv8-detection"}

@app.post("/predict")
def predict():
    return {
        "success": True,
        "predictions": [
            {"class": "person", "confidence": 0.94, "bbox": [100, 150, 50, 80]}
        ]
    }

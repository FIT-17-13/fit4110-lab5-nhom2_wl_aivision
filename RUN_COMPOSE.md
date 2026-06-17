# Hướng dẫn Khởi chạy AI Vision Service (Lab 05)

Hệ thống AI Vision được thiết kế theo kiến trúc Microservices, bao gồm 3 container:
1. **API Gateway (FastAPI):** Tiếp nhận request từ các service khác.
2. **AI Worker (YOLOv8):** Chuyên xử lý hình ảnh bất đồng bộ.
3. **Database (PostgreSQL):** Lưu trữ metadata và kết quả nhận diện.

## 1. Yêu cầu hệ thống
- Đã cài đặt Docker Desktop và Docker Compose (v2).
- Khuyến nghị cấp cho Docker tối thiểu 4GB RAM.

## 2. Cách khởi chạy
Mở terminal tại thư mục gốc của dự án và chạy lệnh:
```bash
docker compose up -d
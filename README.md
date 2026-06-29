# Hệ thống Quản lý Kho Nhà máy (Factory WMS)

## Yêu cầu hệ thống
- Docker Desktop
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (via Docker)
- Redis 7 (via Docker)

## Khởi chạy nhanh

```bash
# 1. Copy file env
copy .env.example .env

# 2. Khởi chạy database & services
docker-compose up -d postgres redis

# 3. Chạy backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed  # Tạo dữ liệu demo
uvicorn app.main:app --reload --port 8000

# 4. Chạy frontend
cd frontend
npm install
npm run dev
```

## Truy cập
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Tài khoản demo
| Username | Password | Vai trò |
|:---|:---|:---|
| admin | admin123 | Admin |
| warehouse | wh123 | Warehouse |
| production | prod123 | Production |

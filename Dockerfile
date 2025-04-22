# Sử dụng image Python chính thức làm base
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements trước để tận dụng cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ project
COPY . .

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED 1

# Port mà ứng dụng Django sẽ chạy
EXPOSE 8000

# Lệnh chạy ứng dụng
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

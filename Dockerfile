# =========================
# Stage 1: Build Frontend
# =========================
FROM node:20 AS frontend-build

WORKDIR /frontend

COPY zno-explorer-frontend/package*.json ./
RUN npm install

COPY zno-explorer-frontend/ .
RUN npm run build


# =========================
# Stage 2: Backend
# =========================
FROM python:3.10

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

# Install torch CPU
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install detectron2 FROM SOURCE
RUN git clone https://github.com/facebookresearch/detectron2.git
RUN pip install --no-build-isolation ./detectron2

# Install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY zno-explorer-backend/backend ./backend

# Create models folder
RUN mkdir -p models

# Install gdown
RUN pip install gdown

# Download model
RUN gdown --id 1ibaw1mS06JFzUUZRmvlm8K8Oxzd0XBVK \
    -O models/detectron.pth

# Copy frontend build
COPY --from=frontend-build /frontend/dist ./frontend_dist

EXPOSE 10000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]

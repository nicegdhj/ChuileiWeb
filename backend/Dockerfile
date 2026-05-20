# syntax=docker/dockerfile:1
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
ARG PIP_INDEX_URL
RUN pip config set global.index-url "$PIP_INDEX_URL"
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
RUN mkdir -p /data/db /data/uploads
ENV DB_URL=sqlite:////data/db/chatbox.sqlite \
    UPLOAD_DIR=/data/uploads
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

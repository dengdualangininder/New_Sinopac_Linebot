# 使用 Python 3.9 的官方映像檔
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製專案檔案到容器中
COPY . .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數 (從 .env 中讀取)
ARG YOUR_CHANNEL_ACCESS_TOKEN
ARG YOUR_CHANNEL_SECRET
ARG Gemini_API

ENV YOUR_CHANNEL_ACCESS_TOKEN=$YOUR_CHANNEL_ACCESS_TOKEN
ENV YOUR_CHANNEL_SECRET=$YOUR_CHANNEL_SECRET
ENV Gemini_API=$Gemini_API

# 執行 Flask 應用程式
CMD ["python", "mainapp.py"]

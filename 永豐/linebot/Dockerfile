# 使用官方 Python 基礎映像
FROM python:3.9-slim

# 設定工作目錄為 /app
WORKDIR /app

# 複製當前目錄的所有文件到容器的工作目錄中
COPY . /app

# 安裝所需的 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器內部的 5001 埠
EXPOSE 5001

# 執行 mainapp2.py
CMD ["python", "mainapp2.py"]

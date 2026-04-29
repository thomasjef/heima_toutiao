# ---- 阶段一：构建器 (Builder) ----
# 使用 Python 官方精简镜像作为构建环境
FROM python:3.13-slim AS builder

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install  --no-cache-dir -r requirements.txt

# 复制所有源代码
COPY . .

# 暴露服务端口
EXPOSE 8080

# 启动命令，这里以 Gunicorn + Uvicorn Worker 为例
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
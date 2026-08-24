# ==================== 第一阶段：依赖安装 ====================
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装系统依赖（aiomysql 需要编译依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==================== 第二阶段：运行镜像 ====================
FROM python:3.12-slim

WORKDIR /app

# 复制第一阶段安装的 Python 包
COPY --from=builder /root/.local /root/.local

# 确保本地 bin 在 PATH 中
ENV PATH=/root/.local/bin:$PATH

# 复制项目代码
COPY . .

# 创建上传目录
RUN mkdir -p backend/uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
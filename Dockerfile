FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest

# 复制项目代码
COPY . .

# 运行测试验证
RUN pytest tests/ -v --tb=short

CMD ["python", "main.py", "--help"]

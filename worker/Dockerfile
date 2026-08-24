# ---- build: instala as dependências Python num prefixo isolado ----
FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime: só o interpretador + o que foi instalado, sem resíduo do pip ----
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /install /usr/local
COPY . .

CMD ["python", "main.py"]

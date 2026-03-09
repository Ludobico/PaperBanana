FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 설치
COPY pyproject.toml ./
RUN uv sync --no-dev

# 소스 복사
COPY . .
RUN mkdir -p data/PaperBananaBench/diagram data/PaperBananaBench/plot && chmod -R 777 data

EXPOSE 8080
CMD ["/bin/bash", "entrypoint.sh"]

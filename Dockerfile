FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY README-docker.md /app/README.md
COPY app /app/app
COPY database /app/database
COPY scanner /app/scanner
COPY data /app/data
COPY tests /app/tests
COPY scripts /app/scripts
COPY Caddyfile /app/Caddyfile
COPY CODE_OF_CONDUCT.md /app/CODE_OF_CONDUCT.md
COPY CONTRIBUTING.md /app/CONTRIBUTING.md
COPY LICENSE /app/LICENSE
COPY SECURITY.md /app/SECURITY.md
COPY scanner.db /app/scanner.db

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir fastapi uvicorn sqlalchemy python-dotenv passlib[bcrypt] itsdangerous jinja2 requests python-multipart fido2 pydantic pydantic-settings

COPY . /app

RUN mkdir -p /app/data /app/app/templates /app/scanner_data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

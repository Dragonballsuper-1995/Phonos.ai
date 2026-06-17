# Multi-stage build for FastAPI
FROM python:3.11-slim as requirements-stage

WORKDIR /tmp
RUN pip install poetry
# Here we'd normally use poetry, but for this setup we'll just use pip
COPY ./requirements.txt /tmp/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=requirements-stage /tmp/wheels /wheels
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache /wheels/*

COPY ./app /app/app
COPY ./alembic.ini /app/
COPY ./data /app/data
# Uncomment when migrations are ready
# COPY ./migrations /app/migrations

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

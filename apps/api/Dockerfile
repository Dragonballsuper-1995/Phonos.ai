FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app
COPY ./alembic.ini /app/

# Copy the embedded SQLite database
COPY ./data /app/data

# Hugging Face Spaces uses port 7860 by default.
# Render and local dev use 8000. The PORT env var controls this.
EXPOSE 7860

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}

#FROM python:3.12.8-bookworm
# WORKDIR /app
# COPY . .
# RUN
# CMD uvicorn src.fast_app.main:app --host 0.0.0.0 --port 8000

FROM python:3.12.8

# Prevent buffering so logs show immediately
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /streamlit

# Copy requirement file
COPY ./pyproject.toml  ./pyproject.toml
COPY ./poetry.lock  ./poetry.lock

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install Python dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy whole project
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit config (optional, fixes some issues)
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the app
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

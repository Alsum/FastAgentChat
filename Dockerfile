# Use a slim Python image for a smaller footprint
FROM python:3.8-slim-buster as builder

# Set the working directory
WORKDIR /app

# Prevent Python from writing .pyc files and from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install build-time dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Final runtime stage
FROM python:3.8-slim-buster

# Create a non-privileged user to run the app
RUN addgroup --system app && adduser --system --group app

# Set the working directory
WORKDIR /app

# Copy the wheels from the builder and install them
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the necessary project files
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Ensure the media directory exists and is writable by the app user
RUN mkdir -p media && chown -R app:app media

# Switch to the non-privileged user and expose the port
USER app
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

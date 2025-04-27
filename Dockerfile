# syntax=docker/dockerfile:1
FROM python:3.9-slim-buster AS base

WORKDIR /app

FROM base AS builder

# Copy requirements.txt first for better cache usage
COPY --link requirements.txt ./

# Create virtual environment and install dependencies using pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install -r requirements.txt

# Copy application code
COPY --link . .

FROM base AS final

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy app code and venv from builder
COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv

# Set environment to use virtualenv
ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Set permissions
RUN chown -R appuser:appgroup /app
USER appuser

# Expose Flask default port
EXPOSE 5000

# Set default command to run the app
CMD ["flask", "run", "--host", "0.0.0.0"]



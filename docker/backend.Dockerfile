# Backend image shared by the API and worker services (same code, different commands).
# Base image is pinned to a minor version; record the resolved digest with
# `docker image inspect` when benchmarking (see README).
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv/nexacart

# Runtime dependencies are exact-pinned in pyproject.toml; dev/test extras are not installed.
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install .

RUN useradd --system --no-create-home --uid 10001 nexacart
USER nexacart

EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

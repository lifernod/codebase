FROM python:3.12-slim
LABEL authors="feni"

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 CMD curl -fsS http://127.0.0.1:8501 || exit 1

ARG UID=1000

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN useradd -rms /bin/bash -u $UID user

WORKDIR /app

RUN chmod 755 /app

COPY --chown=user:user requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

USER user

CMD ["streamlit", "run", "app.py"]
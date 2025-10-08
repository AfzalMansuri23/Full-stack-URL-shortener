# --- Build Stage ---

FROM python:3.9-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# --- Final Stage -----
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY ./app .

ENV PATH=/root/.local/bin:$PATH


EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
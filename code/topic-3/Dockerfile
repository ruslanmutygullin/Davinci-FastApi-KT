FROM python:3.14-slim

WORKDIR /code

# Install dependencies first so this layer is cached when only source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the application code.
COPY ./app ./app

EXPOSE 8000
# 0.0.0.0 so the port is reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

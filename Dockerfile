FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
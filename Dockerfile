FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for Docker cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data during build (faster startup)
RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True)"

# Copy application code
COPY . .

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

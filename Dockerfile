# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set system environment variables to optimize Python within Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the work directory inside the container
WORKDIR /workspace

# Install system dependencies needed for compiling certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker layer caching efficiencies
COPY requirements.txt .

# Install pip packages cleanly without storing cache files
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application codebase to the workspace directory
COPY . .

# Expose ports for both the FastAPI Backend (8000) and Streamlit Frontend (8501)
EXPOSE 8000
EXPOSE 8501

# Create a shell script wrapper to boot both services inside a single container instance cleanly
RUN echo '#!/bin/bash\n\
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &\n\
streamlit run app/ui.py --server.port 8501 --server.address 0.0.0.0\n\
' > /workspace/start.sh && chmod +x /workspace/start.sh

# Set the entrypoint script
CMD ["/workspace/start.sh"]

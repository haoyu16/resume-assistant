FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install LaTeX and other dependencies
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=${PYTHONPATH}:/app/src

# Command to run the application
CMD ["streamlit", "run", "src/app.py"] 
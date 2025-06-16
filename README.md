# Resume Assistant

Resume Assistant is an AI-powered tool that helps you create professional LaTeX/PDF resumes. It provides intelligent suggestions and optimizations while you maintain full control over your content. The app features an intuitive interface for inputting your experience, education, certifications, and other details, with AI guidance to help you present your qualifications more effectively.

## Features
- Interactive interface for inputting your personal information, skills, work experience, projects, education, and publications
- AI-powered suggestions to help improve your content and presentation
- Optional job description analysis to help tailor your resume to specific positions
- Real-time feedback on your resume content
- LaTeX resume generation with PDF preview
- Built-in LaTeX editor for fine-tuning

## Prerequisites
- Python 3.8 or higher
- LaTeX installation (TeX Live or MiKTeX)
- OpenAI API key

## Setup

### Option 1: Local Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your OpenAI API key and PYTHONPATH:
   ```
   OPENAI_API_KEY=your_api_key_here
   PYTHONPATH=${PYTHONPATH}:${PWD}/src
   ```
4. Source the environment variables (make sure you're in the project root directory):
   ```bash
   source .env
   ```
5. Run the application (from the project root directory):
   ```bash
   streamlit run src/app.py
   ```

### Option 2: Docker
1. Clone this repository
2. Make sure you have Docker and Docker Compose installed
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
4. Build and run the Docker container:
   ```bash
   docker-compose up -d
   ```
5. Access the application at http://localhost:8501

To stop the Docker container:
```bash
docker-compose down
```

### Development with Docker
If you want to develop the application while using Docker:

1. Build the image:
   ```bash
   docker build -t resume-assistant .
   ```

2. Run the container with source code mounted as a volume:
   ```bash
   docker run -p 8501:8501 -v $(pwd):/app -e OPENAI_API_KEY=your_api_key_here resume-assistant
   ```

Note: Always run the application from the project root directory to ensure proper module imports.

## Usage
1. Fill in your personal information, skills, work experience, education, certifications, and other details.
2. Optionally paste the job description for the position you're targeting.
3. Choose how to generate your resume:
   - **Generate Basic Resume (No LLM Feedback):** Uses your original content only.
   - **Generate Basic Resume (With LLM Feedback):** Adds AI-powered quality check and suggestions.
   - **Generate Optimized Resume (LaTeX):** Optimizes your content for the target job using AI.
4. Download the generated LaTeX and PDF files.
5. (Optional) Edit the LaTeX source if further customization is needed.

## Output
- Generated LaTeX files are stored in the `output` directory
- PDF previews are automatically generated and opened 

# Resume Writer Assistant

Resume Writer is a Streamlit app for creating professional LaTeX/PDF resumes with sections for experience, education, certifications, and more. It features an easy-to-use UI, AI-powered content optimization, and supports saving/loading resume data.

## Features
- Input personal information, skills, work experience, projects, education, and publications
- Optional job description input for resume optimization
- AI-powered content optimization
- LaTeX resume generation with PDF preview
- Built-in LaTeX editor support

## Prerequisites
- Python 3.8 or higher
- LaTeX installation (TeX Live or MiKTeX)
- OpenAI API key

## Setup
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
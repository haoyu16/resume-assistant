# Resume Writer Assistant

An AI-powered resume writer that helps create professional LaTeX resumes optimized for specific job requirements.

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
1. Fill in your personal information, skills, work experience, and other details
2. Optionally paste the job description you're applying for
3. Click "Generate Resume" to create your LaTeX resume
4. Preview the generated PDF
5. Edit the LaTeX source if needed

## Output
- Generated LaTeX files are stored in the `output` directory
- PDF previews are automatically generated and opened 
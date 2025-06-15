import streamlit as st
from dotenv import load_dotenv
import os
import openai
from ui import ResumeUI
from resume_generator import ResumeGenerator
from llm_agents import QualityCheckResult, ModelConfig

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def display_quality_check_results(quality_result: QualityCheckResult):
    """Display quality check results with appropriate styling."""
    if quality_result.is_approved and quality_result.estimated_pages <= 2:
        st.success("✅ Quality check passed!")
    else:
        if not quality_result.is_approved:
            st.warning("⚠️ Quality check identified some issues:")
        if quality_result.estimated_pages > 2:
            st.error(f"📄 Resume is too long (estimated {quality_result.estimated_pages} pages)")
    
    # Display feedback
    st.write("Feedback:")
    st.write(quality_result.feedback)
    
    # Display suggested changes if any
    if quality_result.suggested_changes:
        st.write("Suggested improvements:")
        for change in quality_result.suggested_changes:
            st.write(f"• {change}")

def main():
    st.title("Resume Writer Assistant")
    
    # Check for OpenAI API key
    if not openai.api_key:
        st.error("Please set your OpenAI API key in the .env file")
        return
    
    # Initialize UI and Resume Generator with configurable models
    ui = ResumeUI()
    
    # Configure models with different parameters
    polisher_config = ModelConfig(temperature=0.8)  # More creative for polishing
    critic_config = ModelConfig(temperature=0.3)    # More consistent for criticism
    quality_checker_config = ModelConfig(temperature=0.2)  # Very consistent for quality checks
    
    generator = ResumeGenerator(
        polisher_config=polisher_config,
        critic_config=critic_config,
        quality_checker_config=quality_checker_config
    )
    
    # Try to load last used resume first
    saved_data = ui.load_last_used_resume()
    # If user loads a different resume, it will override saved_data
    user_selected_data = ui.load_saved_form()
    if user_selected_data:
        saved_data = user_selected_data
    
    # Collect all resume data
    personal_info = ui.collect_personal_info(saved_data)
    summary = ui.collect_summary(saved_data)
    skills = ui.collect_skills(saved_data)
    experience = ui.collect_experience(saved_data)
    projects = ui.collect_projects(saved_data)
    education = ui.collect_education(saved_data)
    certifications = ui.collect_certifications(saved_data)
    publications = ui.collect_publications(saved_data)
    target_info = ui.collect_job_description(saved_data)
    
    # Combine all data
    data = {
        **personal_info,
        'summary': summary,
        'skills': skills,
        'experience': experience,
        'projects': projects,
        'education': education,
        'certifications': certifications,
        'publications': publications,
        'target_info': target_info
    }
    
    # Add save options
    ui.save_current_form(data)

    st.markdown("### 📄 Generate Resume (LaTeX & PDF)")
    st.markdown("""
    Choose how to generate your resume:
    - **Basic Resume (No LLM Feedback)**: Generates LaTeX/PDF using your original content only
    - **Basic Resume (With LLM Feedback)**: Generates LaTeX/PDF with LLM-powered quality check and suggestions
    - **Optimized Resume**: Generates LaTeX/PDF with AI-optimized content based on target information
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        generate_basic_no_llm = st.button("Generate Basic Resume (No LLM Feedback)")
    with col2:
        generate_basic_llm = st.button("Generate Basic Resume (With LLM Feedback)")
    with col3:
        generate_optimized = st.button("Generate Optimized Resume (LaTeX)")

    # Always generate both LaTeX and PDF together
    if generate_basic_no_llm or generate_basic_llm or generate_optimized:
        # Validate required fields
        if not ui.validate_required_fields(data):
            ui.show_error("Please fill in all required fields")
            return
        
        with ui.show_spinner("Generating LaTeX and PDF..."):
            try:
                optimize_content = generate_optimized
                use_llm_feedback = generate_basic_llm or generate_optimized
                latex_content, quality_result = generator.generate_latex(
                    data,
                    target_info if optimize_content else None,
                    optimize_content=use_llm_feedback
                )

                import os
                from datetime import datetime
                os.makedirs('output', exist_ok=True)
                # Use current resume name plus timestamp for folder name
                resume_name = st.session_state.get('current_resume_name')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                if resume_name:
                    safe_filename = "".join(c for c in resume_name if c.isalnum() or c in ('-', '_')).strip()
                    folder_name = f"{safe_filename}_{timestamp}" if safe_filename else f"resume_{timestamp}"
                    file_base = safe_filename if safe_filename else f"resume"
                else:
                    folder_name = f"resume_{timestamp}"
                    file_base = "resume"
                output_folder = os.path.join('output', folder_name)
                os.makedirs(output_folder, exist_ok=True)
                base_filename = os.path.join(output_folder, file_base)
                tex_file = f"{base_filename}.tex"
                with open(tex_file, 'w') as f:
                    f.write(latex_content)

                # Try to compile LaTeX to PDF and catch errors
                try:
                    compilation_result = generator.save_and_compile(latex_content, base_filename)
                except Exception as compile_err:
                    st.error(f"Error during PDF compilation: {compile_err}")
                    return

                st.success("Resume generated!")
                with open(tex_file, "rb") as f:
                    st.download_button(
                        label="Download LaTeX (.tex) file",
                        data=f,
                        file_name=os.path.basename(tex_file),
                        mime="application/x-tex"
                    )
                if compilation_result.success and compilation_result.pdf_path and os.path.exists(compilation_result.pdf_path):
                    with open(compilation_result.pdf_path, "rb") as f:
                        st.download_button(
                            label="Download PDF file",
                            data=f,
                            file_name=os.path.basename(compilation_result.pdf_path),
                            mime="application/pdf"
                        )
                else:
                    st.error(f"Error generating PDF: {compilation_result.error_message}")

                if use_llm_feedback:
                    display_quality_check_results(quality_result)

            except Exception as e:
                st.error(f"Error generating resume: {e}")

if __name__ == "__main__":
    main() 
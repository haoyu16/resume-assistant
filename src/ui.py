import streamlit as st
import webbrowser
from typing import Dict, List, Optional
import os
import json
from pathlib import Path
import datetime

class ResumeUI:
    def __init__(self):
        """Initialize ResumeUI with forms directory."""
        self.forms_dir = Path("resume_json")
        self.forms_dir.mkdir(exist_ok=True)
        
        # Initialize session state variables if they don't exist
        if 'current_resume_name' not in st.session_state:
            st.session_state.current_resume_name = None
        if 'is_new_resume' not in st.session_state:
            st.session_state.is_new_resume = True
        
    def format_phone_number(self, phone: str) -> str:
        """Format phone number as xxx-xxx-xxxx."""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Format as xxx-xxx-xxxx if we have enough digits
        if len(digits) >= 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"
        return phone
        
    def on_phone_change(self):
        """Callback for phone number input changes."""
        if 'phone' in st.session_state:
            digits = ''.join(filter(str.isdigit, st.session_state.phone))
            if len(digits) == 10:
                st.session_state.phone = self.format_phone_number(st.session_state.phone)
                st.session_state.phone_error = ''
            else:
                st.session_state.phone_error = 'Phone number must be exactly 10 digits.'
        
    def load_saved_form(self) -> Optional[Dict]:
        """Load a previously saved form."""
        st.sidebar.header("📂 Resume Management")
        
        # Add refresh button
        if st.sidebar.button("🔄 Refresh Resume List"):
            st.rerun()
            
        saved_forms = [f.stem for f in self.forms_dir.glob("*.json")]
        
        if not saved_forms:
            st.sidebar.info("No saved resumes found in resume_json folder")
            return None
            
        st.sidebar.subheader("Load Resume")
        selected_form = st.sidebar.selectbox(
            "Choose a resume to load",
            [""] + sorted(saved_forms),
            format_func=lambda x: "Select a resume..." if x == "" else x
        )
        
        if selected_form:
            try:
                with open(self.forms_dir / f"{selected_form}.json", 'r') as f:
                    data = json.load(f)
                st.session_state.current_resume_name = selected_form
                st.session_state.is_new_resume = False
                st.sidebar.success(f"✅ Loaded: {selected_form}")
                return data
            except Exception as e:
                st.sidebar.error(f"Error loading resume: {str(e)}")
        return None
        
    def save_current_form(self, data: Dict):
        """Save the current form data."""
        st.sidebar.subheader("💾 Save Resume")
        
        # Display current resume name if it exists
        if st.session_state.current_resume_name:
            st.sidebar.info(f"Current Resume: {st.session_state.current_resume_name}")
        
        # Save button - uses current name or prompts for new name
        if st.sidebar.button("Save"):
            if not st.session_state.current_resume_name:
                filename = st.sidebar.text_input(
                    "Enter a name for this resume",
                    help="Your resume will be saved as 'name.json' in the resume_json folder"
                )
                if not filename:
                    st.sidebar.warning("Please enter a name for the resume")
                    return
                st.session_state.current_resume_name = filename
                st.session_state.is_new_resume = False
            self._save_resume(data, st.session_state.current_resume_name)
        
        # Save As functionality using a form
        if 'save_as_name' not in st.session_state:
            st.session_state.save_as_name = ''
        with st.sidebar.form("save_as_form"):
            st.write("Save As")
            filename = st.text_input(
                "Enter a new name for this resume",
                value=st.session_state.save_as_name,
                key="save_as_name",
                help="Your resume will be saved as 'name.json' in the resume_json folder"
            )
            save_as_submitted = st.form_submit_button("Save As")
            
            if save_as_submitted:
                if not filename:
                    st.warning("Please enter a name for the resume")
                else:
                    st.session_state.current_resume_name = filename
                    st.session_state.is_new_resume = False
                    self._save_resume(data, filename)
                    st.session_state.save_as_name = ''  # Clear after save
    
    def _save_resume(self, data: Dict, filename: str):
        """Internal method to save resume data."""
        file_path = self.forms_dir / f"{filename}.json"
        if file_path.exists() and st.session_state.is_new_resume:
            overwrite = st.sidebar.warning(
                f"'{filename}.json' already exists. Click again to overwrite.",
                button="Overwrite"
            )
            if not overwrite:
                return
                
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        st.sidebar.success(f"Resume saved as '{filename}.json'")
        
        # Save last used resume name
        with open(self.forms_dir / "last_used.txt", 'w') as f:
            f.write(filename)

    def load_last_used_resume(self) -> Optional[Dict]:
        """Load the last used resume."""
        last_used_file = self.forms_dir / "last_used.txt"
        if last_used_file.exists():
            try:
                with open(last_used_file, 'r') as f:
                    last_used = f.read().strip()
                if last_used:
                    resume_file = self.forms_dir / f"{last_used}.json"
                    if resume_file.exists():
                        with open(resume_file, 'r') as f:
                            data = json.load(f)
                        st.session_state.current_resume_name = last_used
                        st.session_state.is_new_resume = False
                        return data
            except Exception as e:
                st.error(f"Error loading last used resume: {str(e)}")
        return None
    
    def display_current_resume_name(self):
        """Display the current resume name in the main UI area."""
        if st.session_state.current_resume_name:
            st.info(f"📄 Current Resume: {st.session_state.current_resume_name}")
        else:
            st.info("📄 New Resume (Unsaved)")
    
    def collect_personal_info(self, loaded_data: Optional[Dict] = None) -> Dict[str, str]:
        """
        Collect personal information from the user.
        
        Args:
            loaded_data (Optional[Dict]): Pre-loaded data to fill the form
        """
        # Display current resume name at the top
        self.display_current_resume_name()
        
        st.header("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=loaded_data.get('name', '') if loaded_data else '')
            email = st.text_input("Email", value=loaded_data.get('email', '') if loaded_data else '')
            phone = st.text_input(
                "Phone",
                value=loaded_data.get('phone', '') if loaded_data else '',
                key='phone',
                on_change=self.on_phone_change
            )
            phone_error = st.session_state.get('phone_error', '')
            if phone_error:
                st.error(phone_error)
            # Only save valid phone number
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) == 10:
                phone = self.format_phone_number(phone)
            else:
                phone = ''
        with col2:
            location = st.text_input("Location", value=loaded_data.get('location', '') if loaded_data else '')
            linkedin = st.text_input("LinkedIn Profile URL", value=loaded_data.get('linkedin', '') if loaded_data else '')
            github = st.text_input("GitHub Profile URL (optional)", value=loaded_data.get('github', '') if loaded_data else '')
        portfolio = st.text_input("Portfolio Website (optional)", value=loaded_data.get('portfolio', '') if loaded_data else '')

        # Citizenship status (optional)
        citizenship_options = ['', 'U.S. Citizen', 'Green Card Holder', 'Other (specify below)']
        citizenship_status = st.selectbox(
            "Citizenship/Work Authorization Status (optional)",
            citizenship_options,
            index=citizenship_options.index(loaded_data.get('citizenship_status', '')) if loaded_data and loaded_data.get('citizenship_status', '') in citizenship_options else 0
        )
        custom_citizenship = ''
        if citizenship_status == 'Other (specify below)':
            custom_citizenship = st.text_input("Please specify your status", value=loaded_data.get('custom_citizenship', '') if loaded_data else '')

        return {
            'name': name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'github': github,
            'portfolio': portfolio,
            'citizenship_status': custom_citizenship if citizenship_status == 'Other (specify below)' else citizenship_status,
            'custom_citizenship': custom_citizenship if citizenship_status == 'Other (specify below)' else ''
        }
    
    def collect_summary(self, loaded_data: Optional[Dict] = None) -> str:
        """Collect professional summary."""
        st.header("Professional Summary")
        return st.text_area("Summary", value=loaded_data.get('summary', '') if loaded_data else '')
    
    def collect_skills(self, loaded_data: Optional[Dict] = None) -> str:
        """Collect skills."""
        st.header("Skills")
        st.markdown("""
        Enter your skills in the following format:
        ```
        Category: Skill1, Skill2, Skill3
        Another Category: Skill4, Skill5
        ```
        """)
        return st.text_area("Skills", value=loaded_data.get('skills', '') if loaded_data else '')
    
    def collect_experience(self, loaded_data: Optional[Dict] = None) -> List[Dict[str, str]]:
        """Collect work experience."""
        st.header("Work Experience")
        experiences = []
        loaded_experiences = loaded_data.get('experience', []) if loaded_data else []
        num_experiences = st.number_input("Number of experiences", min_value=0, max_value=10, 
                                        value=len(loaded_experiences) if loaded_experiences else 1)
        
        for i in range(num_experiences):
            st.subheader(f"Experience {i+1}")
            loaded_exp = loaded_experiences[i] if i < len(loaded_experiences) else None
            
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input(f"Company {i+1}", value=loaded_exp.get('company', '') if loaded_exp else '')
                role = st.text_input(f"Role {i+1}", value=loaded_exp.get('role', '') if loaded_exp else '')
            with col2:
                dates = st.text_input(f"Dates {i+1}", value=loaded_exp.get('dates', '') if loaded_exp else '')
                location = st.text_input(f"Location {i+1}", value=loaded_exp.get('location', '') if loaded_exp else '')
            
            # Collect projects for this experience
            st.subheader(f"Projects for Experience {i+1}")
            projects = []
            loaded_projects = loaded_exp.get('projects', []) if loaded_exp else []
            num_projects = st.number_input(f"Number of projects for Experience {i+1}", min_value=0, max_value=5, 
                                         value=len(loaded_projects) if loaded_projects else 0)
            
            for j in range(num_projects):
                st.markdown(f"**Project {j+1}**")
                loaded_proj = loaded_projects[j] if j < len(loaded_projects) else None
                project_title = st.text_input(
                    f"Project Title {j+1}",
                    value=loaded_proj.get('title', '') if loaded_proj else '',
                    key=f"exp{i}_proj{j}_title"
                )
                project_description = st.text_area(
                    f"Project Description {j+1}",
                    value=loaded_proj.get('description', '') if loaded_proj else '',
                    key=f"exp{i}_proj{j}_desc"
                )
                if project_title:
                    projects.append({
                        'title': project_title,
                        'description': project_description
                    })
            
            if company and role:
                experiences.append({
                    'company': company,
                    'role': role,
                    'dates': dates,
                    'location': location,
                    'projects': projects
                })
        
        return experiences
    
    def collect_projects(self, loaded_data: Optional[Dict] = None) -> List[Dict[str, str]]:
        """Collect projects."""
        st.header("Projects (Optional)")
        projects = []
        loaded_projects = loaded_data.get('projects', []) if loaded_data else []
        num_projects = st.number_input(
            "Number of projects",
            min_value=0,
            max_value=10,
            value=len(loaded_projects) if loaded_projects else 0,
            help="Projects are optional. Set to 0 if you don't want to include any projects."
        )
        
        if num_projects > 0:
            for i in range(num_projects):
                st.subheader(f"Project {i+1}")
                loaded_proj = loaded_projects[i] if i < len(loaded_projects) else None
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input(f"Project Name {i+1}", value=loaded_proj.get('name', '') if loaded_proj else '')
                    technologies = st.text_input(f"Technologies Used {i+1}", 
                                              value=loaded_proj.get('technologies', '') if loaded_proj else '')
                with col2:
                    dates = st.text_input(f"Project Dates {i+1}", value=loaded_proj.get('dates', '') if loaded_proj else '')
                description = st.text_area(f"Project Description {i+1} (one point per line)",
                                         value=loaded_proj.get('description', '') if loaded_proj else '')
                
                if name:
                    projects.append({
                        'name': name,
                        'technologies': technologies,
                        'dates': dates,
                        'description': description
                    })
        
        return projects
    
    def collect_education(self, loaded_data: Optional[Dict] = None) -> List[Dict[str, str]]:
        """Collect education information."""
        st.header("Education")
        education = []
        loaded_education = loaded_data.get('education', []) if loaded_data else []
        num_education = st.number_input("Number of education entries", min_value=0, max_value=5,
                                      value=len(loaded_education) if loaded_education else 1)
        
        for i in range(num_education):
            st.subheader(f"Education {i+1}")
            loaded_edu = loaded_education[i] if i < len(loaded_education) else None
            
            col1, col2 = st.columns(2)
            with col1:
                school = st.text_input(f"School {i+1}", value=loaded_edu.get('school', '') if loaded_edu else '')
                degree = st.text_input(f"Degree {i+1}", value=loaded_edu.get('degree', '') if loaded_edu else '')
            with col2:
                dates = st.text_input(f"Education Dates {i+1}", value=loaded_edu.get('dates', '') if loaded_edu else '')
                location = st.text_input(f"School Location {i+1} (optional)", value=loaded_edu.get('location', '') if loaded_edu else '')
            gpa = st.text_input(f"GPA {i+1} (optional)", value=loaded_edu.get('gpa', '') if loaded_edu else '')
            
            if school and degree:
                education.append({
                    'school': school,
                    'degree': degree,
                    'dates': dates,
                    'location': location if location else None,
                    'gpa': gpa if gpa else None
                })
        
        return education
    
    def collect_publications(self, loaded_data: Optional[Dict] = None) -> List[str]:
        """Collect publications."""
        st.header("Publications (Optional)")
        loaded_publications = loaded_data.get('publications', []) if loaded_data else []
        publications = st.text_area("Publications (one per line)", 
                                  value='\n'.join(loaded_publications) if loaded_publications else '').split('\n')
        return [p for p in publications if p.strip()]
    
    def collect_job_description(self, loaded_data: Optional[Dict] = None) -> Optional[str]:
        """Collect target information for content optimization."""
        st.header("Target Information (Optional)")
        st.markdown("""
        This section helps the AI optimize your resume content. You can include:
        - Job description
        - Required qualifications
        - Preferred qualifications
        - Job responsibilities
        - Company/team culture
        - Any other relevant information
        
        The AI will use this information to optimize your:
        - Professional summary
        - Skills
        - Work experience descriptions
        - Project descriptions
        
        This ensures all sections of your resume are tailored to the position.
        """)
        return st.text_area(
            "Enter any information you want the AI to consider when optimizing your resume",
            value=loaded_data.get('target_info', '') if loaded_data else '',
            height=300,
            help="The more relevant information you provide, the better the AI can optimize your resume content."
        )
    
    def collect_certifications(self, loaded_data: Optional[Dict] = None) -> List[Dict[str, str]]:
        """Collect certifications information."""
        st.header("Certifications (Optional)")
        certifications = []
        loaded_certs = loaded_data.get('certifications', []) if loaded_data else []
        num_certs = st.number_input("Number of certifications", min_value=0, max_value=10,
                                    value=len(loaded_certs) if loaded_certs else 0)
        for i in range(num_certs):
            st.subheader(f"Certification {i+1}")
            loaded_cert = loaded_certs[i] if i < len(loaded_certs) else None
            name = st.text_input(f"Certification Name {i+1}", value=loaded_cert.get('name', '') if loaded_cert else '')
            issued = st.text_input(f"Issued Date {i+1}", value=loaded_cert.get('issued', '') if loaded_cert else '')
            expires = st.text_input(f"Expiration Date {i+1} (optional)", value=loaded_cert.get('expires', '') if loaded_cert else '')
            if name:
                certifications.append({
                    'name': name,
                    'issued': issued,
                    'expires': expires
                })
        return certifications
    
    def show_error(self, message: str):
        """Display error message."""
        st.error(message)
    
    def show_success(self, message: str):
        """Display success message."""
        st.success(message)
    
    def show_spinner(self, message: str):
        """Return a spinner context manager."""
        return st.spinner(message)
    
    def show_pdf(self, pdf_file: str):
        """Display and handle PDF download."""
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=pdf_file.split('/')[-1],
            mime="application/pdf"
        )
        webbrowser.open(f"file://{os.path.abspath(pdf_file)}")
    
    def validate_required_fields(self, data: Dict) -> bool:
        """
        Validate required fields are filled.
        
        Returns:
            bool: True if all required fields are filled, False otherwise
        """
        required_fields = ['name', 'email', 'phone', 'location', 'linkedin', 'summary', 'skills', 'experience', 'education']
        return all(data.get(field) for field in required_fields) 
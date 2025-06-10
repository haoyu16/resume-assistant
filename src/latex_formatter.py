from typing import List, Optional, Dict
import re

def escape_latex(text):
    if not isinstance(text, str):
        return text

    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    # Create a regex to find all special characters
    regex_special_chars = {re.escape(k): v for k, v in replacements.items()}
    pattern = re.compile("|".join(regex_special_chars.keys()))
    
    # The replacement function looks up the matched character
    def replacer(match):
        return regex_special_chars[re.escape(match.group(0))]

    return pattern.sub(replacer, text)

def format_skills(skills_text: str) -> str:
    """Formats the skills section, highlighting categories, as a single paragraph."""
    if not skills_text:
        return ""
    
    formatted_parts = []
    for line in skills_text.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':', 1)
            category = escape_latex(parts[0].strip())
            skills = escape_latex(parts[1].strip())
            formatted_parts.append(f"\\textbf{{{category}:}} {skills}")
        elif line:
            formatted_parts.append(escape_latex(line))
    # Join all with \quad for spacing
    return ' \\quad '.join(formatted_parts)

def format_experience(company: str, role: str, dates: str, location: str, projects: List[Dict[str, str]] = None) -> str:
    """
    Format experience section in LaTeX, ensuring projects are correctly nested.
    """
    # Escape all text inputs
    company = escape_latex(company)
    role = escape_latex(role)
    dates = escape_latex(dates)
    location = escape_latex(location)
    
    # Format the projects section
    projects_section = ""
    if projects:
        project_parts = []
        for project in projects:
            title = escape_latex(project.get('title', ''))
            
            # Use \textbf for the project title to align with the company info
            project_str = f"\\vspace{{-2pt}}\n\\hspace{{15pt}}\\textbf{{{title}}}"

            project_description = project.get('description', '')
            if project_description:
                project_bullets = project_description.strip().split('\n')
                
                if any(bullet.strip() for bullet in project_bullets):
                    # Use a new itemize environment with a specific left margin for indentation
                    # topsep controls space before the list, itemsep between items
                    project_str += "\n\\begin{itemize}[leftmargin=15pt, label={$\\ast$}, topsep=0pt, itemsep=0pt]"
                    for bullet in project_bullets:
                        if bullet.strip():
                            project_str += f"\n\\resumeItem{{{escape_latex(bullet.strip())}}}"
                    project_str += "\n\\end{itemize}"
            project_parts.append(project_str)
        projects_section = "\n".join(project_parts)

    # Combine the heading and the projects section inside a single item
    return f"""\\item
    \\begin{{tabular*}}{{\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textbf{{\\large {company}}} & {dates} \\\\
      \\textit{{{role}}} & \\textit{{{location}}}
    \\end{{tabular*}}
    {projects_section}
    """

def format_project(name: str, technologies: str, dates: str, description: str) -> str:
    """
    Format project section in LaTeX.
    
    Args:
        name (str): Project name
        technologies (str): Technologies used
        dates (str): Project dates
        description (str): Project description with bullet points
        
    Returns:
        str: Formatted LaTeX string
    """
    name = escape_latex(name)
    technologies = escape_latex(technologies)
    dates = escape_latex(dates)
    description = escape_latex(description)
    bullets = description.strip().split('\n')
    bullet_points = '\n'.join([f"\\resumeItem{{{escape_latex(bullet.strip())}}}" 
                              for bullet in bullets if bullet.strip()])
    
    return f"""\\resumeSubheading
        {{{name}}}
        {{{dates}}}
        {{{technologies}}}
        {{}}
        \\resumeItemListStart
        {bullet_points}
        \\resumeItemListEnd
    """

def format_education(school: str, degree: str, dates: str, location: Optional[str] = None, gpa: Optional[str] = None) -> str:
    """
    Format education section in LaTeX as a single row: school on the left, degree, location (optional), and date on the right. GPA omitted.
    """
    school = escape_latex(school)
    degree = escape_latex(degree)
    dates = escape_latex(dates)
    location = escape_latex(location) if location else None
    right_col = f"{degree}, {location}, {dates}" if location else f"{degree}, {dates}"
    return f"""\\item
\\begin{{tabular*}}{{\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
  {{{school}}} & {right_col} \\
\\end{{tabular*}}
"""

def format_publications(publications: List[str]) -> str:
    """
    Format publications section in LaTeX.
    
    Args:
        publications (List[str]): List of publications
        
    Returns:
        str: Formatted LaTeX string or empty string if no publications
    """
    if not publications:
        return ""
        
    publications_items = []
    publications_section = "\n\\section{Publications}\n\\begin{enumerate}\n"
    for pub in publications:
        publications_items.append(f"\\item {pub}")
    publications_section += '\n'.join(publications_items)
    publications_section += "\n\\end{enumerate}"
    
    return publications_section

def format_contact_links(github: Optional[str] = None, portfolio: Optional[str] = None, linkedin: Optional[str] = None) -> str:
    """
    Format additional contact links in LaTeX.
    
    Args:
        github (str, optional): GitHub profile URL
        portfolio (str, optional): Portfolio website
        linkedin (str, optional): LinkedIn profile URL
        
    Returns:
        str: Formatted LaTeX string
    """
    additional_links = ""
    if github:
        additional_links += f"$|$ \\faIcon{{github}} \\href{{{github}}}{{GitHub}}"
    if portfolio:
        additional_links += f"$|$ \\faIcon{{globe}} \\href{{{portfolio}}}{{{portfolio}}}"
    if linkedin:
        additional_links += f"$|$ \\faIcon{{linkedin}} \\href{{{linkedin}}}{{LinkedIn}}"
    return additional_links 

def format_certifications(certifications: List[Dict[str, str]]) -> str:
    if not certifications:
        return ""
    cert_lines = []
    for cert in certifications:
        name = escape_latex(cert['name'])
        issued = escape_latex(cert['issued'])
        expires = escape_latex(cert['expires']) if cert.get('expires') else ""
        date_range = f"{issued} - {expires}" if expires else issued
        cert_lines.append(
            f"\\item\n\\begin{{tabular*}}{{\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}\n"
            f"  {{{name}}} & {date_range} \\\\"
            f"\\end{{tabular*}}"
        )
    return "\\section{Certifications}\n\\begin{itemize}[leftmargin=0pt]\n" + "\n".join(cert_lines) + "\n\\end{itemize}" 
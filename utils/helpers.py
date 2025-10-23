import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import List, Dict

# ==========================
# 📄 PDF Generation Helpers
# ==========================

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_pdfs")

# Ensure output directory exists
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render_pdf(template_name: str, context: Dict, output_filename: str) -> str:
    """
    Render a PDF from a Jinja2 HTML template.
    
    Args:
        template_name (str): Name of the template file (e.g., 'report_template.html').
        context (dict): Context variables to pass to the template.
        output_filename (str): Output PDF filename (without path).
    
    Returns:
        str: Path to the generated PDF.
    """
    template = env.get_template(template_name)
    html_content = template.render(context)
    
    output_path = os.path.join(PDF_OUTPUT_DIR, output_filename)
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path


def generate_class_report(class_name: str, students: List[Dict], date: str) -> str:
    """
    Generate a PDF report for a specific class attendance.
    
    Args:
        class_name (str): Name of the class.
        students (List[Dict]): List of students with attendance info.
                               Example: [{"name": "John Doe", "status": "present"}]
        date (str): Date of attendance (YYYY-MM-DD).
    
    Returns:
        str: Path to the generated PDF.
    """
    context = {
        "class_name": class_name,
        "students": students,
        "date": date
    }
    filename = f"{class_name}_{date}.pdf".replace(" ", "_")
    return render_pdf("class_list_template.html", context, filename)


def generate_analytics_report(analytics_data: Dict, report_name: str) -> str:
    """
    Generate a PDF for analytics summary.
    
    Args:
        analytics_data (dict): Analytics metrics (totals, percentages, trends).
        report_name (str): Desired PDF filename (without path).
    
    Returns:
        str: Path to the generated PDF.
    """
    context = {
        "analytics": analytics_data
    }
    filename = f"{report_name}.pdf".replace(" ", "_")
    return render_pdf("report_template.html", context, filename)

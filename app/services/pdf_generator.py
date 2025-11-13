import json
import matplotlib.pyplot as plt
from fpdf import FPDF, HTMLMixin
import os

def create_chart(data):
    if not data or not isinstance(data, dict):
        return
    os.makedirs("outputs", exist_ok=True)
    plt.figure()
    plt.bar(data.keys(), data.values())
    plt.title("Key Metrics Overview")
    plt.tight_layout()
    plt.savefig("outputs/chart.png")
    plt.close()

class EnhancedPDF(FPDF, HTMLMixin):
    def add_section(self, title, content):
        self.set_font("Arial", "B", 14)
        self.cell(200, 10, txt=title, ln=True)
        self.set_font("Arial", size=12)
        if isinstance(content, dict):
            for key, value in content.items():
                self.cell(0, 8, txt=f"{key}: {value}", ln=True)
        else:
            self.multi_cell(0, 8, txt=str(content))
        self.ln(5)

def generate_pdf(report_json: str, output_path: str):
    data = json.loads(report_json)
    os.makedirs("outputs", exist_ok=True)

    pdf = EnhancedPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Business Report", ln=True, align="C")
    pdf.ln(10)

    for section, content in data.items():
        pdf.add_section(section.capitalize(), content)

    if "key_metrics" in data:
        create_chart(data["key_metrics"])
        pdf.image("outputs/chart.png", w=160)

    pdf.output(output_path)
    return output_path

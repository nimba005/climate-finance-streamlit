from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename):
    text = """National Financial Budget – 2024

Total Public Investment in Climate Initiatives: 100,000,000

Percentage of National Budget Allocated to Climate Adaptation: 12%

Year-on-Year Budget Increase for Climate Adaptation: -

Private Sector Investment Mobilized: 30,000,000

Funding Allocation by Sector:
Energy: 25%
Agriculture: 30%
Health: 20%
Transport: 15%
Water: 10%


National Financial Budget – 2025

Total Public Investment in Climate Initiatives: 120,000,000

Percentage of National Budget Allocated to Climate Adaptation: 15%

Year-on-Year Budget Increase for Climate Adaptation: 20%

Private Sector Investment Mobilized: 45,000,000

Funding Allocation by Sector:
Energy: 30%
Agriculture: 25%
Health: 15%
Transport: 20%
Water: 10%
"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 100
    for line in text.split("\n"):
        c.drawString(100, y, line)
        y -= 20
    c.save()

if __name__ == "__main__":
    create_pdf("budget.pdf")
    print("✅ budget.pdf created successfully with 2024 & 2025 data!")

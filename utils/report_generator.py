from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def generate_pdf_report(user_data, total_expense, category_data, suggestions):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Financial Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph(f"User: {user_data.username}", styles['Normal']))
    elements.append(Paragraph(f"Total Spending: ₹{total_expense:,.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Category Table
    elements.append(Paragraph("Category Breakdown", styles['Heading2']))
    data = [["Category", "Amount (INR)"]]
    for cat, amt in category_data.items():
        data.append([cat, f"₹{amt:,.2f}"])
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Suggestions
    elements.append(Paragraph("AI Suggestions", styles['Heading2']))
    for sug in suggestions:
        elements.append(Paragraph(f"• {sug}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

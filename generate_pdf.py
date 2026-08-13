from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from pathlib import Path

base_dir = Path(__file__).resolve().parent
input_path = base_dir / 'final_year_project_documentation.md'
output_path = base_dir / 'Face_Recognition_Attendance_System_Report.pdf'

text = input_path.read_text(encoding='utf-8')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ProjectTitle', fontName='Helvetica-Bold', fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=18, textColor=colors.HexColor('#1f538d')))
styles.add(ParagraphStyle(name='ProjectSubtitle', fontName='Helvetica', fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=20))
styles.add(ParagraphStyle(name='ProjectBody', fontName='Helvetica', fontSize=11, leading=14, alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle(name='ProjectHeading1', fontName='Helvetica-Bold', fontSize=14, leading=18, spaceBefore=12, spaceAfter=8, textColor=colors.HexColor('#2fa572')))
styles.add(ParagraphStyle(name='ProjectHeading2', fontName='Helvetica-Bold', fontSize=12, leading=15, spaceBefore=10, spaceAfter=6))

story = []

for line in text.splitlines():
    if not line.strip():
        story.append(Spacer(1, 6))
        continue
    if line.startswith('# '):
        story.append(Paragraph(line[2:], styles['ProjectTitle']))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:], styles['ProjectHeading1']))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:], styles['ProjectHeading2']))
    elif line.startswith('---'):
        continue
    else:
        story.append(Paragraph(line, styles['ProjectBody']))

# Create PDF
pdf = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
pdf.build(story)
print(f'PDF created: {output_path}')

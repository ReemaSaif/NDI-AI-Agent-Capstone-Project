import os
import sys
from pathlib import Path
from datetime import datetime

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.append(str(CURRENT_DIR))

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)

from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from layouts import fix_arabic, generate_metrics_chart, OESummary

class OEReportBuilder:
    def __init__(self, output_file="OE_Arabic_Report.pdf", logo_path="sdaia_logo.png"):
        self.output_file = output_file
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()
        self.section_style_ar = ParagraphStyle(
            name="SectionStyleAR",
            parent=self.styles["Heading2"],
            fontName="Arabic-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#625D9C"),
            alignment=2,
            spaceAfter=10,
        )

        self.body_ar = ParagraphStyle(
            name="BodyArabic",
            parent=self.styles["BodyText"],
            fontName="Arabic",
            fontSize=13,
            leading=24,
            alignment=2,
        )

        self.italic_ar = ParagraphStyle(
            name="ItalicArabic",
            parent=self.styles["Italic"],
            fontName="Arabic",
            fontSize=10,
            leading=14,
            alignment=2,
        )

    # Cover Page

    def _cover_page(self, canvas, doc, summary: OESummary):
        width, height = A4
        canvas.setFillColor(colors.HexColor("#625D9C"))
        strip_height = height * 0.35
        strip_y = (height - strip_height) / 2
        canvas.rect(0, strip_y, width, strip_height, fill=1, stroke=0)

        # Add Logo

        if os.path.exists(self.logo_path):
            try:
                canvas.drawImage(
                    self.logo_path,
                    (width - 140) / 2,
                    height * 0.74,
                    width=140,
                    height=140,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except:
                pass

        canvas.setFillColor(colors.white)
        canvas.setFont("Arabic-Bold", 24)
        canvas.drawCentredString(width / 2, strip_y + strip_height - 40, fix_arabic("تقرير التميز التشغيلي"))

        canvas.setFont("Arabic", 16)
        canvas.drawCentredString(width / 2, strip_y + strip_height - 80, fix_arabic("المكتب الوطني لإدارة البيانات (NDMO)"))

        canvas.setFont("Arabic", 14)
        canvas.drawCentredString(width / 2, strip_y + strip_height - 130, fix_arabic(summary.entity_name))
        canvas.drawCentredString(width / 2, strip_y + strip_height - 160, fix_arabic(summary.cycle_name))

    # Build PDF

    def build(self, summary: OESummary):
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=30
        )

        elements = []

        elements.append(Spacer(1, A4[1] - 100))
        elements.append(PageBreak())

        elements.append(Paragraph(fix_arabic("الملخص التنفيذي"), self.section_style_ar))
        elements.append(Spacer(1, 20))

        summary_text = f"""
        {fix_arabic(f'الجهة: {summary.entity_name}')}<br/><br/>
        {fix_arabic(f'الدورة: {summary.cycle_name}')}<br/><br/>
        {fix_arabic(f'النتيجة النهائية: {summary.final_score:.2f}')}<br/><br/>
        {fix_arabic(f'مستوى النضج: {summary.maturity_level} ({summary.maturity_label})')}<br/><br/>
        {fix_arabic(f'وصف مستوى النضج: {summary.maturity_description}')}<br/><br/>
        {fix_arabic(f'تاريخ التقييم: {datetime.now().strftime("%Y-%m-%d")}')}
        """

        elements.append(Paragraph(summary_text, self.body_ar))
        elements.append(Spacer(1, 25))
        elements.append(HRFlowable(width="100%"))
        elements.append(Spacer(1, 25))

        elements.append(Paragraph(fix_arabic("تفصيل المؤشرات"), self.section_style_ar))
        elements.append(Spacer(1, 20))

        table_data = [[
            fix_arabic("النتيجة الموزونة"),
            fix_arabic("الوزن"),
            fix_arabic("المقياس"),
            fix_arabic("النسبة المئوية"),
            fix_arabic("المؤشر"),
        ]]

        for m in summary.metrics:
            table_data.append([
                f"{m.weighted_score:.2f}",
                str(m.weight),
                fix_arabic(str(m.scale)),
                f"{m.percentage:.1f}%",
                fix_arabic(m.metric_id),
            ])

        table = Table(table_data, colWidths=[100, 80, 90, 100, 120])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#625D9C")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Arabic-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTNAME", (0, 1), (-1, -1), "Arabic"),
            ("ALIGN", (0, 1), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ]))

        elements.append(table)
        elements.append(PageBreak())

        elements.append(Paragraph(fix_arabic("مخطط المؤشرات"), self.section_style_ar))
        elements.append(Spacer(1, 20))

        generate_metrics_chart(summary.metrics)
        elements.append(Image("metrics_chart.png", width=400, height=220))

        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%"))
        elements.append(Spacer(1, 10))

        footer_text = fix_arabic(f"تم إنشاء هذا التقرير آلياً بتاريخ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        elements.append(Paragraph(footer_text, self.italic_ar))

        doc.build(elements, onFirstPage=lambda c, d: self._cover_page(c, d, summary))

        print(f"PDF generated successfully: {self.output_file}")

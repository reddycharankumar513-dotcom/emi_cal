"""
Export Engine for Excel (.xlsx) and PDF (.pdf) Reports.
Generates polished banking-grade financial schedules and scenario comparison documents.
"""

import io
from typing import Optional, Dict, Any
import pandas as pd
import datetime

# OpenPyXL imports
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .formatting import format_currency, format_percentage, format_tenure, format_date_standard


# --- OpenPyXL Excel Helpers ---

NAVY_HEADER_FILL = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
SUBHEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ACCENT_GREEN_FILL = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
LIGHT_ZEBRA_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1"),
)


def generate_excel_amortization(
    schedule_df: pd.DataFrame,
    loan_summary: Any = None,
    sheet_title: str = "Amortization Schedule"
) -> bytes:
    """
    Generates a beautifully styled Excel workbook containing the amortization schedule.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]
    ws.views.sheetView[0].showGridLines = True

    current_row = 1

    # Main Title
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=12)
    title_cell = ws.cell(row=current_row, column=1, value="ADVANCED LOAN EMI & AMORTIZATION SCHEDULE")
    title_cell.font = Font(name="Segoe UI", size=15, bold=True, color="FFFFFF")
    title_cell.fill = NAVY_HEADER_FILL
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[current_row].height = 36
    current_row += 2

    # Summary Section (if provided)
    if loan_summary is not None:
        ws.cell(row=current_row, column=1, value="Loan Overview").font = Font(name="Segoe UI", size=12, bold=True, color="0F172A")
        current_row += 1

        summary_pairs = [
            ("Loan Amount:", format_currency(loan_summary.loan_amount), "Monthly EMI:", format_currency(loan_summary.monthly_emi)),
            ("Annual Interest Rate:", format_percentage(loan_summary.annual_rate), "Total Interest:", format_currency(loan_summary.total_interest)),
            ("Tenure:", format_tenure(loan_summary.tenure_months), "Total Repayment:", format_currency(loan_summary.total_repayment)),
            ("Start Date:", format_date_standard(loan_summary.start_date), "Completion Date:", format_date_standard(loan_summary.completion_date)),
        ]

        for p in summary_pairs:
            ws.cell(row=current_row, column=1, value=p[0]).font = Font(name="Segoe UI", bold=True, color="475569")
            ws.cell(row=current_row, column=2, value=p[1]).font = Font(name="Segoe UI", bold=False, color="0F172A")
            ws.cell(row=current_row, column=4, value=p[2]).font = Font(name="Segoe UI", bold=True, color="475569")
            ws.cell(row=current_row, column=5, value=p[3]).font = Font(name="Segoe UI", bold=False, color="0F172A")
            current_row += 1

        current_row += 2

    # Amortization Table Headers
    cols = list(schedule_df.columns)
    for col_idx, col_name in enumerate(cols, start=1):
        cell = ws.cell(row=current_row, column=col_idx, value=col_name)
        cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        cell.fill = SUBHEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    # Data Rows
    for row_idx, row in schedule_df.iterrows():
        is_even = (row_idx % 2 == 0)
        row_fill = LIGHT_ZEBRA_FILL if is_even else WHITE_FILL

        for col_idx, col_name in enumerate(cols, start=1):
            val = row[col_name]
            cell = ws.cell(row=current_row, column=col_idx)

            if isinstance(val, (int, float)):
                cell.value = float(val)
                if col_name == "Month":
                    cell.number_format = "#,##0"
                    cell.alignment = Alignment(horizontal="center")
                else:
                    cell.number_format = "#,##0.00"
                    cell.alignment = Alignment(horizontal="right")
            else:
                cell.value = str(val)
                cell.alignment = Alignment(horizontal="center")

            cell.font = Font(name="Segoe UI", size=9)
            cell.fill = row_fill
            cell.border = THIN_BORDER

        current_row += 1

    # Totals Row
    ws.cell(row=current_row, column=1, value="TOTALS").font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    for col_idx, col_name in enumerate(cols, start=1):
        tot_cell = ws.cell(row=current_row, column=col_idx)
        tot_cell.fill = NAVY_HEADER_FILL
        tot_cell.font = Font(name="Segoe UI", size=9, bold=True, color="FFFFFF")
        tot_cell.border = THIN_BORDER
        if col_name in ["Interest", "Principal", "Additional Payment", "Total Principal", "EMI"]:
            tot_val = float(schedule_df[col_name].sum())
            tot_cell.value = tot_val
            tot_cell.number_format = "#,##0.00"
            tot_cell.alignment = Alignment(horizontal="right")

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 13)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def generate_excel_comparison(comp_result: Any) -> bytes:
    """
    Generates an Excel workbook comparing multiple loan scenarios.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scenario Comparison"
    ws.views.sheetView[0].showGridLines = True

    # Title
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(comp_result.summary_df.columns))
    title_cell = ws.cell(row=1, column=1, value="FINANCIAL SCENARIO COMPARISON REPORT")
    title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    title_cell.fill = NAVY_HEADER_FILL
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    current_row = 3
    df = comp_result.summary_df

    # Headers
    for c_idx, c_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=current_row, column=c_idx, value=c_name)
        cell.font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        cell.fill = SUBHEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = THIN_BORDER
    ws.row_dimensions[current_row].height = 24
    current_row += 1

    # Rows
    for r_idx, row in df.iterrows():
        is_even = (r_idx % 2 == 0)
        row_fill = LIGHT_ZEBRA_FILL if is_even else WHITE_FILL

        for c_idx, c_name in enumerate(df.columns, start=1):
            val = row[c_name]
            cell = ws.cell(row=current_row, column=c_idx)
            cell.font = Font(name="Segoe UI", size=9)
            cell.fill = row_fill
            cell.border = THIN_BORDER

            if isinstance(val, (int, float)):
                cell.value = float(val)
                if "Month" in str(row["Metric"]) or "EMIs" in str(row["Metric"]):
                    cell.number_format = "#,##0"
                elif "%" in str(row["Metric"]):
                    cell.number_format = "0.00"
                else:
                    cell.number_format = "#,##0.00"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.value = str(val)
                cell.alignment = Alignment(horizontal="left" if c_idx == 1 else "center")

        current_row += 1

    # Column widths
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[col_letter].width = max(max_len + 5, 18)

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


# --- ReportLab PDF Helpers ---

def generate_pdf_report(
    loan_summary: Any,
    schedule_df: pd.DataFrame,
    result_a: Optional[Any] = None,
    result_b: Optional[Any] = None
) -> bytes:
    """
    Generates a high-quality PDF report with executive summary,
    option comparisons, and an amortized repayment statement.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
        alignment=1,  # Center
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15,
        alignment=1,
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#1E293B"),
        leading=12,
    )
    legal_style = ParagraphStyle(
        "LegalNotice",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        textColor=colors.HexColor("#64748B"),
        leading=10,
        spaceBefore=12,
    )

    story = []

    # Title & Header
    story.append(Paragraph("LOAN REPAYMENT & PREPAYMENT REPORT", title_style))
    story.append(Paragraph(f"Generated on {datetime.date.today().strftime('%d %B %Y')} | Confidential Financial Planning Document", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=15))

    # Loan Summary Table
    story.append(Paragraph("1. Executive Loan Summary", section_style))
    summary_data = [
        [
            Paragraph("<b>Loan Amount</b>", body_style), format_currency(loan_summary.loan_amount),
            Paragraph("<b>Monthly EMI</b>", body_style), format_currency(loan_summary.monthly_emi),
        ],
        [
            Paragraph("<b>Annual Interest Rate</b>", body_style), format_percentage(loan_summary.annual_rate),
            Paragraph("<b>Total Interest Payable</b>", body_style), format_currency(loan_summary.total_interest),
        ],
        [
            Paragraph("<b>Total Tenure</b>", body_style), format_tenure(loan_summary.tenure_months),
            Paragraph("<b>Total Repayment</b>", body_style), format_currency(loan_summary.total_repayment),
        ],
        [
            Paragraph("<b>Start Date</b>", body_style), format_date_standard(loan_summary.start_date),
            Paragraph("<b>Maturity Date</b>", body_style), format_date_standard(loan_summary.completion_date),
        ],
    ]

    t_summary = Table(summary_data, colWidths=[130, 130, 130, 145])
    t_summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 12))

    # Prepayment Comparison Table (if available)
    if result_a is not None and result_b is not None:
        story.append(Paragraph("2. Prepayment Strategy Comparison", section_style))
        story.append(Paragraph(
            f"Simulation: Part-payment of <b>{format_currency(result_a.total_prepayment_paid)}</b> at Month <b>{result_a.part_payment_month}</b>.",
            body_style
        ))
        story.append(Spacer(1, 6))

        comp_data = [
            ["Metric", "Original Baseline", "Option A: Reduce EMI", "Option B: Reduce Tenure"],
            ["Monthly EMI", format_currency(result_a.original_emi), format_currency(result_a.revised_emi), format_currency(result_b.revised_emi)],
            ["Tenure (Months)", f"{result_a.original_tenure_months} mos", f"{result_a.revised_tenure_months} mos", f"{result_b.revised_tenure_months} mos"],
            ["Tenure Reduction", "0 mos", "0 mos", f"{result_b.tenure_reduction_months} months saved"],
            ["Total Interest", format_currency(result_a.original_total_interest), format_currency(result_a.revised_total_interest), format_currency(result_b.revised_total_interest)],
            ["Total Interest Saved", "₹ 0.00", format_currency(result_a.interest_saved), format_currency(result_b.interest_saved)],
            ["Interest Savings (%)", "0.0%", format_percentage(result_a.interest_savings_pct), format_percentage(result_b.interest_savings_pct)],
            ["Total Repayment", format_currency(result_a.original_total_payment), format_currency(result_a.revised_total_payment), format_currency(result_b.revised_total_payment)],
        ]

        t_comp = Table(comp_data, colWidths=[140, 130, 130, 135])
        t_comp.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            # Highlight interest saved row
            ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#D1FAE5")),
            ("TEXTCOLOR", (0, 5), (-1, 5), colors.HexColor("#065F46")),
            ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
        ]))
        story.append(t_comp)
        story.append(Spacer(1, 14))

    # Amortization Table Preview (First 24 months + total)
    story.append(Paragraph("3. Amortization Schedule (First 24 Months Preview)", section_style))
    sample_df = schedule_df.head(24)

    sched_headers = ["Month", "Date", "Opening Bal", "EMI", "Interest", "Principal", "Closing Bal"]
    sched_data = [sched_headers]

    for _, r in sample_df.iterrows():
        sched_data.append([
            str(r["Month"]),
            str(r["Payment Date"]),
            format_currency(r["Opening Balance"], include_symbol=False),
            format_currency(r["EMI"], include_symbol=False),
            format_currency(r["Interest"], include_symbol=False),
            format_currency(r["Total Principal"], include_symbol=False),
            format_currency(r["Closing Balance"], include_symbol=False),
        ])

    t_sched = Table(sched_data, colWidths=[40, 75, 84, 84, 84, 84, 84])
    t_sched.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_sched)

    # Disclaimer
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "<b>Important Notice:</b> This report is generated by the Advanced Loan EMI & Repayment Calculator for "
        "informational and budgeting purposes. Please consult your lending institution for official settlement figures, "
        "applicable foreclosure fees, and exact broken-period day counts.",
        legal_style
    ))

    doc.build(story)
    return buffer.getvalue()

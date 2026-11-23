"""
Unit tests for Excel and PDF report generation.
"""

import pytest
import datetime
from calculations.emi import calculate_loan_summary
from calculations.amortization import generate_amortization_schedule
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
)
from calculations.comparison import compare_scenarios
from utils.export import generate_excel_amortization, generate_excel_comparison, generate_pdf_report


def test_excel_amortization_export():
    """Verify that openpyxl generates non-empty valid xlsx bytes."""
    summary = calculate_loan_summary(500000.0, 9.5, 3, 0)
    sched = generate_amortization_schedule(500000.0, 9.5, 36)

    excel_bytes = generate_excel_amortization(sched, summary)
    assert len(excel_bytes) > 2000
    # Check magic bytes for ZIP/XLSX
    assert excel_bytes[:2] == b"PK"


def test_excel_comparison_export():
    """Verify scenario comparison Excel generation."""
    principal = 500000.0
    rate = 9.5
    tenure = 36
    sched = generate_amortization_schedule(principal, rate, tenure)
    res_a = calculate_revised_schedule_reduce_emi(principal, rate, tenure, 12, 50000.0)
    res_b = calculate_revised_schedule_reduce_tenure(principal, rate, tenure, 12, 50000.0)
    comp = compare_scenarios(principal, sched, res_a, res_b)

    excel_bytes = generate_excel_comparison(comp)
    assert len(excel_bytes) > 2000
    assert excel_bytes[:2] == b"PK"


def test_pdf_report_export():
    """Verify ReportLab produces valid PDF bytes."""
    summary = calculate_loan_summary(500000.0, 9.5, 3, 0, start_date=datetime.date(2025, 1, 1))
    sched = generate_amortization_schedule(500000.0, 9.5, 36, start_date=datetime.date(2025, 1, 1))
    res_a = calculate_revised_schedule_reduce_emi(500000.0, 9.5, 36, 12, 50000.0, start_date=datetime.date(2025, 1, 1))
    res_b = calculate_revised_schedule_reduce_tenure(500000.0, 9.5, 36, 12, 50000.0, start_date=datetime.date(2025, 1, 1))

    pdf_bytes = generate_pdf_report(summary, sched, res_a, res_b)
    assert len(pdf_bytes) > 3000
    # PDF magic bytes
    assert pdf_bytes[:4] == b"%PDF"

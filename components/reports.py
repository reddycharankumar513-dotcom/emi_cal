"""
Reports View Component.
Handles statement generation and one-click downloads for Excel (.xlsx) workbooks
and bank-grade PDF reports in unified dark navy theme.
"""

import streamlit as st
import pandas as pd
from typing import Any, Optional
import datetime
from utils.export import generate_excel_amortization, generate_excel_comparison, generate_pdf_report
from utils.formatting import format_currency, format_percentage, format_tenure


def render_reports_view(
    summary: Any,
    orig_schedule: pd.DataFrame,
    result_a: Optional[Any],
    result_b: Optional[Any],
    comp_result: Optional[Any],
    currency_style: str = "standard_inr"
) -> None:
    """
    Renders the Reports & Downloads page with interactive export generators.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                📑 Financial Statements & Export Center
            </h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                Download complete amortization schedules, prepayment audits, and scenario matrices in Excel and PDF formats.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # 1. Excel Amortization Schedules
    with col1:
        st.markdown(
            """
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); height: 100%;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                    📊 Amortization Schedules (Excel)
                </div>
                <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 16px;">
                    Full month-by-month payment ledger with opening balance, interest, principal breakdown, and running totals formatted in Excel (.xlsx).
                </p>
            """,
            unsafe_allow_html=True
        )

        # Baseline schedule download
        excel_orig = generate_excel_amortization(
            schedule_df=orig_schedule,
            loan_summary=summary,
            sheet_title="Original Schedule"
        )
        st.download_button(
            label="📥 Download Original Schedule (Excel)",
            data=excel_orig,
            file_name=f"Loan_Amortization_Original_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_orig_excel"
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Revised Option A schedule download
        if result_a is not None:
            excel_a = generate_excel_amortization(
                schedule_df=result_a.revised_schedule,
                loan_summary=summary,
                sheet_title="Option A (Reduce EMI)"
            )
            st.download_button(
                label="📥 Download Option A Schedule (Excel)",
                data=excel_a,
                file_name=f"Loan_Schedule_OptionA_ReduceEMI_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_opt_a_excel"
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Revised Option B schedule download
        if result_b is not None:
            excel_b = generate_excel_amortization(
                schedule_df=result_b.revised_schedule,
                loan_summary=summary,
                sheet_title="Option B (Reduce Tenure)"
            )
            st.download_button(
                label="📥 Download Option B Schedule (Excel)",
                data=excel_b,
                file_name=f"Loan_Schedule_OptionB_ReduceTenure_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_opt_b_excel"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Executive PDF Reports & Comparison Matrix
    with col2:
        st.markdown(
            """
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); height: 100%;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                    📑 Formal PDF Reports & Audit Matrices
                </div>
                <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 16px;">
                    Printable banking-style summary statement containing executive metrics, prepayment savings audit, and first 24-month schedule.
                </p>
            """,
            unsafe_allow_html=True
        )

        # Complete PDF Report
        pdf_bytes = generate_pdf_report(
            loan_summary=summary,
            schedule_df=orig_schedule,
            result_a=result_a,
            result_b=result_b
        )
        st.download_button(
            label="📄 Generate & Download Official PDF Report",
            data=pdf_bytes,
            file_name=f"Loan_Repayment_Report_{datetime.date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_pdf_rep"
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Scenario Comparison Excel
        if comp_result is not None:
            excel_comp = generate_excel_comparison(comp_result)
            st.download_button(
                label="📊 Download Scenario Comparison Matrix (Excel)",
                data=excel_comp,
                file_name=f"Loan_Scenario_Comparison_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_comp_excel"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Loan Executive Summary Table
    st.markdown("### 📋 Executive Summary Table")
    summary_data = {
        "Parameter": [
            "Loan Principal Amount",
            "Annual Interest Rate",
            "Loan Tenure",
            "Monthly EMI (Original)",
            "Total Interest Payable",
            "Total Repayment Amount",
            "Interest-to-Principal Ratio",
            "Prepayment Month (Configured)",
            "Prepayment Amount (Configured)",
            "Tenure Savings (Option B)",
            "Interest Saved (Option B)"
        ],
        "Value": [
            format_currency(summary.loan_amount, style=currency_style),
            format_percentage(summary.annual_rate),
            format_tenure(summary.tenure_months),
            format_currency(summary.monthly_emi, style=currency_style),
            format_currency(summary.total_interest, style=currency_style),
            format_currency(summary.total_repayment, style=currency_style),
            f"{summary.interest_to_principal_ratio:.1f}%",
            f"Month {result_b.part_payment_month}" if result_b else "N/A",
            format_currency(result_b.total_prepayment_paid, style=currency_style) if result_b else "N/A",
            f"{result_b.tenure_reduction_months} months ({result_b.emis_eliminated} EMIs eliminated)" if result_b else "N/A",
            format_currency(result_b.interest_saved, style=currency_style) if result_b else "N/A",
        ]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

"""
Dashboard View Component.
Displays high-level financial summary cards, visual asset distributions,
and instant prepayment opportunity highlights in unified dark navy theme.
"""

import streamlit as st
import pandas as pd
from typing import Any
from utils.formatting import format_currency, format_percentage, format_tenure, format_date_standard
from components.charts import render_total_pie_chart, render_balance_chart
from config import THEME_COLORS


def render_dashboard_view(
    summary: Any,
    orig_schedule: pd.DataFrame,
    result_b: Any,
    currency_style: str = "standard_inr"
) -> None:
    """
    Renders the executive financial dashboard view.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                📊 Loan Overview & Financial Health Dashboard
            </h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                Real-time tracking of principal liability, amortization pace, and early retirement savings.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4-Column Primary Metrics Grid in Unified Navy
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 18px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                    Monthly EMI
                </div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-top: 4px;">
                    {format_currency(summary.monthly_emi, style=currency_style)}
                </div>
                <div style="font-size: 0.75rem; color: #10b981; font-weight: 600; margin-top: 4px;">
                    Rate: {summary.monthly_interest_rate:.3f}% per month
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 18px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                    Principal Amount
                </div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-top: 4px;">
                    {format_currency(summary.loan_amount, style=currency_style)}
                </div>
                <div style="font-size: 0.75rem; color: #38bdf8; margin-top: 4px;">
                    Duration: {format_tenure(summary.tenure_months)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 18px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                    Total Interest
                </div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #f59e0b; margin-top: 4px;">
                    {format_currency(summary.total_interest, style=currency_style)}
                </div>
                <div style="font-size: 0.75rem; color: #fbbf24; font-weight: 600; margin-top: 4px;">
                    Ratio: {summary.interest_to_principal_ratio:.1f}% of principal
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div style="background-color: #131f37; border: 1px solid #22314e; border-radius: 10px; padding: 18px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                <div style="font-size: 0.78rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                    Total Repayment
                </div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-top: 4px;">
                    {format_currency(summary.total_repayment, style=currency_style)}
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                    Matures: {format_date_standard(summary.completion_date)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Opportunity Banner: Tenure Reduction Savings Callout
    if result_b is not None and result_b.interest_saved > 0:
        st.markdown(
            f"""
            <div style="background: linear-gradient(90deg, #131f37 0%, #1e293b 100%); border-left: 5px solid #10b981; border-radius: 10px; padding: 18px 22px; color: #ffffff; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); border-top: 1px solid #22314e; border-right: 1px solid #22314e; border-bottom: 1px solid #22314e;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #10b981; font-weight: 700;">
                            💡 Prepayment Opportunity Highlight
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 600; margin-top: 6px;">
                            Paying an extra <b>{format_currency(result_b.total_prepayment_paid, style=currency_style)}</b> at Month <b>{result_b.part_payment_month}</b> saves 
                            <span style="color: #10b981; font-weight: 700;">{format_currency(result_b.interest_saved, style=currency_style)}</span> in finance costs!
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                            Eliminates <b style="color: #ffffff;">{result_b.emis_eliminated} EMIs</b> ({result_b.tenure_reduction_months} months) and finishes early on <b style="color: #38bdf8;">{format_date_standard(result_b.revised_completion_date)}</b>.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Visual Analytics Row
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        pie_fig = render_total_pie_chart(
            principal=summary.loan_amount,
            total_interest=summary.total_interest,
            title="Loan Cost Distribution"
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with chart_col2:
        bal_fig = render_balance_chart(
            schedule_df=orig_schedule,
            title="Scheduled Amortization Curve"
        )
        st.plotly_chart(bal_fig, use_container_width=True)

    # Quick Navigation Cards
    st.markdown("### ⚡ Quick Actions")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("📅 View Month-by-Month Schedule", use_container_width=True):
            st.session_state["active_page"] = "Repayment Schedule"
            st.rerun()
    with q2:
        if st.button("💰 Optimize Prepayment Options", use_container_width=True):
            st.session_state["active_page"] = "Part-Payment Calculator"
            st.rerun()
    with q3:
        if st.button("📥 Download Statements & Reports", use_container_width=True):
            st.session_state["active_page"] = "Reports & Downloads"
            st.rerun()

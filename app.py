"""
Advanced Loan EMI & Repayment Calculator.
Main Application Entry Point built with Streamlit, Plotly, Pandas, and OpenPyXL.
Styled in a unified, professional dark navy & emerald banking aesthetic.
"""

import streamlit as st
import datetime
import pandas as pd
import numpy as np

# Page configuration - must be called first
st.set_page_config(
    page_title="Loan EMI & Repayment Calculator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Unified Dark Navy & Emerald Styling Injection
st.markdown(
    """
    <style>
        /* Base typography and full viewport background */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            color: #f8fafc;
        }

        .stApp {
            background-color: #0b1120;
        }

        /* Main container styling */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1400px;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #22314e;
        }

        /* Metric card container styling */
        div[data-testid="stMetric"] {
            background-color: #131f37;
            border: 1px solid #22314e;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.55rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        /* Buttons styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background-color: #131f37;
            color: #ffffff;
            border: 1px solid #22314e;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            border-color: #10b981;
            color: #10b981;
            background-color: #1e293b;
        }

        /* Inputs & Selectboxes */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: #131f37 !important;
            border-color: #22314e !important;
            color: #ffffff !important;
        }

        /* Dataframe styling */
        div[data-testid="stDataFrame"] {
            border: 1px solid #22314e;
            border-radius: 8px;
            overflow: hidden;
            background-color: #131f37;
        }

        /* Headings */
        h1, h2, h3, h4 {
            color: #ffffff !important;
        }

        /* Paragraphs and captions */
        p, span, label {
            color: #cbd5e1;
        }
    </style>
    """,
    unsafe_allow_html=True
)

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    THEME_COLORS,
    DEFAULT_LOAN_AMOUNT,
    DEFAULT_INTEREST_RATE,
    DEFAULT_TENURE_YEARS,
    DEFAULT_TENURE_MONTHS,
    DEFAULT_PART_PAYMENT_MONTH,
    DEFAULT_PART_PAYMENT_AMOUNT,
    CALCULATION_CONVENTIONS,
    INTEREST_ROUNDING_OPTIONS,
    CURRENCY_DISPLAY_FORMATS,
    LEGAL_DISCLAIMER,
)
from calculations.emi import calculate_emi, calculate_loan_summary
from calculations.amortization import generate_amortization_schedule
from calculations.part_payment import (
    calculate_revised_schedule_reduce_emi,
    calculate_revised_schedule_reduce_tenure,
    calculate_custom_prepayment_schedule,
    get_outstanding_balance_after_month,
)
from calculations.comparison import compare_scenarios
from utils.formatting import (
    format_currency,
    format_percentage,
    format_tenure,
    format_date_standard,
)
from utils.validation import validate_loan_inputs, validate_part_payment_inputs
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard_view
from components.charts import (
    render_monthly_split_chart,
    render_total_pie_chart,
    render_balance_chart,
    render_cumulative_chart,
    render_scenario_comparison_chart,
    render_interest_savings_chart,
)
from components.tables import render_amortization_table, render_comparison_table
from components.reports import render_reports_view


def init_session_state():
    """Initializes global session state variables."""
    if "loan_amount" not in st.session_state:
        st.session_state["loan_amount"] = DEFAULT_LOAN_AMOUNT
    if "annual_rate" not in st.session_state:
        st.session_state["annual_rate"] = DEFAULT_INTEREST_RATE
    if "tenure_years" not in st.session_state:
        st.session_state["tenure_years"] = DEFAULT_TENURE_YEARS
    if "tenure_months_extra" not in st.session_state:
        st.session_state["tenure_months_extra"] = DEFAULT_TENURE_MONTHS
    if "part_payment_month" not in st.session_state:
        st.session_state["part_payment_month"] = DEFAULT_PART_PAYMENT_MONTH
    if "part_payment_amount" not in st.session_state:
        st.session_state["part_payment_amount"] = DEFAULT_PART_PAYMENT_AMOUNT
    if "start_date" not in st.session_state:
        st.session_state["start_date"] = datetime.date.today().replace(day=1)
    if "convention" not in st.session_state:
        st.session_state["convention"] = "monthly_reducing"
    if "rounding_mode" not in st.session_state:
        st.session_state["rounding_mode"] = "standard"
    if "currency_style" not in st.session_state:
        st.session_state["currency_style"] = "standard_inr"


def main():
    init_session_state()

    # Render Sidebar and retrieve active page
    active_page = render_sidebar()

    # Retrieve current active configuration parameters
    loan_amount = float(st.session_state["loan_amount"])
    annual_rate = float(st.session_state["annual_rate"])
    tenure_years = int(st.session_state["tenure_years"])
    tenure_months_extra = int(st.session_state["tenure_months_extra"])
    total_months = (tenure_years * 12) + tenure_months_extra
    start_date = st.session_state["start_date"]
    convention = st.session_state.get("convention", "monthly_reducing")
    rounding_mode = st.session_state.get("rounding_mode", "standard")
    currency_style = st.session_state.get("currency_style", "standard_inr")

    part_month = int(st.session_state["part_payment_month"])
    part_amount = float(st.session_state["part_payment_amount"])

    # 1. Validation
    val_loan = validate_loan_inputs(loan_amount, annual_rate, tenure_years, tenure_months_extra)
    if not val_loan.is_valid:
        st.error(f"❌ Input Error: {val_loan.error_message}")
        return

    # 2. Compute Core Loan Calculations
    try:
        loan_summary = calculate_loan_summary(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            tenure_years=tenure_years,
            tenure_months_extra=tenure_months_extra,
            start_date=start_date,
            method=convention,
            rounding_mode=rounding_mode
        )

        orig_schedule = generate_amortization_schedule(
            principal=loan_amount,
            annual_rate=annual_rate,
            tenure_months=total_months,
            start_date=start_date,
            convention=convention,
            rounding_mode=rounding_mode
        )
    except Exception as e:
        st.error(f"Calculation Error: {str(e)}")
        return

    # 3. Compute Part-Payment Scenarios (Option A & Option B)
    val_part_month = min(part_month, total_months - 1)
    if val_part_month < 1:
        val_part_month = 1

    balance_at_month = get_outstanding_balance_after_month(
        principal=loan_amount,
        annual_rate=annual_rate,
        tenure_months=total_months,
        target_month=val_part_month,
        rounding_mode=rounding_mode
    )

    safe_part_amount = min(part_amount, balance_at_month * 0.99) if balance_at_month > 0 else 0.0

    result_a = None
    result_b = None
    comp_result = None

    if safe_part_amount > 0 and val_part_month < total_months:
        try:
            result_a = calculate_revised_schedule_reduce_emi(
                principal=loan_amount,
                annual_rate=annual_rate,
                tenure_months=total_months,
                part_payment_month=val_part_month,
                part_payment_amount=safe_part_amount,
                start_date=start_date,
                convention=convention,
                rounding_mode=rounding_mode
            )
            result_b = calculate_revised_schedule_reduce_tenure(
                principal=loan_amount,
                annual_rate=annual_rate,
                tenure_months=total_months,
                part_payment_month=val_part_month,
                part_payment_amount=safe_part_amount,
                start_date=start_date,
                convention=convention,
                rounding_mode=rounding_mode
            )
            comp_result = compare_scenarios(
                principal=loan_amount,
                orig_schedule=orig_schedule,
                result_a=result_a,
                result_b=result_b
            )
        except Exception as e:
            # Non-fatal prepayment exception
            pass

    # -------------------------------------------------------------
    # PAGE ROUTING
    # -------------------------------------------------------------

    # Page 1: Dashboard
    if active_page == "Dashboard":
        render_dashboard_view(
            summary=loan_summary,
            orig_schedule=orig_schedule,
            result_b=result_b,
            currency_style=currency_style
        )

    # Page 2: EMI Calculator
    elif active_page == "EMI Calculator":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    🧮 Loan EMI Calculator
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Equated Monthly Installment analysis under reducing-balance financial principles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 📌 Calculation Breakdown")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Monthly EMI", format_currency(loan_summary.monthly_emi, style=currency_style))
                st.metric("Principal Borrowed", format_currency(loan_summary.loan_amount, style=currency_style))
                st.metric("Effective Monthly Rate", f"{loan_summary.monthly_interest_rate:.3f}%")
            with c2:
                st.metric("Total Interest Payable", format_currency(loan_summary.total_interest, style=currency_style))
                st.metric("Total Repayment", format_currency(loan_summary.total_repayment, style=currency_style))
                st.metric("Loan Completion Date", format_date_standard(loan_summary.completion_date))

            st.markdown("---")
            st.markdown("### 📐 Reducing-Balance Mathematical Formula")
            st.latex(r"EMI = \frac{P \times r \times (1 + r)^n}{(1 + r)^n - 1}")
            st.markdown(
                f"""
                - **P (Principal)** = {format_currency(loan_summary.loan_amount, style=currency_style)}
                - **r (Monthly Interest Rate)** = {loan_summary.annual_rate}% / (12 × 100) = `{loan_summary.annual_rate / 1200:.6f}`
                - **n (Duration)** = `{loan_summary.tenure_months}` months
                """
            )
            if loan_summary.annual_rate == 0:
                st.info("ℹ️ **Zero-Interest Loan:** EMI = Principal / Tenure.")

        with col_right:
            pie_fig = render_total_pie_chart(
                principal=loan_summary.loan_amount,
                total_interest=loan_summary.total_interest,
                title="Principal vs Interest Share"
            )
            st.plotly_chart(pie_fig, use_container_width=True)

    # Page 3: Principal & Interest Distribution
    elif active_page == "Principal & Interest Distribution":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    📈 Principal & Interest Distribution Analysis
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Visual progression of monthly repayments, capital recovery, and finance costs over time.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(render_monthly_split_chart(orig_schedule), use_container_width=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.plotly_chart(render_cumulative_chart(orig_schedule), use_container_width=True)
        with col_c2:
            st.plotly_chart(render_balance_chart(orig_schedule), use_container_width=True)

    # Page 4: Repayment Schedule
    elif active_page == "Repayment Schedule":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    📅 Complete Amortization Schedule
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Official month-by-month payment schedule, interest deductions, capital amortization, and closing balances.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        render_amortization_table(orig_schedule, currency_style=currency_style, key_prefix="orig_table")

    # Page 5: Part-Payment Calculator
    elif active_page == "Part-Payment Calculator":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    💰 Part-Payment & Prepayment Optimization
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Evaluate the financial impact of lump sum capital infusions or recurring prepayments.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🔎 Current Prepayment Simulation")
        p_c1, p_c2, p_c3 = st.columns(3)
        with p_c1:
            st.metric("Balance Before Prepayment", format_currency(balance_at_month, style=currency_style))
        with p_c2:
            st.metric("Prepayment Amount", format_currency(safe_part_amount, style=currency_style))
        with p_c3:
            bal_after = max(0.0, balance_at_month - safe_part_amount)
            st.metric("Outstanding Balance After Prepayment", format_currency(bal_after, style=currency_style))

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        if result_a is not None and result_b is not None:
            c_opt_a, c_opt_b = st.columns(2)
            with c_opt_a:
                st.markdown(
                    f"""
                    <div style="background-color: #131f37; border: 1px solid #22314e; border-top: 4px solid #38bdf8; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">
                            Option A: Reduce Monthly EMI
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                            Keep loan maturity date fixed, lower monthly cash outflow.
                        </div>
                        <hr style="border: 0; border-top: 1px solid #22314e; margin: 14px 0;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff;">
                            {format_currency(result_a.revised_emi, style=currency_style)} <span style="font-size: 0.85rem; color: #10b981;">(-{result_a.emi_reduction_pct:.1f}%)</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px;">
                            Monthly Cashflow Saved: <b style="color: #38bdf8;">{format_currency(result_a.emi_reduction_amount, style=currency_style)}</b>
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                            Total Interest Saved: <b style="color: #10b981;">{format_currency(result_a.interest_saved, style=currency_style)}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_opt_b:
                st.markdown(
                    f"""
                    <div style="background-color: #131f37; border: 1px solid #22314e; border-top: 4px solid #10b981; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">
                            Option B: Reduce Loan Tenure
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                            Keep EMI constant, eliminate debt and maximize savings.
                        </div>
                        <hr style="border: 0; border-top: 1px solid #22314e; margin: 14px 0;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">
                            {result_b.emis_eliminated} EMIs Eliminated
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px;">
                            Revised Tenure: <b style="color: #ffffff;">{format_tenure(result_b.revised_tenure_months)}</b> (saved {result_b.tenure_reduction_months} mos)
                        </div>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                            Total Interest Saved: <b style="color: #10b981;">{format_currency(result_b.interest_saved, style=currency_style)}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            st.plotly_chart(
                render_scenario_comparison_chart(
                    orig_schedule,
                    result_a.revised_schedule,
                    result_b.revised_schedule
                ),
                use_container_width=True
            )

        # Advanced Multiple Prepayment Simulator
        st.markdown("<hr style='border:0; border-top:1px solid #22314e; margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔄 Multi-Payment & Recurring Prepayment Simulation")
        rec_type = st.radio(
            "Select Prepayment Strategy",
            options=["One-time Lump Sum", "Monthly Extra Principal", "Yearly Prepayment (e.g. Annual Bonus)", "Full Foreclosure"],
            horizontal=True
        )

        if rec_type == "Monthly Extra Principal":
            extra_monthly = st.number_input("Extra Principal Every Month (₹)", min_value=500.0, max_value=loan_amount*0.5, value=5000.0, step=1000.0)
            start_m = st.number_input("Start from Month", min_value=1, max_value=total_months-1, value=1)
            prep_dict = {m: extra_monthly for m in range(int(start_m), total_months + 1)}
            res_rec = calculate_custom_prepayment_schedule(loan_amount, annual_rate, total_months, prep_dict, start_date)
            st.success(
                f"Paying an extra {format_currency(extra_monthly, style=currency_style)} every month eliminates "
                f"**{res_rec.emis_eliminated} EMIs** and saves **{format_currency(res_rec.interest_saved, style=currency_style)}** in interest!"
            )
            render_amortization_table(res_rec.revised_schedule, currency_style=currency_style, key_prefix="rec_monthly_table")

        elif rec_type == "Yearly Prepayment (e.g. Annual Bonus)":
            extra_yearly = st.number_input("Extra Principal Every Year (₹)", min_value=1000.0, max_value=loan_amount*0.8, value=50000.0, step=10000.0)
            prep_dict = {m: extra_yearly for m in range(12, total_months + 1, 12)}
            res_rec = calculate_custom_prepayment_schedule(loan_amount, annual_rate, total_months, prep_dict, start_date)
            st.success(
                f"Paying an extra {format_currency(extra_yearly, style=currency_style)} annually eliminates "
                f"**{res_rec.emis_eliminated} EMIs** and saves **{format_currency(res_rec.interest_saved, style=currency_style)}** in interest!"
            )
            render_amortization_table(res_rec.revised_schedule, currency_style=currency_style, key_prefix="rec_yearly_table")

        elif rec_type == "Full Foreclosure":
            foreclose_month = st.slider("Foreclose Loan at Month", min_value=1, max_value=total_months-1, value=12)
            bal_foreclose = get_outstanding_balance_after_month(loan_amount, annual_rate, total_months, foreclose_month)
            res_foreclose = calculate_custom_prepayment_schedule(loan_amount, annual_rate, total_months, {foreclose_month: bal_foreclose}, start_date)
            st.warning(
                f"Full Foreclosure at Month {foreclose_month}: Pay remaining principal of **{format_currency(bal_foreclose, style=currency_style)}** "
                f"to close the loan. Total interest saved: **{format_currency(res_foreclose.interest_saved, style=currency_style)}**."
            )

    # Page 6: EMI Reduction
    elif active_page == "EMI Reduction":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    📉 Option A: EMI Reduction Analysis
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Reduces your monthly EMI commitment while keeping your original loan completion date unchanged.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if result_a is not None:
            a1, a2, a3, a4 = st.columns(4)
            with a1:
                st.metric("Original Monthly EMI", format_currency(result_a.original_emi, style=currency_style))
            with a2:
                st.metric("Revised Monthly EMI", format_currency(result_a.revised_emi, style=currency_style), delta=f"-{result_a.emi_reduction_pct:.1f}%")
            with a3:
                st.metric("Monthly Cashflow Saved", format_currency(result_a.emi_reduction_amount, style=currency_style))
            with a4:
                st.metric("Total Interest Saved", format_currency(result_a.interest_saved, style=currency_style))

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            st.plotly_chart(render_monthly_split_chart(result_a.revised_schedule, title="Revised Repayment Breakdown (Reduced EMI)"), use_container_width=True)
            st.markdown("### 📋 Revised Schedule Ledger")
            render_amortization_table(result_a.revised_schedule, currency_style=currency_style, key_prefix="opt_a_table")
        else:
            st.info("Please configure a valid part-payment in the sidebar to view EMI Reduction.")

    # Page 7: Tenure Reduction
    elif active_page == "Tenure Reduction":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    ⏱️ Option B: Tenure Reduction Analysis
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Keeps your monthly EMI constant to accelerate principal repayment, slashing years off your loan.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if result_b is not None:
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                st.metric("Original Tenure", format_tenure(result_b.original_tenure_months))
            with b2:
                st.metric("Revised Tenure", format_tenure(result_b.revised_tenure_months), delta=f"-{result_b.tenure_reduction_months} mos")
            with b3:
                st.metric("EMIs Eliminated", f"{result_b.emis_eliminated} EMIs")
            with b4:
                st.metric("Total Interest Saved", format_currency(result_b.interest_saved, style=currency_style))

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            st.plotly_chart(render_balance_chart(result_b.revised_schedule, title="Accelerated Balance Amortization Curve"), use_container_width=True)
            st.markdown("### 📋 Revised Accelerated Schedule Ledger")
            render_amortization_table(result_b.revised_schedule, currency_style=currency_style, key_prefix="opt_b_table")
        else:
            st.info("Please configure a valid part-payment in the sidebar to view Tenure Reduction.")

    # Page 8: Scenario Comparison
    elif active_page == "Scenario Comparison":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    ⚖️ Multi-Scenario Financial Matrix
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Direct side-by-side audit comparing Baseline, Option A, and Option B repayment strategies.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if comp_result is not None:
            render_comparison_table(comp_result.summary_df, currency_style=currency_style)

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(render_interest_savings_chart(comp_result.summary_df), use_container_width=True)
            with c2:
                st.plotly_chart(
                    render_scenario_comparison_chart(
                        orig_schedule,
                        result_a.revised_schedule,
                        result_b.revised_schedule
                    ),
                    use_container_width=True
                )
        else:
            st.info("Please configure a valid part-payment in the sidebar to generate Scenario Comparison.")

    # Page 9: Reports & Downloads
    elif active_page == "Reports & Downloads":
        render_reports_view(
            summary=loan_summary,
            orig_schedule=orig_schedule,
            result_a=result_a,
            result_b=result_b,
            comp_result=comp_result,
            currency_style=currency_style
        )

    # Page 10: Settings
    elif active_page == "Settings":
        st.markdown(
            """
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">
                    ⚙️ Calculation Conventions & Display Settings
                </h1>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                    Configure lender-specific accounting formulas, rounding rules, and denomination formats.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        s_col1, s_col2 = st.columns(2)

        with s_col1:
            st.markdown("### 🏦 Lender Calculation Rules")
            sel_conv = st.selectbox(
                "Interest Calculation Convention",
                options=list(CALCULATION_CONVENTIONS.keys()),
                format_func=lambda x: CALCULATION_CONVENTIONS[x],
                index=list(CALCULATION_CONVENTIONS.keys()).index(st.session_state.get("convention", "monthly_reducing")),
                help="Retail loans generally use monthly reducing balance; overdraft/commercial loans may use daily reducing balance."
            )
            st.session_state["convention"] = sel_conv

            sel_round = st.selectbox(
                "Interest Rounding Convention",
                options=list(INTEREST_ROUNDING_OPTIONS.keys()),
                format_func=lambda x: INTEREST_ROUNDING_OPTIONS[x],
                index=list(INTEREST_ROUNDING_OPTIONS.keys()).index(st.session_state.get("rounding_mode", "standard")),
                help="Configure whether pennies/paise are rounded to 2 decimal places or rounded to the nearest integer Rupee."
            )
            st.session_state["rounding_mode"] = sel_round

        with s_col2:
            st.markdown("### 🇮🇳 Currency & Number Formatting")
            sel_curr = st.selectbox(
                "Currency Display Format",
                options=list(CURRENCY_DISPLAY_FORMATS.keys()),
                format_func=lambda x: CURRENCY_DISPLAY_FORMATS[x],
                index=list(CURRENCY_DISPLAY_FORMATS.keys()).index(st.session_state.get("currency_style", "standard_inr")),
            )
            st.session_state["currency_style"] = sel_curr

            st.markdown("### ℹ️ Regulatory & Financial Disclaimer")
            st.info(LEGAL_DISCLAIMER)

    # Footer banner
    st.markdown("<hr style='border:0; border-top:1px solid #22314e; margin: 24px 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; color: #64748b; font-size: 0.78rem;">
            <div>{APP_TITLE} v{st.session_state.get('version', '2.0.0')} | Bank-Grade Calculation Engine</div>
            <div>Built with Python, Streamlit, Pandas, Plotly & OpenPyXL</div>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

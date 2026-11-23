"""
Sidebar Component.
Hosts global navigation, responsive loan parameter input controls,
prepayment triggers, and quick reset features.
"""

import streamlit as st
import datetime
from config import (
    APP_TITLE,
    APP_VERSION,
    NAVIGATION_PAGES,
    DEFAULT_LOAN_AMOUNT,
    DEFAULT_INTEREST_RATE,
    DEFAULT_TENURE_YEARS,
    DEFAULT_TENURE_MONTHS,
    DEFAULT_PART_PAYMENT_MONTH,
    DEFAULT_PART_PAYMENT_AMOUNT,
    CALCULATION_CONVENTIONS,
)
from utils.formatting import format_currency


def render_sidebar() -> str:
    """
    Renders the sidebar navigation and parameter inputs,
    syncing them with st.session_state.
    
    Returns:
    - selected_page (str): The active navigation page name.
    """
    with st.sidebar:
        # App Header Brand Banner
        st.markdown(
            """
            <div style="padding: 10px 4px 16px 4px; border-bottom: 1px solid #22314e; margin-bottom: 12px;">
                <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff; line-height: 1.2;">
                    🏦 LoanCalc <span style="color: #10b981;">Pro</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                    Advanced EMI & Amortization Suite v2.0
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Primary Navigation
        st.markdown("### 🧭 Navigation")
        selected_page = st.radio(
            "Select Module",
            options=NAVIGATION_PAGES,
            index=NAVIGATION_PAGES.index(st.session_state.get("active_page", "Dashboard")),
            label_visibility="collapsed",
            key="nav_selection",
        )
        st.session_state["active_page"] = selected_page

        st.markdown("<hr style='border:0; border-top:1px solid #22314e; margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("### ⚙️ Loan Parameters")

        # Loan Amount Input
        loan_amount = st.number_input(
            "Loan Principal Amount (₹)",
            min_value=10_000.0,
            max_value=500_000_000.0,
            value=float(st.session_state.get("loan_amount", DEFAULT_LOAN_AMOUNT)),
            step=50_000.0,
            format="%.2f",
            help="Principal amount borrowed from the lender."
        )
        st.caption(f"Formatted: **{format_currency(loan_amount, style='lakhs_crores')}**")
        st.session_state["loan_amount"] = loan_amount

        # Annual Interest Rate Input
        annual_rate = st.number_input(
            "Annual Interest Rate (% p.a.)",
            min_value=0.0,
            max_value=40.0,
            value=float(st.session_state.get("annual_rate", DEFAULT_INTEREST_RATE)),
            step=0.25,
            format="%.2f",
            help="Annual nominal interest rate. Set to 0.00% for interest-free loans."
        )
        st.session_state["annual_rate"] = annual_rate

        # Tenure Inputs
        col_y, col_m = st.columns(2)
        with col_y:
            tenure_years = st.number_input(
                "Tenure (Years)",
                min_value=0,
                max_value=40,
                value=int(st.session_state.get("tenure_years", DEFAULT_TENURE_YEARS)),
                step=1
            )
        with col_m:
            tenure_months_extra = st.number_input(
                "Tenure (Months)",
                min_value=0,
                max_value=11,
                value=int(st.session_state.get("tenure_months_extra", DEFAULT_TENURE_MONTHS)),
                step=1
            )

        total_months = (tenure_years * 12) + tenure_months_extra
        if total_months <= 0:
            st.error("Total tenure must be at least 1 month.")
            total_months = 1
            tenure_months_extra = 1

        st.session_state["tenure_years"] = tenure_years
        st.session_state["tenure_months_extra"] = tenure_months_extra
        st.session_state["total_tenure_months"] = total_months
        st.caption(f"Duration: **{total_months} months** ({tenure_years}y {tenure_months_extra}m)")

        # Start Date Input
        default_date = st.session_state.get("start_date", datetime.date.today().replace(day=1))
        start_date = st.date_input(
            "Loan Start Date (First EMI)",
            value=default_date,
            help="Optional start date to project calendar payment dates."
        )
        st.session_state["start_date"] = start_date

        st.markdown("<hr style='border:0; border-top:1px solid #22314e; margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("### 💰 Part-Payment Setup")

        part_month = st.number_input(
            "Part-Payment at Month",
            min_value=1,
            max_value=max(1, total_months - 1),
            value=min(int(st.session_state.get("part_payment_month", DEFAULT_PART_PAYMENT_MONTH)), max(1, total_months - 1)),
            step=1,
            help="Month number after which additional principal is paid."
        )
        st.session_state["part_payment_month"] = part_month

        part_amount = st.number_input(
            "Part-Payment Amount (₹)",
            min_value=1_000.0,
            max_value=loan_amount,
            value=min(float(st.session_state.get("part_payment_amount", DEFAULT_PART_PAYMENT_AMOUNT)), loan_amount * 0.9),
            step=25_000.0,
            format="%.2f",
            help="Lump sum additional principal to pay."
        )
        st.caption(f"Formatted: **{format_currency(part_amount, style='lakhs_crores')}**")
        st.session_state["part_payment_amount"] = part_amount

        st.markdown("<hr style='border:0; border-top:1px solid #22314e; margin: 16px 0;'>", unsafe_allow_html=True)
        # Reset defaults button
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state["loan_amount"] = DEFAULT_LOAN_AMOUNT
            st.session_state["annual_rate"] = DEFAULT_INTEREST_RATE
            st.session_state["tenure_years"] = DEFAULT_TENURE_YEARS
            st.session_state["tenure_months_extra"] = DEFAULT_TENURE_MONTHS
            st.session_state["part_payment_month"] = DEFAULT_PART_PAYMENT_MONTH
            st.session_state["part_payment_amount"] = DEFAULT_PART_PAYMENT_AMOUNT
            st.session_state["start_date"] = datetime.date.today().replace(day=1)
            st.rerun()

        st.markdown(
            """
            <div style="font-size: 0.72rem; color: #64748b; text-align: center; margin-top: 20px;">
                🔒 Bank-Grade Mathematical Precision<br>
                Unified Dark Navy & Emerald Suite
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_page

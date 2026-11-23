"""
Table Components for Amortization Schedules and Scenario Comparisons.
Provides clean banking-styled tables with filtering by year or month,
formatted currency values, and interactive pagination.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from utils.formatting import format_currency, format_indian_number


def render_amortization_table(
    schedule_df: pd.DataFrame,
    currency_style: str = "standard_inr",
    key_prefix: str = "sched"
) -> None:
    """
    Renders an interactive amortization table with year and month range filters.
    """
    if schedule_df.empty:
        st.info("No amortization data available to display.")
        return

    # Total years in schedule
    max_month = int(schedule_df["Month"].max())
    total_years = (max_month + 11) // 12

    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        view_mode = st.selectbox(
            "Filter Schedule View",
            options=["All Months", "Filter by Year", "Filter by Month Range"],
            key=f"{key_prefix}_view_mode"
        )

    filtered_df = schedule_df.copy()

    if view_mode == "Filter by Year" and total_years > 1:
        with col2:
            selected_year = st.selectbox(
                "Select Year",
                options=[f"Year {y}" for y in range(1, total_years + 1)],
                key=f"{key_prefix}_year_select"
            )
            year_num = int(selected_year.split(" ")[1])
            start_m = (year_num - 1) * 12 + 1
            end_m = min(year_num * 12, max_month)
            filtered_df = filtered_df[(filtered_df["Month"] >= start_m) & (filtered_df["Month"] <= end_m)]

    elif view_mode == "Filter by Month Range":
        with col2:
            start_range = st.number_input(
                "From Month",
                min_value=1,
                max_value=max_month,
                value=1,
                key=f"{key_prefix}_start_m"
            )
        with col3:
            end_range = st.number_input(
                "To Month",
                min_value=int(start_range),
                max_value=max_month,
                value=min(int(start_range) + 23, max_month),
                key=f"{key_prefix}_end_m"
            )
        filtered_df = filtered_df[(filtered_df["Month"] >= start_range) & (filtered_df["Month"] <= end_range)]

    # Display row count indicator
    st.caption(f"Displaying **{len(filtered_df)}** of **{len(schedule_df)}** months")

    # Format values for clean display using string dictionary construction to avoid Pandas dtype collision
    currency_cols = [
        "Opening Balance", "EMI", "Interest", "Principal",
        "Additional Payment", "Total Principal", "Closing Balance",
        "Cumulative Interest", "Cumulative Principal", "Cumulative Total"
    ]

    formatted_rows = []
    for _, row in filtered_df.iterrows():
        row_dict = {
            "Month": int(row["Month"]),
            "Payment Date": str(row["Payment Date"]),
        }
        for c in currency_cols:
            if c in filtered_df.columns:
                row_dict[c] = format_currency(row[c], style=currency_style, include_symbol=True)
        formatted_rows.append(row_dict)

    display_df = pd.DataFrame(formatted_rows)

    # Render Streamlit data table with full container width
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=min(450, 40 + len(display_df) * 35),
    )

    # Summary metric pills below table
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Filtered Principal Repaid", format_currency(filtered_df["Total Principal"].sum(), style=currency_style))
    with s2:
        st.metric("Filtered Interest Paid", format_currency(filtered_df["Interest"].sum(), style=currency_style))
    with s3:
        st.metric("Filtered Total Paid", format_currency((filtered_df["EMI"] + filtered_df["Additional Payment"]).sum(), style=currency_style))
    with s4:
        closing_bal = filtered_df["Closing Balance"].iloc[-1] if not filtered_df.empty else 0.0
        st.metric("Ending Balance", format_currency(closing_bal, style=currency_style))


def render_comparison_table(
    comp_df: pd.DataFrame,
    currency_style: str = "standard_inr"
) -> None:
    """
    Renders a formatted side-by-side scenario comparison table.
    Builds a brand new string-based DataFrame row-by-row to completely avoid
    any Pandas float64 LossySetitemError / TypeError.
    """
    if comp_df.empty:
        st.info("No scenario comparison data available.")
        return

    scenario_cols = [c for c in comp_df.columns if c != "Metric"]
    formatted_rows = []

    for _, row in comp_df.iterrows():
        metric = str(row["Metric"])
        is_currency = (
            any(kw in metric for kw in ["Amount", "EMI", "Balance", "Interest", "Repayment", "Principal", "Paid", "Saved"])
            and "%" not in metric
            and "Months" not in metric
            and "EMIs" not in metric
            and "Years" not in metric
        )
        is_pct = "%" in metric
        is_int = any(kw in metric for kw in ["Months", "EMIs", "Tenure (Months)"])
        is_float_year = "Years" in metric

        new_row = {"Metric": metric}
        for col in scenario_cols:
            raw_val = row[col]
            try:
                if is_currency:
                    new_row[col] = format_currency(raw_val, style=currency_style)
                elif is_pct:
                    new_row[col] = f"{float(raw_val):.2f}%"
                elif is_int:
                    new_row[col] = f"{int(raw_val):,d} mos" if ("Tenure" in metric or "Months" in metric) else f"{int(raw_val):,d}"
                elif is_float_year:
                    new_row[col] = f"{float(raw_val):.2f} yrs"
                else:
                    new_row[col] = str(raw_val)
            except Exception:
                new_row[col] = str(raw_val)

        formatted_rows.append(new_row)

    formatted_df = pd.DataFrame(formatted_rows)

    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True,
        height=min(550, 45 + len(formatted_df) * 36)
    )

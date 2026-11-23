"""
Plotly Chart Components.
Provides interactive banking visualizations matching the unified dark navy & emerald theme:
- Monthly principal vs interest stacked bar chart
- Total principal vs interest donut chart
- Outstanding loan balance line chart
- Cumulative principal and interest curves
- Scenario comparison trajectory curves
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, Dict, Any
from config import THEME_COLORS


def get_common_layout(title: str, height: int = 420) -> dict:
    """Returns a standardized professional dark navy banking chart layout."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Segoe UI, Inter, sans-serif", size=15, color=THEME_COLORS["text_light"]),
            x=0.02,
            y=0.96,
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=30, t=55, b=40),
        font=dict(family="Segoe UI, Inter, sans-serif", color=THEME_COLORS["text_light"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=THEME_COLORS["text_light"]),
        ),
        hoverlabel=dict(
            bgcolor="#131f37",
            font_size=12,
            font_family="Segoe UI, Inter, sans-serif",
            font_color="#ffffff",
            bordercolor="#22314e",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            showline=True,
            linecolor="#334155",
            tickfont=dict(color="#94a3b8"),
            title=dict(text="", font=dict(color="#cbd5e1")),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1e293b",
            zeroline=False,
            showline=True,
            linecolor="#334155",
            tickprefix="₹ ",
            tickfont=dict(color="#94a3b8"),
            title=dict(text="", font=dict(color="#cbd5e1")),
        ),
    )


def render_balance_chart(schedule_df: pd.DataFrame, title: str = "Outstanding Loan Balance Over Time") -> go.Figure:
    """
    Renders an area / line chart showing declining loan balance over time.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=schedule_df["Month"],
            y=schedule_df["Closing Balance"],
            mode="lines",
            name="Outstanding Balance",
            line=dict(color=THEME_COLORS["info_blue"], width=3),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.12)",
            hovertemplate="Month %{x}<br>Outstanding: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    layout = get_common_layout(title)
    layout["xaxis"]["title"] = dict(text="Loan Month", font=dict(color="#cbd5e1"))
    layout["yaxis"]["title"] = dict(text="Outstanding Balance (₹)", font=dict(color="#cbd5e1"))
    fig.update_layout(layout)
    return fig


def render_monthly_split_chart(schedule_df: pd.DataFrame, title: str = "Monthly Principal vs Interest Breakdown") -> go.Figure:
    """
    Renders a stacked bar chart showing the composition of Principal, Additional Prepayment, and Interest.
    """
    fig = go.Figure()

    # Principal component
    fig.add_trace(
        go.Bar(
            x=schedule_df["Month"],
            y=schedule_df["Principal"],
            name="Principal Component",
            marker_color=THEME_COLORS["accent_green"],
            hovertemplate="Month %{x}<br>Principal: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    # Additional payment (if any)
    if "Additional Payment" in schedule_df.columns and schedule_df["Additional Payment"].sum() > 0:
        fig.add_trace(
            go.Bar(
                x=schedule_df["Month"],
                y=schedule_df["Additional Payment"],
                name="Additional Part-Payment",
                marker_color=THEME_COLORS["info_blue"],
                hovertemplate="Month %{x}<br>Extra Payment: <b>₹ %{y:,.2f}</b><extra></extra>",
            )
        )

    # Interest component
    fig.add_trace(
        go.Bar(
            x=schedule_df["Month"],
            y=schedule_df["Interest"],
            name="Interest Component",
            marker_color=THEME_COLORS["warning_amber"],
            hovertemplate="Month %{x}<br>Interest: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    layout = get_common_layout(title)
    layout["barmode"] = "stack"
    layout["xaxis"]["title"] = dict(text="Loan Month", font=dict(color="#cbd5e1"))
    layout["yaxis"]["title"] = dict(text="Payment Amount (₹)", font=dict(color="#cbd5e1"))
    fig.update_layout(layout)
    return fig


def render_total_pie_chart(
    principal: float,
    total_interest: float,
    additional_payments: float = 0.0,
    title: str = "Total Repayment Breakdown"
) -> go.Figure:
    """
    Renders a clean donut chart showing the share of Principal vs Interest.
    """
    labels = ["Principal Loan Amount", "Total Interest Payable"]
    values = [principal, total_interest]
    colors_list = [THEME_COLORS["accent_green"], THEME_COLORS["warning_amber"]]

    if additional_payments > 0:
        labels.append("Prepayments Paid")
        values.append(additional_payments)
        colors_list.append(THEME_COLORS["info_blue"])

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors_list, line=dict(color="#0b1120", width=2)),
                textinfo="percent+label",
                textposition="outside",
                insidetextorientation="horizontal",
                textfont=dict(color="#f8fafc"),
                hovertemplate="<b>%{label}</b><br>Amount: ₹ %{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family="Segoe UI, Inter, sans-serif", size=15, color=THEME_COLORS["text_light"]),
            x=0.02,
            y=0.96,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(color="#f8fafc")
        ),
        font=dict(family="Segoe UI, Inter, sans-serif", color=THEME_COLORS["text_light"]),
    )
    return fig


def render_cumulative_chart(schedule_df: pd.DataFrame, title: str = "Cumulative Repayment Progression") -> go.Figure:
    """
    Renders cumulative lines for Principal repaid, Interest paid, and Total payments.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=schedule_df["Month"],
            y=schedule_df["Cumulative Principal"],
            mode="lines",
            name="Cumulative Principal",
            line=dict(color=THEME_COLORS["accent_green"], width=2.5),
            hovertemplate="Month %{x}<br>Principal Repaid: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=schedule_df["Month"],
            y=schedule_df["Cumulative Interest"],
            mode="lines",
            name="Cumulative Interest",
            line=dict(color=THEME_COLORS["warning_amber"], width=2.5),
            hovertemplate="Month %{x}<br>Interest Paid: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=schedule_df["Month"],
            y=schedule_df["Cumulative Total"],
            mode="lines",
            name="Cumulative Total Paid",
            line=dict(color="#f8fafc", width=2.5, dash="dot"),
            hovertemplate="Month %{x}<br>Total Paid: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    layout = get_common_layout(title)
    layout["xaxis"]["title"] = dict(text="Loan Month", font=dict(color="#cbd5e1"))
    layout["yaxis"]["title"] = dict(text="Cumulative Amount (₹)", font=dict(color="#cbd5e1"))
    fig.update_layout(layout)
    return fig


def render_scenario_comparison_chart(
    orig_df: pd.DataFrame,
    res_a_df: pd.DataFrame,
    res_b_df: pd.DataFrame,
    title: str = "Loan Balance Curves: Baseline vs Option A vs Option B"
) -> go.Figure:
    """
    Plots the outstanding balance over time comparing Original, Option A, and Option B.
    """
    fig = go.Figure()

    # Original curve
    fig.add_trace(
        go.Scatter(
            x=orig_df["Month"],
            y=orig_df["Closing Balance"],
            mode="lines",
            name="Original Baseline",
            line=dict(color=THEME_COLORS["text_muted"], width=2.5, dash="dash"),
            hovertemplate="Baseline Month %{x}<br>Balance: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    # Option A (Reduce EMI)
    fig.add_trace(
        go.Scatter(
            x=res_a_df["Month"],
            y=res_a_df["Closing Balance"],
            mode="lines",
            name="Option A: Reduce EMI",
            line=dict(color=THEME_COLORS["info_blue"], width=3),
            hovertemplate="Option A Month %{x}<br>Balance: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    # Option B (Reduce Tenure)
    fig.add_trace(
        go.Scatter(
            x=res_b_df["Month"],
            y=res_b_df["Closing Balance"],
            mode="lines",
            name="Option B: Reduce Tenure",
            line=dict(color=THEME_COLORS["accent_green"], width=3),
            hovertemplate="Option B Month %{x}<br>Balance: <b>₹ %{y:,.2f}</b><extra></extra>",
        )
    )

    layout = get_common_layout(title, height=450)
    layout["xaxis"]["title"] = dict(text="Loan Month", font=dict(color="#cbd5e1"))
    layout["yaxis"]["title"] = dict(text="Outstanding Balance (₹)", font=dict(color="#cbd5e1"))
    fig.update_layout(layout)
    return fig


def render_interest_savings_chart(
    comp_df: pd.DataFrame,
    title: str = "Total Repayment & Interest by Scenario"
) -> go.Figure:
    """
    Bar chart comparing Total Principal, Prepayment, and Interest across scenarios.
    """
    scenarios = [c for c in comp_df.columns if c != "Metric"]
    
    # Extract values
    interest_vals = []
    repayment_vals = []
    
    int_row = comp_df[comp_df["Metric"] == "Total Interest Payable"]
    rep_row = comp_df[comp_df["Metric"] == "Total Repayment Amount"]
    
    for sc in scenarios:
        interest_vals.append(float(int_row[sc].iloc[0]))
        repayment_vals.append(float(rep_row[sc].iloc[0]))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=interest_vals,
            name="Total Interest",
            marker_color=THEME_COLORS["warning_amber"],
            text=[f"₹ {v:,.0f}" for v in interest_vals],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Interest: ₹ %{y:,.2f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=repayment_vals,
            name="Total Repayment",
            marker_color=THEME_COLORS["info_blue"],
            text=[f"₹ {v:,.0f}" for v in repayment_vals],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Total Repayment: ₹ %{y:,.2f}<extra></extra>",
        )
    )

    layout = get_common_layout(title, height=420)
    layout["barmode"] = "group"
    layout["yaxis"]["title"] = dict(text="Amount (₹)", font=dict(color="#cbd5e1"))
    fig.update_layout(layout)
    return fig

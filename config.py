"""
Application Configuration and Constants.
Configures color themes, currency formatting, calculation conventions, and UI constants.
"""

from dataclasses import dataclass
from typing import Dict, Any

# Application Metadata
APP_TITLE = "Advanced Loan EMI & Repayment Calculator"
APP_SUBTITLE = "Financial Planning, Prepayment Optimization & Amortization Engine"
APP_VERSION = "2.0.0"

# Unified Professional Dark Navy & Emerald Color Palette
THEME_COLORS = {
    "body_bg": "#0b1120",            # Deepest Navy
    "card_bg": "#131f37",            # Elevated Navy Card
    "sidebar_bg": "#0f172a",         # Sidebar Navy
    "card_border": "#22314e",        # Subtle Navy Border
    "accent_green": "#10b981",       # Vibrant Emerald 500
    "dark_green": "#059669",         # Emerald 600
    "light_green": "#064e3b",        # Dark Emerald Tint
    "text_light": "#f8fafc",         # Crisp White Text
    "text_muted": "#94a3b8",         # Slate 400 Text
    "text_dark": "#f8fafc",          # Standard Text for Dark UI
    "danger_red": "#f43f5e",         # Rose 500
    "warning_amber": "#f59e0b",      # Amber 500
    "info_blue": "#38bdf8",          # Sky Blue 400
    "chart_palette": [
        "#10b981",  # Emerald Green
        "#38bdf8",  # Sky Blue
        "#f59e0b",  # Amber
        "#818cf8",  # Indigo
        "#ec4899",  # Pink
        "#06b6d4",  # Cyan
    ]
}

# Default Loan Parameters
DEFAULT_LOAN_AMOUNT = 1_000_000.0  # ₹10,00,000
DEFAULT_INTEREST_RATE = 10.0      # 10% per annum
DEFAULT_TENURE_YEARS = 5
DEFAULT_TENURE_MONTHS = 0
DEFAULT_PART_PAYMENT_MONTH = 18
DEFAULT_PART_PAYMENT_AMOUNT = 200_000.0  # ₹2,00,000

# Calculation Methods & Conventions
CALCULATION_CONVENTIONS = {
    "monthly_reducing": "Monthly Reducing Balance (Standard retail loan)",
    "daily_reducing": "Daily Reducing Balance (Actual days / 365)",
}

INTEREST_ROUNDING_OPTIONS = {
    "standard": "Standard (Exact 2 Decimal places)",
    "round_rupee": "Round to nearest Rupee (₹)",
    "bankers": "Banker's Rounding (Round half to even)",
}

CURRENCY_DISPLAY_FORMATS = {
    "lakhs_crores": "Indian Numbering (₹ Lakhs / Crores)",
    "standard_inr": "Indian Rupee with Full Comma Separation (₹ 10,00,000.00)",
    "millions": "International Standard (₹ Millions)",
}

# Navigation Pages
NAVIGATION_PAGES = [
    "Dashboard",
    "EMI Calculator",
    "Principal & Interest Distribution",
    "Repayment Schedule",
    "Part-Payment Calculator",
    "EMI Reduction",
    "Tenure Reduction",
    "Scenario Comparison",
    "Reports & Downloads",
    "Settings",
]

# Legal & Financial Disclaimer
LEGAL_DISCLAIMER = (
    "Disclaimer: This calculator is designed for financial planning and simulation purposes. "
    "Calculations are based on mathematical reducing balance and day-count formulas. "
    "Actual figures may vary slightly depending on your lender's specific settlement policies, "
    "processing fees, applicable taxes, or broken-period interest conventions."
)

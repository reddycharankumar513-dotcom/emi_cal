# 🏦 Advanced Loan EMI & Repayment Calculator

A production-grade **Loan EMI & Repayment Calculator** and financial analytics suite engineered in Python and Streamlit.

Designed for borrowers, financial analysts, and mortgage planners, this application calculates standard Equated Monthly Installments (EMI), generates month-by-month amortization schedules with zero final balance guarantees, simulates lump sum and recurring part-payments, and provides comparative financial models for **Option A (Reduce Monthly EMI)** and **Option B (Reduce Loan Tenure)**.

---

## 🚀 Key Features & Highlights

- **Bank-Grade Precision Engine**: Built with Decimal arithmetic principles; zero intermediate rounding drift, exact conservation of loan principal, and automatic final EMI balancing.
- **Interactive Multi-Module Navigation**:
  1. **Dashboard**: Executive overview with high-level KPI cards, amortization pace, donut breakdown, and prepayment opportunity banner.
  2. **EMI Calculator**: Live parameter adjustments with formula transparency ($EMI = P \times r \times \frac{(1+r)^n}{(1+r)^n - 1}$).
  3. **Principal & Interest Distribution**: Stacked monthly distribution charts, cumulative repayment curves, and capital recovery visualization.
  4. **Repayment Schedule**: Complete month-by-month ledger with year and month-range filters, searchable pagination, and summary totals.
  5. **Part-Payment Calculator**: Single, recurring (monthly/yearly), custom prepayment simulations, and full loan foreclosure analysis.
  6. **EMI Reduction (Option A)**: In-depth analysis of preserving original maturity date while lowering monthly cash outflow.
  7. **Tenure Reduction (Option B)**: In-depth analysis of preserving monthly EMI while cutting months and years off loan tenure.
  8. **Scenario Comparison**: Side-by-side metric matrix comparing Baseline vs Option A vs Option B vs Custom strategies with overlaid balance curves.
  9. **Reports & Downloads**: One-click generation of styled Excel workbooks (`.xlsx`) and formal banking-grade PDF statements (`.pdf`).
  10. **Settings**: Configurable lender conventions (Monthly Reducing vs Daily Reducing 365-day balance, rounding rules, and Indian ₹ formatting).

---

## 📐 Mathematical Formulation

### 1. Monthly Reducing Balance EMI
The monthly installment is computed using the standard reducing-balance formula:

$$EMI = \frac{P \times r \times (1 + r)^n}{(1 + r)^n - 1}$$

Where:
- $P$ = Principal loan amount borrowed
- $r$ = Periodic monthly interest rate: $\frac{\text{Annual Nominal Rate}}{12 \times 100}$
- $n$ = Total loan duration in months

For interest-free loans ($r = 0$):
$$EMI = \frac{P}{n}$$

### 2. Month-by-Month Amortization
For each period $m \in [1, n]$:
- $\text{Interest}_m = \text{Opening Balance}_m \times r$
- $\text{Principal}_m = \min(\text{Scheduled EMI} - \text{Interest}_m, \text{Opening Balance}_m)$
- $\text{Total Principal}_m = \text{Principal}_m + \text{Prepayment}_m$
- $\text{Closing Balance}_m = \text{Opening Balance}_m - \text{Total Principal}_m$

### 3. Prepayment Restructuring Options
Given an outstanding balance $B_m$ after the regular EMI at month $m$, and a part-payment $A \le B_m$:
- **New Outstanding Principal**: $P_{\text{new}} = B_m - A$
- **Option A (Reduce EMI)**:
  - Remaining tenure is locked at $n - m$ months.
  - New EMI is recalculated:
    $$EMI_{\text{new}} = \frac{P_{\text{new}} \times r \times (1+r)^{n - m}}{(1+r)^{n - m} - 1}$$
- **Option B (Reduce Tenure)**:
  - EMI remains locked at $EMI_{\text{original}}$.
  - The higher principal portion accelerates amortization, retiring the loan in $n_{\text{revised}} < n$ months.

---

## 📂 Project Architecture

```
loan-emi-calculator/
│
├── app.py                      # Main Streamlit web application & routing
├── requirements.txt            # Project dependencies
├── README.md                   # Comprehensive documentation
├── config.py                   # Configuration constants, themes, and conventions
│
├── calculations/               # Independent financial computation engine
│   ├── __init__.py
│   ├── emi.py                  # Core reducing-balance & zero-interest EMI math
│   ├── amortization.py         # Full month-by-month amortization schedule builder
│   ├── part_payment.py         # Option A, Option B, recurring prepayments & foreclosure
│   ├── interest.py             # Reducing balance interest calculation & date helpers
│   └── comparison.py           # Scenario aggregator & comparative metrics
│
├── components/                 # Streamlit UI visual components
│   ├── __init__.py
│   ├── dashboard.py            # Financial dashboard & executive summary cards
│   ├── charts.py               # Interactive Plotly chart builders
│   ├── tables.py               # Filterable amortization & comparison tables
│   ├── sidebar.py              # Navigation and input controls
│   └── reports.py              # Export center & statement downloads
│
├── utils/                      # Helper utilities
│   ├── __init__.py
│   ├── formatting.py           # Indian currency (₹ Lakhs/Crores) and date formatting
│   ├── validation.py           # Domain boundary validation & error handlers
│   └── export.py               # Excel (.xlsx) and ReportLab PDF (.pdf) generators
│
├── tests/                      # Automated Pytest suite
│   ├── __init__.py
│   ├── test_emi.py             # Standard, zero-interest, and boundary tests
│   ├── test_amortization.py    # Schedule conservation & zero final balance tests
│   ├── test_part_payment.py    # Prepayment, Option A/B, and foreclosure tests
│   ├── test_comparison.py      # Scenario comparison matrix tests
│   └── test_export.py          # Excel and PDF generation tests
│
└── exports/                    # Directory for local report storage
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.11 or Python 3.12+
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repo-url>
cd "emi cal"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run Automated Tests
Execute the full test suite to verify calculation precision:
```bash
pytest -v
```
*All 17 unit tests validate standard EMI, zero-interest cases, final EMI adjustments, full foreclosure, and strict parity between Option A and Option B.*

### 4. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Verification & Conservation Guarantees

Every amortization schedule generated adheres strictly to the following financial constraints:
1. **Conservation of Principal**: $\sum \text{Total Principal Repaid} \equiv \text{Original Loan Principal}$.
2. **Total Repayment Integrity**: $\text{Total Amount Repaid} \equiv \text{Principal} + \text{Total Interest Paid}$.
3. **Non-Negative Balances**: Closing balance never drops below zero at any point.
4. **Exact Zero Maturity**: Sub-cent rounding discrepancies are systematically absorbed in the final installment, yielding an exact closing balance of `₹ 0.00`.
5. **Prepayment Parity**: Both Option A and Option B share identical opening balances, interest, and principal amortization history up to the prepayment month.

---

## ⚖️ License & Disclaimer

This project is open-source and intended for personal and professional financial modeling. Actual settlement amounts with banking institutions may vary due to broken-period interest, loan processing fees, or lender-specific prepayment penalties.

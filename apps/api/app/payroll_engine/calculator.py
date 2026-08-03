from dataclasses import dataclass, field
from typing import Any


@dataclass
class PayrollCalculationResult:
    gross_salary: float
    total_earnings: float
    total_deductions: float
    net_salary: float
    earnings_breakdown: list[dict[str, Any]] = field(default_factory=list)
    deductions_breakdown: list[dict[str, Any]] = field(default_factory=list)


class PayrollCalculator:
    """Configurable enterprise payroll calculation engine."""

    @staticmethod
    def calculate_employee_payroll(
        monthly_ctc: float,
        overtime_hours: float = 0.0,
        unpaid_leave_days: float = 0.0,
        bonus_amount: float = 0.0,
        reimbursement_amount: float = 0.0,
        loan_emi: float = 0.0,
        tax_regime: str = "New",
    ) -> PayrollCalculationResult:
        if monthly_ctc <= 0:
            monthly_ctc = 3000.0  # Default baseline for calculation

        # 1. Base Components Structure
        basic = round(monthly_ctc * 0.50, 2)
        hra = round(basic * 0.40, 2)
        special_allowance = round(max(0.0, monthly_ctc - basic - hra), 2)

        # 2. Overtime Addition (1.5x hourly rate based on 160 standard monthly hours)
        hourly_rate = monthly_ctc / 160.0
        overtime_earnings = round(overtime_hours * hourly_rate * 1.5, 2)

        # 3. Loss of Pay (LOP) Deduction for unpaid leaves
        daily_rate = monthly_ctc / 30.0
        lop_deduction = round(unpaid_leave_days * daily_rate, 2)

        # 4. Total Gross Earnings
        total_earnings = round(
            basic + hra + special_allowance + overtime_earnings + bonus_amount + reimbursement_amount, 2
        )

        # 5. Statutory Deductions
        pf_deduction = round(basic * 0.12, 2)  # 12% PF contribution
        pt_deduction = 200.0 if monthly_ctc > 1500.0 else 0.0  # Professional Tax

        # 6. Income Tax Withholding (TDS Framework)
        taxable_monthly = max(0.0, total_earnings - pf_deduction)
        if tax_regime == "Old":
            income_tax = round(taxable_monthly * 0.15, 2) if taxable_monthly > 2500 else 0.0
        else:  # New Regime
            income_tax = round(taxable_monthly * 0.10, 2) if taxable_monthly > 2000 else 0.0

        # 7. Total Deductions
        total_deductions = round(
            pf_deduction + pt_deduction + income_tax + loan_emi + lop_deduction, 2
        )

        # 8. Net Payable Salary
        net_salary = round(max(0.0, total_earnings - total_deductions), 2)

        earnings_breakdown = [
            {"component_name": "Basic Pay", "earning_or_deduction": "earning", "amount": basic},
            {"component_name": "House Rent Allowance (HRA)", "earning_or_deduction": "earning", "amount": hra},
            {"component_name": "Special Allowance", "earning_or_deduction": "earning", "amount": special_allowance},
        ]
        if overtime_earnings > 0:
            earnings_breakdown.append(
                {"component_name": "Overtime Earnings", "earning_or_deduction": "earning", "amount": overtime_earnings}
            )
        if bonus_amount > 0:
            earnings_breakdown.append(
                {"component_name": "Bonus / Incentive", "earning_or_deduction": "earning", "amount": bonus_amount}
            )
        if reimbursement_amount > 0:
            earnings_breakdown.append(
                {"component_name": "Approved Reimbursement", "earning_or_deduction": "earning", "amount": reimbursement_amount}
            )

        deductions_breakdown = [
            {"component_name": "Provident Fund (PF)", "earning_or_deduction": "deduction", "amount": pf_deduction},
            {"component_name": "Professional Tax (PT)", "earning_or_deduction": "deduction", "amount": pt_deduction},
            {"component_name": "Income Tax (TDS)", "earning_or_deduction": "deduction", "amount": income_tax},
        ]
        if lop_deduction > 0:
            deductions_breakdown.append(
                {"component_name": "Loss of Pay (LOP)", "earning_or_deduction": "deduction", "amount": lop_deduction}
            )
        if loan_emi > 0:
            deductions_breakdown.append(
                {"component_name": "Loan EMI Deduction", "earning_or_deduction": "deduction", "amount": loan_emi}
            )

        return PayrollCalculationResult(
            gross_salary=total_earnings,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary,
            earnings_breakdown=earnings_breakdown,
            deductions_breakdown=deductions_breakdown,
        )

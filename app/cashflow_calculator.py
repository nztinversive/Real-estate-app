from datetime import datetime, timedelta
from .models import Income, Expense

def calculate_monthly_cashflow(property_id, start_date, end_date):
    incomes = Income.query.filter_by(property_id=property_id).filter(Income.date.between(start_date, end_date)).all()
    expenses = Expense.query.filter_by(property_id=property_id).filter(Expense.date.between(start_date, end_date)).all()

    total_income = sum(income.amount for income in incomes)
    total_expenses = sum(expense.amount for expense in expenses)

    return total_income - total_expenses

def calculate_annual_cashflow(property_id, year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    return calculate_monthly_cashflow(property_id, start_date, end_date)

def project_future_cashflow(property_id, years, income_growth_rate, expense_growth_rate):
    current_year = datetime.now().year
    projections = []

    for year in range(current_year, current_year + years):
        annual_cashflow = calculate_annual_cashflow(property_id, year)
        projections.append({
            'year': year,
            'cashflow': annual_cashflow
        })

        # Apply growth rates to incomes and expenses for the next year
        incomes = Income.query.filter_by(property_id=property_id).all()
        expenses = Expense.query.filter_by(property_id=property_id).all()

        for income in incomes:
            income.amount *= (1 + income_growth_rate)
        
        for expense in expenses:
            expense.amount *= (1 + expense_growth_rate)

    return projections
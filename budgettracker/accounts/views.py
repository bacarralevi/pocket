import calendar
import json
from django.http import JsonResponse # type: ignore
from django.core.serializers.json import DjangoJSONEncoder # type: ignore
from .models import Transaction, Category, Budget
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # type: ignore
from django.contrib.auth import login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.utils.safestring import mark_safe # type: ignore
from django.db.models import Sum # type: ignore
from datetime import datetime
from .forms import BudgetForm
from django.utils.dateparse import parse_date # type: ignore
from datetime import datetime
import csv
from django.http import HttpResponse # type: ignore


# Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # After successful registration, redirect to the login page
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to dashboard after successful login
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    # After logout, redirect to login page
    return redirect('login')


# Dashboard View
@login_required
def dashboard(request):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_name = datetime.now().strftime('%B')
    
    # Get days in the current month
    _, num_days = calendar.monthrange(current_year, current_month)
    
    # Calculate total income for the current month
    total_income = Transaction.objects.filter(
        user=request.user,
        type='Income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate total expenses for the current month
    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate the remaining balance
    remaining_balance = total_income - total_expenses
    
    # Pass the data to the template without chart data
    return render(request, 'accounts/dashboard.html', {
        'current_month_name': current_month_name,
        'current_year': current_year,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'days_in_month': num_days,
    })
    
# Chart data endpoint
@login_required
def dashboard_chart_data(request):
    view_type = request.GET.get('view', 'monthly')
    
    if view_type == 'yearly':
        return get_yearly_chart_data(request)
    else:
        return get_monthly_chart_data(request)

# Monthly chart data (daily breakdown)
def get_monthly_chart_data(request):
    # Get the requested month and year, defaulting to current if not provided
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
    except ValueError:
        # If invalid parameters are provided, use current date
        month = datetime.now().month
        year = datetime.now().year
    
    # Validate month range
    if month < 1 or month > 12:
        month = datetime.now().month
    
    # Get days in the selected month
    _, num_days = calendar.monthrange(year, month)
    
    # Get daily income and expense data for chart
    daily_data = []
    
    # Iterate through each day of the month
    for day in range(1, num_days + 1):
        current_date = datetime(year, month, day).date()
        
        # Get income for this day
        day_income = Transaction.objects.filter(
            user=request.user,
            type='Income',
            date=current_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get expenses for this day
        day_expenses = Transaction.objects.filter(
            user=request.user,
            type='Expense',
            date=current_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Add data for this day
        daily_data.append({
            'day': day,
            'income': float(day_income),
            'expenses': float(day_expenses)
        })
    
    # Return the data as JSON
    return JsonResponse(daily_data, safe=False)

# Yearly chart data (monthly breakdown)
def get_yearly_chart_data(request):
    # Get the requested year, defaulting to current if not provided
    try:
        year = int(request.GET.get('year', datetime.now().year))
    except ValueError:
        # If invalid parameter is provided, use current year
        year = datetime.now().year
    
    # Month names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Get monthly income and expense data for chart
    monthly_data = []
    
    # Iterate through each month of the year
    for month in range(1, 13):
        # Get income for this month
        month_income = Transaction.objects.filter(
            user=request.user,
            type='Income',
            date__month=month,
            date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get expenses for this month
        month_expenses = Transaction.objects.filter(
            user=request.user,
            type='Expense',
            date__month=month,
            date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Add data for this month
        monthly_data.append({
            'month': month_names[month-1],
            'income': float(month_income),
            'expenses': float(month_expenses)
        })
    
    # Return the data as JSON
    return JsonResponse(monthly_data, safe=False)


# Transactions View
@login_required
def transactions(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')
    categories = Category.objects.all()

    # # Get the current month and year
    # current_month = datetime.now().month
    # current_year = datetime.now().year

    # # Calculate total income for the current month
    # # total_income = Transaction.objects.filter(
    # #     user=request.user,
    # #     type='Income',
    # #     date__month=current_month,
    # #     date__year=current_year
    # # ).aggregate(Sum('amount'))['amount__sum'] or 0  # Use 0 if no income

    # # Calculate total expenses for the current month
    # total_expenses = Transaction.objects.filter(
    #     user=request.user,
    #     type='Expense',
    #     date__month=current_month,
    #     date__year=current_year
    # ).aggregate(Sum('amount'))['amount__sum'] or 0  # Use 0 if no expenses

    # # Calculate the remaining balance
    # remaining_balance = total_income - total_expenses

    return render(request, 'accounts/transactions.html', {
        'transactions': transactions,  # Changed from user_transactions to transactions
        # 'total_income': total_income,
        # 'total_expenses': total_expenses,
        # 'remaining_balance': remaining_balance,
    })


# Create Transaction View
@login_required
def create_transaction(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        type = request.POST.get('type')
        notes = request.POST.get('notes')
        category_id = request.POST.get('category')

        category = Category.objects.get(id=category_id) if category_id else None

        Transaction.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            date=date,
            type=type,
            notes=notes,
            category=category
        )

        return redirect('transactions')  # After saving, redirect to "My Transactions"

    return render(request, 'accounts/create_transaction.html', {'categories': categories})


# Edit Transaction View
@login_required
def edit_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.title = request.POST.get('title')
        transaction.amount = request.POST.get('amount')
        transaction.date = request.POST.get('date')
        transaction.type = request.POST.get('type')
        transaction.notes = request.POST.get('notes')
        transaction.save()

        return redirect('transactions')

    return render(request, 'accounts/edit_transaction.html', {'transaction': transaction})


# Delete Transaction View
@login_required
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        return redirect('transactions')

    return render(request, 'accounts/delete_transaction.html', {'transaction': transaction})



# Budget Page
@login_required
def set_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('transactions')
    else:
        form = BudgetForm()

    return render(request, 'accounts/set_budget.html', {'form': form})



# Export Transactions to CSV
def export_transactions_csv(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category_id')

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if category_id:
        transactions = transactions.filter(category__id=category_id)

    # Create the HttpResponse with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=transactions.csv'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Date', 'Type', 'Category', 'Notes'])

    for t in transactions:
        writer.writerow([
            t.title, t.amount, t.date, t.type, t.category.name if t.category else "", t.notes
        ])

    return response
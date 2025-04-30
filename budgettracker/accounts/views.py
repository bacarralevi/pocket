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
from django.shortcuts import get_object_or_404  # type: ignore
from django.contrib import messages # type: ignore


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


# Update the dashboard view to include budget information
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
    
    # Get budget information
    current_month_start = datetime(current_year, current_month, 1).date()
    
    # Get overall budget if it exists
    overall_budget = Budget.objects.filter(
        user=request.user,
        month__year=current_year,
        month__month=current_month,
        category__isnull=True
    ).first()
    
    # Get category budgets
    category_budgets = Budget.objects.filter(
        user=request.user,
        month__year=current_year,
        month__month=current_month,
        category__isnull=False
    ).select_related('category')
    
    # Get expense by category for the current month
    expenses_by_category = Transaction.objects.filter(
        user=request.user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    ).values('category').annotate(total=Sum('amount'))
    
    # Convert to a dictionary for easier lookup
    category_expenses = {}
    for expense in expenses_by_category:
        category_id = expense['category']
        if category_id:  # Skip None categories
            category_expenses[category_id] = expense['total']
    
    # Calculate budget status
    budget_status = {
        'has_budget': bool(overall_budget or category_budgets),
        'overall': {
            'amount': overall_budget.amount if overall_budget else 0,
            'spent': total_expenses,
            'remaining': (overall_budget.amount - total_expenses) if overall_budget else 0,
            'percentage': (total_expenses / overall_budget.amount * 100) if overall_budget and overall_budget.amount > 0 else 0,
            'status': get_budget_status(total_expenses, overall_budget.amount if overall_budget else 0)
        },
        'categories': []
    }
    
    # Process category budgets
    for budget in category_budgets:
        spent = category_expenses.get(budget.category.id, 0)
        remaining = budget.amount - spent
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        status = get_budget_status(spent, budget.amount)
        
        budget_status['categories'].append({
            'name': budget.category.name,
            'amount': budget.amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': status
        })
    
    # Pass the data to the template
    return render(request, 'accounts/dashboard.html', {
        'current_month_name': current_month_name,
        'current_year': current_year,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
        'days_in_month': num_days,
        'budget_status': budget_status
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

# Category chart data endpoint
@login_required
def category_chart_data(request):
    # Get the requested month and year
    try:
        month = request.GET.get('month')
        year = int(request.GET.get('year', datetime.now().year))
        
        # Convert month to integer if provided
        if month:
            month = int(month)
    except ValueError:
        # If invalid parameters are provided, use current date
        month = None
        year = datetime.now().year
    
    # Get expense data by category
    category_data = []
    
    # Build the query filter
    filter_args = {
        'user': request.user,
        'type': 'Expense',
        'date__year': year
    }
    
    # Add month filter if specified
    if month:
        filter_args['date__month'] = month
    
    # Get all the categories that have expenses
    expenses_by_category = Transaction.objects.filter(**filter_args).values(
        'category__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Process results - handle transactions without categories
    for expense in expenses_by_category:
        category_name = expense['category__name'] or 'Uncategorized'
        category_data.append({
            'category': category_name,
            'amount': float(expense['total'])
        })
    
    # Return the data as JSON
    return JsonResponse(category_data, safe=False)

# Updated transactions view with budget warnings
@login_required
def transactions(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    categories = Category.objects.all()
    
    # Get filter parameters from request
    search_term = request.GET.get('search_term', '')
    type_filter = request.GET.get('type_filter', '')
    category_filter = request.GET.get('category_filter', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Apply filters if provided
    if search_term:
        # Search in title and notes
        transactions = transactions.filter(title__icontains=search_term) | transactions.filter(notes__icontains=search_term)
    
    if type_filter:
        transactions = transactions.filter(type=type_filter)
    
    if category_filter:
        transactions = transactions.filter(category_id=category_filter)
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    # Order by date, newest first
    transactions = transactions.order_by('-date')
    
    # Get current month budget warnings
    budget_warnings = []
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get total expenses for the current month
    total_expenses = Transaction.objects.filter(
        user=user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Check overall budget
    overall_budget = Budget.objects.filter(
        user=user,
        month__year=current_year,
        month__month=current_month,
        category__isnull=True
    ).first()
    
    if overall_budget:
        percentage = (total_expenses / overall_budget.amount * 100) if overall_budget.amount > 0 else 0
        status = get_budget_status(total_expenses, overall_budget.amount)
        
        if status in ['warning', 'exceeded']:
            budget_warnings.append({
                'type': 'overall',
                'amount': overall_budget.amount,
                'spent': total_expenses,
                'percentage': percentage,
                'status': status
            })
    
    # Check category budgets
    category_budgets = Budget.objects.filter(
        user=user,
        month__year=current_year,
        month__month=current_month,
        category__isnull=False
    ).select_related('category')
    
    # Get expense by category for the current month
    expenses_by_category = Transaction.objects.filter(
        user=user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    ).values('category').annotate(total=Sum('amount'))
    
    # Convert to a dictionary for easier lookup
    category_expenses = {}
    for expense in expenses_by_category:
        category_id = expense['category']
        if category_id:  # Skip None categories
            category_expenses[category_id] = expense['total']
    
    # Check each category budget
    for budget in category_budgets:
        spent = category_expenses.get(budget.category.id, 0)
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        status = get_budget_status(spent, budget.amount)
        
        if status in ['warning', 'exceeded']:
            budget_warnings.append({
                'type': 'category',
                'category': budget.category.name,
                'amount': budget.amount,
                'spent': spent,
                'percentage': percentage,
                'status': status
            })
    
    return render(request, 'accounts/transactions.html', {
        'transactions': transactions,
        'categories': categories,
        'search_term': search_term,
        'type_filter': type_filter,
        'category_filter': category_filter,
        'start_date': start_date,
        'end_date': end_date,
        'budget_warnings': budget_warnings
    })
    
# Create Transaction View
@login_required
def create_transaction(request):
    # Get all categories and order them so that "Others..." appears last
    regular_categories = Category.objects.exclude(name="Others...").order_by('name')
    others_category = Category.objects.filter(name="Others...").first()
    
    # Combine the querysets
    if others_category:
        # Convert querysets to lists for manipulation
        categories_list = list(regular_categories)
        # Append "Others..." category at the end
        categories_list.append(others_category)
        categories = categories_list
    else:
        categories = regular_categories
    
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
    
    # Get all categories and order them so that "Others..." appears last
    regular_categories = Category.objects.exclude(name="Others...").order_by('name')
    others_category = Category.objects.filter(name="Others...").first()
    
    # Combine the querysets
    if others_category:
        # Convert querysets to lists for manipulation
        categories_list = list(regular_categories)
        # Append "Others..." category at the end
        categories_list.append(others_category)
        categories = categories_list
    else:
        categories = regular_categories

    if request.method == 'POST':
        transaction.title = request.POST.get('title')
        transaction.amount = request.POST.get('amount')
        transaction.date = request.POST.get('date')
        transaction.type = request.POST.get('type')
        transaction.notes = request.POST.get('notes')
        
        category_id = request.POST.get('category')
        transaction.category = Category.objects.get(id=category_id) if category_id else None
            
        transaction.save()

        return redirect('transactions')

    return render(request, 'accounts/edit_transaction.html', {
        'transaction': transaction,
        'categories': categories
    })

# Delete Transaction View
@login_required
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        return redirect('transactions')

    return render(request, 'accounts/delete_transaction.html', {'transaction': transaction})



# Budget Views
@login_required
def set_budget(request):
    # Get the user's existing budgets
    existing_budgets = Budget.objects.filter(user=request.user).order_by('-month')
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            
            # Check if a budget already exists for this month and category
            month_date = form.cleaned_data['month_year']  # Now using month_year from the form
            category = form.cleaned_data['category']
            
            # Try to find an existing budget for the same month and category
            try:
                existing_budget = Budget.objects.get(
                    user=request.user,
                    month__year=month_date.year,
                    month__month=month_date.month,
                    category=category
                )
                # Update the existing budget
                existing_budget.amount = form.cleaned_data['amount']
                existing_budget.save()
                messages.success(request, "Budget updated successfully!")
            except Budget.DoesNotExist:
                # Create a new budget
                budget.save()
                messages.success(request, "Budget created successfully!")
                
            return redirect('set_budget')
    else:
        form = BudgetForm(user=request.user)

    return render(request, 'accounts/set_budget.html', {
        'form': form,
        'existing_budgets': existing_budgets
    })

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully!")
            return redirect('set_budget')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    return render(request, 'accounts/edit_budget.html', {
        'form': form,
        'budget': budget
    })

@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget deleted successfully!")
        return redirect('set_budget')
    
    return render(request, 'accounts/delete_budget.html', {
        'budget': budget
    })
    
# Helper function to determine budget status
def get_budget_status(spent, budget_amount):
    if budget_amount <= 0:
        return 'no-budget'
    
    percentage = (spent / budget_amount) * 100
    
    if percentage < 80:
        return 'normal'
    elif percentage < 100:
        return 'warning'
    else:
        return 'exceeded'


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
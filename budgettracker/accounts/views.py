from .models import Transaction, Category
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime


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

    # Calculate total income for the current month
    total_income = Transaction.objects.filter(
        user=request.user,
        type='Income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0  # Use 0 if no income

    # Calculate total expenses for the current month
    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0  # Use 0 if no expenses

    # Calculate the remaining balance
    remaining_balance = total_income - total_expenses

    # Pass the totals and remaining balance to the template
    return render(request, 'accounts/dashboard.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_balance': remaining_balance,
    })


# Transactions View
@login_required
def transactions(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    return render(request, 'accounts/transactions.html', {'transactions': user_transactions})


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

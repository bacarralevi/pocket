from .models import Transaction
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

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
    return render(request, 'accounts/dashboard.html')


# Transactions View
@login_required
def transactions(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    return render(request, 'accounts/transactions.html', {'transactions': user_transactions})


# Create Transaction View
@login_required
def create_transaction(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        type = request.POST.get('type')
        notes = request.POST.get('notes')

        Transaction.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            date=date,
            type=type,
            notes=notes
        )

        return redirect('transactions')  # After saving, redirect to "My Transactions"

    return render(request, 'accounts/create_transaction.html')


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

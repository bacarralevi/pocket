# accounts/admin.py

from django.contrib import admin
from .models import Transaction, Category  # Import Category

admin.site.register(Transaction)
admin.site.register(Category)  

# accounts/admin.py

from django.contrib import admin
from .models import Transaction, Category, Budget  # Import Category

admin.site.register(Transaction)
admin.site.register(Category)  
admin.site.register(Budget)
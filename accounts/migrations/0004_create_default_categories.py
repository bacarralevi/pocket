# accounts/migrations/XXXX_create_default_categories.py

from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('accounts', 'Category')
    
    # List of default categories
    default_categories = [
        'Housing', 'Food', 'Transportation', 'Utilities', 
        'Healthcare', 'Entertainment', 'Shopping', 'Education',
        'Personal Care', 'Investments', 'Debt', 'Gifts',
        'Groceries', 'Restaurants', 'Travel', 'Subscriptions','Others...'
    ]
    
    # Create each category if it doesn't exist
    for category_name in default_categories:
        Category.objects.get_or_create(name=category_name)

def reverse_func(apps, schema_editor):
    # This migration is not meant to be reversible
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_category_transaction_category'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, reverse_func),
    ]
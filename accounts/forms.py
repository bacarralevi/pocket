from django import forms
from django.utils import timezone
from .models import Budget, Category
import datetime

class BudgetForm(forms.ModelForm):
    # Add a custom month field
    month_year = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'month', 'class': 'form-control'}),
        required=True,
        help_text="Budget month and year"
    )
    
    class Meta:
        model = Budget
        fields = ['category', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(BudgetForm, self).__init__(*args, **kwargs)
        
        # If we're editing an existing budget, set the month_year field based on the instance's month
        if self.instance.pk and self.instance.month:
            self.fields['month_year'].initial = self.instance.month.strftime('%Y-%m')
        else:
            # Set default month to the first day of current month
            today = timezone.now()
            self.fields['month_year'].initial = today.strftime('%Y-%m')
        
        # Add an option for "Overall Budget" (no specific category)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "Overall Budget (All Categories)"
        
        # Add help text
        self.fields['category'].help_text = "Select a category or leave blank for an overall budget"
        self.fields['amount'].help_text = "Maximum amount to spend in this category per month"
    
    def clean_month_year(self):
        """Convert month-year string to a date object (first day of the month)"""
        month_year = self.cleaned_data.get('month_year')
        if not month_year:
            raise forms.ValidationError("Please select a month and year")
        
        try:
            # Parse the YYYY-MM format from the month input
            year, month = map(int, month_year.split('-'))
            # Create a date object for the first day of the month
            date_obj = datetime.date(year, month, 1)
            return date_obj
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid month format. Please use the month picker.")
    
    def save(self, commit=True):
        """Override the save method to set the month field from month_year"""
        budget = super(BudgetForm, self).save(commit=False)
        budget.month = self.cleaned_data.get('month_year')
        
        if commit:
            budget.save()
        return budget
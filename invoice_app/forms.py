from django import forms
from .models import Invoice, InvoiceItem, Customer, Product

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_type', 'customer', 'discount', 'logo']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']

class HospitalInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'discount', 'logo']  # Customer here is the Patient

class HospitalInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity'] 

class StationeryInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'discount', 'logo']  # Customer = Stationery Buyer

class StationeryInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']  # Product = Stationery Item


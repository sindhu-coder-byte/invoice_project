from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    gstin = models.CharField(max_length=15, blank=True, null=True)
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    tax = models.FloatField(default=0)  # e.g., 5 for 5%
    sku = models.CharField(max_length=50, blank=True, null=True)
    
class Invoice(models.Model):
    INVOICE_TYPE = [
        ('SHOP', 'Shopping'),
        ('HOSP', 'Hospital'),
        ('STAT', 'Stationery')
    ]
    invoice_type = models.CharField(max_length=5, choices=INVOICE_TYPE)
    invoice_no = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    discount = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    tax = models.FloatField(default=0)
    total = models.FloatField()





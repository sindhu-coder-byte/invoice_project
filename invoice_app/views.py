from django.shortcuts import render, redirect, get_object_or_404
from .forms import InvoiceForm, HospitalInvoiceForm, StationeryInvoiceForm
from .models import Invoice, InvoiceItem, Product, Customer
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth import logout

# -------------------------------
# Helper Functions
# -------------------------------

def get_invoice_number(invoice_type):
    """Generate the next invoice number for a given type."""
    last_invoice = Invoice.objects.filter(invoice_type=invoice_type).order_by('-id').first()
    next_id = (last_invoice.id + 1) if last_invoice else 1
    return f"{invoice_type[:4].upper()}-{next_id:03d}"

# -------------------------------
# Dashboard
# -------------------------------

def dashboard(request):
    total_customers = Customer.objects.count()
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(total_amount__gte=0).count()  # example
    unpaid_invoices = total_invoices - paid_invoices
    return render(request, 'invoice/dashboard.html', {
        'total_customers': total_customers,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices
    })

# -------------------------------
# Invoice Views
# -------------------------------

def create_invoice(request, invoice_type):
    """Generic invoice creation for shopping, hospital, and stationery."""
    form_mapping = {
        'shopping': InvoiceForm,
        'hospital': HospitalInvoiceForm,
        'stationery': StationeryInvoiceForm
    }
    form_class = form_mapping.get(invoice_type)
    if not form_class:
        return HttpResponse("Invalid invoice type")

    products = Product.objects.all()  # ✅ Always defined here

    if request.method == 'POST':
        invoice_form = form_class(request.POST, request.FILES)
        items_data = request.POST.getlist('product')
        qty_data = request.POST.getlist('quantity')

        if invoice_form.is_valid():
            invoice = invoice_form.save(commit=False)
            invoice.invoice_type = invoice_type.upper()[:4]
            invoice.invoice_no = get_invoice_number(invoice_type)
            invoice.save()

            total_amount = 0
            for product_id, qty in zip(items_data, qty_data):
                try:
                    product = Product.objects.get(id=product_id)
                    qty = int(qty)
                    total = (product.price * qty) + (product.price * qty * product.tax / 100)
                    total_amount += total
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=qty,
                        price=product.price,
                        tax=product.tax,
                        total=total
                    )
                except Product.DoesNotExist:
                    continue

            invoice.total_amount = total_amount - (invoice.discount or 0)
            invoice.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        invoice_form = form_class()

    return render(request, f'invoice/{invoice_type}_invoice_form.html', {
        'invoice_form': invoice_form,
        'products': products
    })



def create_shopping_invoice(request):
    return create_invoice(request, invoice_type='shopping')


def create_hospital_invoice(request):
    return create_invoice(request, invoice_type='hospital')


def create_stationery_invoice(request):
    return create_invoice(request, invoice_type='stationery')


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    return render(request, 'invoice/invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    template_path = 'invoice/invoice_pdf.html'
    context = {'invoice': invoice, 'items': items}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice_{invoice.invoice_no}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')
    return response

# -------------------------------
# Customer, Product, Invoice Lists
# -------------------------------


def pricing(request):
    return render(request, 'invoice/pricing.html')


# -------------------------------
# User Logout
# -------------------------------

def user_logout(request):
    logout(request)
    return redirect('dashboard')

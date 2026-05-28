import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import logout

from weasyprint import HTML, CSS

from .forms import InvoiceForm, HospitalInvoiceForm, StationeryInvoiceForm
from .models import Invoice, InvoiceItem, Product, Customer

# -------------------------------
# Helpers
# -------------------------------
def get_invoice_number(invoice_type):
    type_code = invoice_type[:4].upper()
    last_invoice = Invoice.objects.filter(invoice_type=type_code).order_by('-id').first()
    next_id = (last_invoice.id + 1) if last_invoice else 1
    return f"{type_code}-{next_id:03d}"

def get_template_name(template_choice):
    template_map = {
        "classic": "invoice/invoice_pdf_classic.html",
        "modern":  "invoice/invoice_pdf_modern.html",
        "minimal": "invoice/invoice_pdf_minimal.html",
    }
    return template_map.get(template_choice, "invoice/invoice_pdf_classic.html")

def compute_totals(items, discount=0):
    subtotal   = sum((item.price or 0) * (item.quantity or 0) for item in items)
    total_tax  = sum(((item.price or 0) * (item.quantity or 0) * ((item.tax or 0) / 100.0)) for item in items)
    total_amount = subtotal + total_tax - (discount or 0)
    return round(subtotal, 2), round(total_tax, 2), round(total_amount, 2)

# -------------------------------
# Dashboard
# -------------------------------
def dashboard(request):
    recent_invoices = Invoice.objects.select_related('customer').order_by('-id')[:10]
    return render(request, 'invoice/dashboard.html', {
        'total_customers': Customer.objects.count(),
        'total_invoices':  Invoice.objects.count(),
        'recent_invoices': recent_invoices,
    })

# -------------------------------
# Invoice creation views
# -------------------------------
def create_shopping_invoice(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    return render(request, "invoice/shopping_invoice_form.html", {"form": form})

def create_hospital_invoice(request):
    if request.method == "POST":
        form = HospitalInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = HospitalInvoiceForm()
    return render(request, "invoice/hospital_invoice_form.html", {"form": form})

def create_stationery_invoice(request):
    if request.method == "POST":
        form = StationeryInvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = form.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = StationeryInvoiceForm()
    return render(request, "invoice/stationery_invoice_form.html", {"form": form})

def create_invoice(request, invoice_type):
    form_mapping = {
        'shopping':   InvoiceForm,
        'hospital':   HospitalInvoiceForm,
        'stationery': StationeryInvoiceForm,
    }
    form_class = form_mapping.get(invoice_type)
    if not form_class:
        return HttpResponse("Invalid invoice type", status=400)

    products = Product.objects.all()

    if request.method == 'POST':
        invoice_form = form_class(request.POST, request.FILES)
        items_data = request.POST.getlist('product')
        qty_data   = request.POST.getlist('quantity')

        if invoice_form.is_valid():
            invoice = invoice_form.save(commit=False)
            invoice.invoice_type = invoice_type[:4].upper()
            invoice.invoice_no   = get_invoice_number(invoice_type)
            invoice.save()

            created_items = []
            for product_id, qty in zip(items_data, qty_data):
                try:
                    product = Product.objects.get(id=product_id)
                    qty_int = int(qty)
                    total   = (product.price * qty_int) + (product.price * qty_int * product.tax / 100)
                    item    = InvoiceItem.objects.create(
                        invoice=invoice, product=product,
                        quantity=qty_int, price=product.price,
                        tax=product.tax, total=total,
                    )
                    created_items.append(item)
                except (Product.DoesNotExist, ValueError):
                    continue

            subtotal, total_tax, grand_total = compute_totals(created_items, invoice.discount)
            invoice.subtotal      = subtotal
            invoice.tax           = total_tax
            invoice.total_amount  = grand_total
            invoice.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        invoice_form = form_class()

    return render(request, f'invoice/{invoice_type}_invoice_form.html', {
        'invoice_form': invoice_form,
        'products': products,
    })

# -------------------------------
# Invoice detail
# -------------------------------
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items   = invoice.items.select_related('product').all()
    subtotal, total_tax, total_amount = compute_totals(items, invoice.discount)
    return render(request, 'invoice/invoice_detail.html', {
        'invoice':       invoice,
        'items':         items,
        'subtotal':      subtotal,
        'total_tax':     total_tax,
        'total_amount':  total_amount,
    })

# -------------------------------
# PDF generation (WeasyPrint)
# -------------------------------
def invoice_pdf(request, invoice_id):
    invoice          = get_object_or_404(Invoice, id=invoice_id)
    template_choice  = request.GET.get("style", "classic")
    template_name    = get_template_name(template_choice)

    items = invoice.items.select_related('product').all()
    subtotal, total_tax, total_amount = compute_totals(items, invoice.discount)

    html_string = render_to_string(template_name, {
        "invoice":      invoice,
        "items":        items,
        "subtotal":     subtotal,
        "total_tax":    total_tax,
        "total_amount": total_amount,
    })

    html     = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    action   = request.GET.get("action", "download")
    response = HttpResponse(pdf_file, content_type='application/pdf')
    disp     = "inline" if action == "preview" else "attachment"
    response['Content-Disposition'] = f'{disp}; filename="invoice_{invoice.invoice_no}.pdf"'
    return response

# -------------------------------
# Invoice preview (server-rendered)
# -------------------------------
def invoice_preview(request, pk, template="classic"):
    invoice         = get_object_or_404(Invoice, pk=pk)
    items           = invoice.items.select_related('product').all()
    template_choice = request.GET.get("style", template)
    template_name   = get_template_name(template_choice)

    subtotal, total_tax, total_amount = compute_totals(items, invoice.discount)
    return render(request, template_name, {
        "invoice":      invoice,
        "items":        items,
        "subtotal":     subtotal,
        "total_tax":    total_tax,
        "total_amount": total_amount,
    })

# -------------------------------
# Pricing
# -------------------------------
def pricing(request):
    return render(request, 'invoice/pricing.html')

# -------------------------------
# Logout
# -------------------------------
def user_logout(request):
    logout(request)
    return redirect('dashboard')

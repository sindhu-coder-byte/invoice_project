from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Invoices
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),

    # Create invoice - dynamic URL
    path('invoice/create/<str:invoice_type>/', views.create_invoice, name='create_invoice_type'),

    # Optional separate URLs
    path('shopping_invoice/', views.create_shopping_invoice, name='create_shopping_invoice'),
    path('hospital_invoice/', views.create_hospital_invoice, name='create_hospital_invoice'),
    path('stationery_invoice/', views.create_stationery_invoice, name='create_stationery_invoice'),

    # Pricing & Preview
    path('pricing/', views.pricing, name='pricing'),
    path("invoice/<int:pk>/preview/<str:template>/", views.invoice_preview, name="invoice_preview"),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

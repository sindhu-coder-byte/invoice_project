from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # for default logout if needed

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),


    # Invoices
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/pdf/', views.download_invoice_pdf, name='download_invoice_pdf'),

    # Create invoice - dynamic URL
    path('invoice/create/<str:invoice_type>/', views.create_invoice, name='create_invoice_type'),

    # Optional separate URLs (if you want shortcut links)
    path('shopping_invoice/', views.create_shopping_invoice, name='create_shopping_invoice'),
    path('hospital_invoice/', views.create_hospital_invoice, name='create_hospital_invoice'),
    path('stationery_invoice/', views.create_stationery_invoice, name='create_stationery_invoice'),
    path('pricing/', views.pricing, name='pricing'),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

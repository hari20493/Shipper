from django.contrib.auth.decorators import login_required
from django.urls import path

from dashboard.views import LoginView, logout_dashboard, DashboardView, CustomerAddView, CustomerView, ShipmentAddView, \
    ShipmentView, shipment_details, change_shipment_status, TrackShipmentView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_dashboard, name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('customer-add/', CustomerAddView.as_view(), name='customer-add'),
    path('customer/', CustomerView.as_view(), name='customer'),
    path('shipment-add/', ShipmentAddView.as_view(), name='shipment-add'),
    path('shipment/', ShipmentView.as_view(), name='shipment'),
    path('shipment-details/<int:shipment_id>', shipment_details, name='shipment-details'),
    path('change-status/<str:shipment_code>/<str:status>', change_shipment_status,
         name='shipment-change-status'),
    path('track/<str:shipment_code>/', TrackShipmentView.as_view(), name='track-shipment'),

]

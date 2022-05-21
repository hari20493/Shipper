from django.contrib import admin

# Register your models here.
from dashboard.models import Customer, Shipment, ShipmentStatus

admin.site.site_header = "Shipping Management"
admin.site.site_title = "Shipping Management"

admin.site.register(Customer)
admin.site.register(Shipment)
admin.site.register(ShipmentStatus)

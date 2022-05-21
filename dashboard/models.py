from django.contrib.auth.models import User
from django.db import models

shipment_status = (
    ('pending', 'Pending'),
    ('sending', 'Sending'),
    ('received', 'Received'),
)


# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    shipping_code = models.CharField(max_length=200, null=True)
    weight = models.FloatField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    shipment_current_status = models.CharField(max_length=200, choices=shipment_status, default='pending')
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def get_shipment_details(self):
        status_last_updated = ShipmentStatus.objects.filter(shipment=self).order_by('-created_date')[0]
        return {
            'shipping_code': self.shipping_code,
            'weight': self.weight,
            'customer': self.customer.name,
            'shipment_current_status': self.shipment_current_status,
            'created_date': self.created_date.strftime('%d-%m-%Y %H:%M:%S'),
            'last_updated_date': status_last_updated.created_date.strftime('%d %B, %Y %H:%M:%S'),
        }

    def __str__(self):
        return self.shipping_code


class ShipmentStatus(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=200, null=True, choices=shipment_status)
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def change_status(self, status):
        ShipmentStatus.objects.create(shipment=self.shipment, status=status)
        self.shipment.shipment_current_status = status
        self.shipment.save()
        status_dict = {"status": self.shipment.shipment_current_status}
        return status_dict

    def __str__(self):
        return self.status

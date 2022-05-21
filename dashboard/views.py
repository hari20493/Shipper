from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Min
from django.http import JsonResponse
from django.shortcuts import redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from django.contrib.auth.mixins import UserPassesTestMixin

from dashboard.models import Customer, Shipment, ShipmentStatus
import random


def generate_shipment_code():
    return 'SHIP-MY-STUFF' + str(Shipment.objects.count() + 1) + '-' + str(random.randint(100, 999))


class SuperUserCheck(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser


class LoginView(TemplateView):
    template_name = 'dashboard/login.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(LoginView, self).dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))

        return context

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username != '' and password != '':
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('dashboard'))
            else:
                messages.error(request, 'Invalid username or password')
                return redirect(reverse('login'))


def logout_dashboard(request):
    logout(request)
    return redirect(reverse('login'))


class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(DashboardView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return context

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['title'] = 'Dashboard'
        context['active_menu'] = 'dashboard'
        if self.request.user.is_superuser:
            customers_count = Customer.objects.count()
            shipments = Shipment.objects.all()
            shipments_count = shipments.count()
            pending_shipments_count = Shipment.objects.filter(shipment_current_status='pending',
                                                              ).count()

            received_shipments_count = Shipment.objects.filter(shipment_current_status='received',
                                                               ).count()

            context['customers_count'] = customers_count
        else:
            shipments = Shipment.objects.filter(customer__admin_user=self.request.user)
            shipments_count = shipments.count()
            pending_shipments_count = Shipment.objects.filter(shipment_current_status='pending',
                                                              customer__admin_user=self.request.user).count()
            sending_shipments_count = Shipment.objects.filter(shipment_current_status='sending',
                                                              customer__admin_user=self.request.user).count()
            received_shipments_count = Shipment.objects.filter(shipment_current_status='received',
                                                               customer__admin_user=self.request.user).count()
            context['sent_shipments_count'] = sending_shipments_count
            delivered_orders = ShipmentStatus.objects.filter(status='received',
                                                             shipment__customer__admin_user=self.request.user).values(
                'created_date__date').annotate(count=Count('created_date__date'))
            dates_list = []
            count_list = []
            for delivered_order in delivered_orders:
                dates_list.append(delivered_order['created_date__date'].strftime('%d-%m-%Y'))
                count_list.append(delivered_order['count'])
            context['delivered_orders_dates'] = str(dates_list)
            context['delivered_orders_count'] = count_list

        context['shipments_count'] = shipments_count
        context['pending_shipments_count'] = pending_shipments_count
        context['received_shipments_count'] = received_shipments_count
        context['totalshipments_count'] = pending_shipments_count + received_shipments_count
        context['shipments'] = shipments
        return context


class CustomerAddView(SuperUserCheck, TemplateView):
    template_name = 'dashboard/customer_add.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(CustomerAddView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return context

    def get_context_data(self, **kwargs):
        context = super(CustomerAddView, self).get_context_data(**kwargs)
        context['title'] = 'Customer'
        context['active_menu'] = 'customer-add'
        return context

    def post(self, request):
        name = request.POST.get('name', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        if name != '' and username != '' and password != '' and email != '':
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            if Customer.objects.filter(name=name).exists():
                messages.error(request, 'Customer already exists')
                return redirect(reverse('customer-add'))
            else:
                Customer.objects.create(name=name, admin_user=user)

            return redirect(reverse('customer'))
        else:
            messages.error(request, 'Please fill all the fields')
            return redirect(reverse('customer-add'))


class CustomerView(SuperUserCheck, TemplateView):
    template_name = 'dashboard/customer.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(CustomerView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return context

    def get_context_data(self, **kwargs):
        context = super(CustomerView, self).get_context_data(**kwargs)
        context['title'] = 'Customer'
        context['active_menu'] = 'customer'
        context['customers'] = Customer.objects.all()
        return context


class ShipmentAddView(SuperUserCheck, TemplateView):
    template_name = 'dashboard/shipment_add.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(ShipmentAddView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return context

    def get_context_data(self, **kwargs):
        context = super(ShipmentAddView, self).get_context_data(**kwargs)
        context['title'] = 'Shipment'
        context['active_menu'] = 'shipment-add'
        context['shipment_code'] = generate_shipment_code()
        context['customers'] = Customer.objects.all()
        return context

    def post(self, request):
        code = request.POST.get('code', '')
        weight = request.POST.get('weight', '')
        customer = request.POST.get('customer', '')

        if code != '' and weight != '' and customer != '':
            if Shipment.objects.filter(shipping_code=code).exists():
                messages.error(request, 'Shipment already exists')
                return redirect(reverse('shipment-add'))
            else:
                try:
                    customer_obj = Customer.objects.get(id=customer)
                    shipment_obj = Shipment.objects.create(shipping_code=code, weight=weight, customer=customer_obj)
                    ShipmentStatus.objects.create(shipment=shipment_obj, status='pending')
                except:
                    messages.error(request, 'Invalid customer')
                    return redirect(reverse('shipment-add'))
                return redirect(reverse('shipment'))
        else:
            messages.error(request, 'Please fill all the fields')
            return redirect(reverse('shipment-add'))


class ShipmentView(TemplateView):
    template_name = 'dashboard/shipment.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(ShipmentView, self).dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return context

    def get_context_data(self, **kwargs):
        context = super(ShipmentView, self).get_context_data(**kwargs)
        context['title'] = 'Shipment'
        context['active_menu'] = 'shipments'
        if self.request.user.is_superuser:
            context['shipments'] = Shipment.objects.all()
        else:
            print(Shipment.objects.filter(customer__admin_user=self.request.user))
            context['shipments'] = Shipment.objects.filter(customer__admin_user=self.request.user)
        return context


class TrackShipmentView(TemplateView):
    template_name = 'dashboard/track_shipment.html'

    def dispatch(self, request, *args, **kwargs):
        context = super(TrackShipmentView, self).dispatch(request, *args, **kwargs)
        return context

    def get_context_data(self, **kwargs):
        context = super(TrackShipmentView, self).get_context_data(**kwargs)
        context['title'] = 'Track Shipment'
        context['active_menu'] = 'track-shipment'
        context['nosidebar'] = True
        shipment_code = kwargs.get('shipment_code', '')
        if shipment_code != '':
            shipment_obj = Shipment.objects.filter(shipping_code=shipment_code).first()
            if shipment_obj:
                context['shipment'] = shipment_obj.get_shipment_details()
                context['shipment_status'] = ShipmentStatus.objects.filter(shipment=shipment_obj).order_by('-id')

        return context


def shipment_details(request, shipment_id):
    shipment = Shipment.objects.get(id=shipment_id).get_shipment_details()
    return JsonResponse(shipment)


def change_shipment_status(request, shipment_code, status):
    shipment = ShipmentStatus.objects.filter(shipment__shipping_code=shipment_code).first().change_status(status)
    return JsonResponse(shipment)

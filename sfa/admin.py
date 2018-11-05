from django.contrib import admin
from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
# Register your models here.
from .models import CustomerInfo, ContactInfo, AddressInfo


@admin.register(CustomerInfo)
class CustomerInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    pass

@admin.register(AddressInfo)
class AddressInfoAdmin(admin.ModelAdmin):
    pass

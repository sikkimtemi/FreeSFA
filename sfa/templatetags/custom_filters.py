from django import template
from django.template.defaultfilters import stringfilter
from sfa.models import CustomerInfo

register = template.Library()

@register.filter
@stringfilter
def is_editable(pk, email):
    customer_info = CustomerInfo.objects.get(pk=pk)
    return customer_info.is_editable(email)

from django.contrib import admin
from .models import Client, Contact, ServiceAgreement


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0


class ServiceAgreementInline(admin.TabularInline):
    model = ServiceAgreement
    extra = 0
    fields = ('name', 'start_date', 'end_date', 'is_active', 'billing_frequency')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'state', 'industry')
    search_fields = ('name', 'address', 'city', 'notes')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ContactInline, ServiceAgreementInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'phone', 'website')
        }),
        ('Additional Information', {
            'fields': ('industry', 'notes', 'stripe_customer_id')
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'client', 'email', 'phone', 'is_primary')
    list_filter = ('is_primary', 'client')
    search_fields = ('first_name', 'last_name', 'email', 'job_title')
    autocomplete_fields = ['client']


@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'start_date', 'end_date', 'is_active', 'billing_frequency')
    list_filter = ('is_active', 'billing_frequency', 'start_date')
    search_fields = ('name', 'description', 'notes')
    autocomplete_fields = ['client']
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': ('client', 'name', 'description', 'is_active')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Billing Information', {
            'fields': ('billing_frequency', 'billing_day', 'per_device_pricing', 'stripe_subscription_id')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )

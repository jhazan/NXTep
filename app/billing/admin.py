from django.contrib import admin
from .models import Quote, QuoteItem, Invoice, InvoiceItem, Payment


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'client', 'title', 'status', 'created_at', 'expiration_date', 'total')
    list_filter = ('status', 'created_at', 'expiration_date')
    search_fields = ('quote_number', 'title', 'client__name')
    readonly_fields = ('quote_number', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'total')
    fieldsets = (
        (None, {
            'fields': ('client', 'title', 'status', 'quote_number')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'expiration_date')
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_percent', 'tax_amount', 'total')
        }),
        ('Additional Information', {
            'fields': ('notes', 'terms')
        }),
    )
    inlines = [QuoteItemInline]


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total_price', 'device')
    readonly_fields = ('total_price',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('amount', 'payment_date', 'payment_method', 'reference_number')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'title', 'status', 'issue_date', 'due_date', 'total', 'balance_due')
    list_filter = ('status', 'issue_date', 'due_date', 'is_recurring')
    search_fields = ('invoice_number', 'title', 'client__name')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'total', 'balance_due')
    fieldsets = (
        (None, {
            'fields': ('client', 'service_agreement', 'title', 'status', 'invoice_number')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'issue_date', 'due_date')
        }),
        ('Recurring Information', {
            'fields': ('is_recurring', 'billing_period_start', 'billing_period_end')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_invoice_id', 'stripe_payment_intent_id')
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_percent', 'tax_amount', 'total', 'balance_due')
        }),
        ('Additional Information', {
            'fields': ('notes', 'payment_terms')
        }),
    )
    inlines = [InvoiceItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'reference_number')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('invoice__invoice_number', 'reference_number', 'notes')
    date_hierarchy = 'payment_date'

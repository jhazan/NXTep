from django.contrib import admin
from .models import DeviceType, Device, MonitoringResult, Alert


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_price')
    search_fields = ('name', 'description')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'device_type', 'ip_address', 'status', 'monitoring_enabled')
    list_filter = ('status', 'monitoring_enabled', 'device_type', 'client')
    search_fields = ('name', 'ip_address', 'hostname', 'notes')
    autocomplete_fields = ['client', 'device_type']
    fieldsets = (
        (None, {
            'fields': ('client', 'name', 'device_type', 'status')
        }),
        ('Network Information', {
            'fields': ('ip_address', 'mac_address', 'hostname')
        }),
        ('Monitoring Configuration', {
            'fields': ('monitoring_enabled', 'ping_check_enabled', 'snmp_check_enabled', 'snmp_community', 'snmp_port')
        }),
        ('Billing Information', {
            'fields': ('custom_price',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )


@admin.register(MonitoringResult)
class MonitoringResultAdmin(admin.ModelAdmin):
    list_display = ('device', 'check_time', 'ping_status', 'ping_latency', 'snmp_status', 'cpu_load')
    list_filter = ('ping_status', 'snmp_status', 'device')
    date_hierarchy = 'check_time'
    readonly_fields = ('device', 'check_time', 'ping_status', 'ping_latency', 'snmp_status', 'cpu_load', 'memory_used', 'disk_used')

    def has_add_permission(self, request):
        return False  # Prevent manual creation of results


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'device', 'severity', 'status', 'created_at')
    list_filter = ('severity', 'status', 'device__client')
    search_fields = ('title', 'message', 'device__name')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('device', 'title', 'message', 'severity', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'acknowledged_at', 'resolved_at')
        }),
    )
    readonly_fields = ('created_at',)

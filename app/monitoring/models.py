from django.db import models
from clients.models import Client, ServiceAgreement


class DeviceType(models.Model):
    """Model representing types of devices (server, workstation, switch, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.name


class Device(models.Model):
    """Model representing a monitored device."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('decommissioned', 'Decommissioned'),
    ]
    
    client = models.ForeignKey(Client, related_name='devices', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    device_type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True)
    hostname = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Device-specific pricing (if different from device type default)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # SNMP settings
    snmp_community = models.CharField(max_length=100, default='public', help_text="SNMP community string")
    snmp_port = models.IntegerField(default=161)
    
    # Monitoring settings
    monitoring_enabled = models.BooleanField(default=True)
    ping_check_enabled = models.BooleanField(default=True)
    snmp_check_enabled = models.BooleanField(default=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    @property
    def billing_price(self):
        """Returns the price to bill for this device"""
        if self.custom_price is not None:
            return self.custom_price
        elif self.device_type:
            return self.device_type.default_price
        return 0.00


class MonitoringResult(models.Model):
    """Model storing results of device monitoring checks."""
    STATUS_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('unreachable', 'Unreachable'),
        ('unknown', 'Unknown'),
    ]
    
    device = models.ForeignKey(Device, related_name='results', on_delete=models.CASCADE)
    check_time = models.DateTimeField(auto_now_add=True)
    ping_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    ping_latency = models.FloatField(null=True, blank=True)  # in milliseconds
    snmp_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    
    # SNMP metrics
    cpu_load = models.FloatField(null=True, blank=True)  # percentage
    memory_used = models.FloatField(null=True, blank=True)  # percentage
    disk_used = models.FloatField(null=True, blank=True)  # percentage
    
    class Meta:
        ordering = ['-check_time']
        
    def __str__(self):
        return f"{self.device.name} check at {self.check_time}"


class Alert(models.Model):
    """Model representing monitoring alerts."""
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    device = models.ForeignKey(Device, related_name='alerts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.severity} alert for {self.device.name}: {self.title}"

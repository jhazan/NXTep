import subprocess
import time
from datetime import datetime
from celery import shared_task
from pysnmp.hlapi import *
from django.utils import timezone

from .models import Device, MonitoringResult, Alert

@shared_task
def monitor_all_devices():
    """Task to monitor all active devices."""
    devices = Device.objects.filter(monitoring_enabled=True, status='active')
    for device in devices:
        check_device.delay(device.id)
    return f"Scheduled monitoring for {devices.count()} devices"

@shared_task
def check_device(device_id):
    """Task to check a specific device."""
    try:
        device = Device.objects.get(id=device_id)
        result = MonitoringResult(device=device)
        
        # Perform ping check if enabled
        if device.ping_check_enabled:
            ping_status, ping_latency = check_ping(device.ip_address)
            result.ping_status = ping_status
            result.ping_latency = ping_latency
            
            # Create alert for down devices
            if ping_status == 'down' and device.status == 'active':
                create_alert(
                    device=device,
                    title=f"Device {device.name} is down",
                    message=f"Ping check failed for {device.name} ({device.ip_address})",
                    severity='critical'
                )
        
        # Perform SNMP check if enabled and device is up
        if device.snmp_check_enabled and result.ping_status == 'up':
            snmp_status, metrics = check_snmp(device.ip_address, device.snmp_community, device.snmp_port)
            result.snmp_status = snmp_status
            
            if metrics:
                result.cpu_load = metrics.get('cpu_load')
                result.memory_used = metrics.get('memory_used')
                result.disk_used = metrics.get('disk_used')
                
                # Check for high resource usage
                if result.cpu_load and result.cpu_load > 90:
                    create_alert(
                        device=device,
                        title=f"High CPU usage on {device.name}",
                        message=f"CPU usage is at {result.cpu_load}%",
                        severity='warning'
                    )
                    
                if result.memory_used and result.memory_used > 90:
                    create_alert(
                        device=device,
                        title=f"High memory usage on {device.name}",
                        message=f"Memory usage is at {result.memory_used}%",
                        severity='warning'
                    )
                    
                if result.disk_used and result.disk_used > 90:
                    create_alert(
                        device=device,
                        title=f"High disk usage on {device.name}",
                        message=f"Disk usage is at {result.disk_used}%",
                        severity='warning'
                    )
        
        # Save the monitoring result
        result.save()
        return f"Monitoring complete for {device.name}"
    
    except Device.DoesNotExist:
        return f"Device with ID {device_id} not found"
    except Exception as e:
        return f"Error monitoring device {device_id}: {str(e)}"

def check_ping(ip_address, count=3, timeout=1):
    """Perform a ping check on the specified IP address."""
    try:
        # Use ping command with subprocess
        if subprocess.call(['ping', '-c', str(count), '-W', str(timeout), ip_address],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            # Measure latency with a second ping
            start_time = time.time()
            subprocess.call(['ping', '-c', '1', '-W', str(timeout), ip_address],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            latency = (time.time() - start_time) * 1000  # Convert to ms
            return 'up', latency
        else:
            return 'down', None
    except Exception:
        return 'unknown', None

def check_snmp(ip_address, community='public', port=161):
    """Perform SNMP checks on the specified device."""
    metrics = {}
    try:
        # Simple SNMP get to check if SNMP is responsive
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip_address, port), timeout=2.0, retries=1),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        )
        
        if errorIndication or errorStatus:
            return 'unreachable', None
            
        # If we got here, SNMP is working. Try to get some basic system metrics.
        # This is simplified and may need adjustment for different device types
        try:
            # CPU Load (generic approach - may need device-specific OIDs)
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(community),
                       UdpTransportTarget((ip_address, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'laLoad', 1)))
            )
            if not errorIndication and not errorStatus:
                metrics['cpu_load'] = float(varBinds[0][1]) * 100
        except:
            pass
            
        try:
            # Memory usage (generic approach)
            # These OIDs might need to be adjusted based on the device type
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(community),
                       UdpTransportTarget((ip_address, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalReal', 0)),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0)))
            )
            if not errorIndication and not errorStatus:
                total_memory = float(varBinds[0][1])
                available_memory = float(varBinds[1][1])
                memory_used_percent = ((total_memory - available_memory) / total_memory) * 100 if total_memory > 0 else 0
                metrics['memory_used'] = memory_used_percent
        except:
            pass
            
        try:
            # Disk usage (generic approach)
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(community),
                       UdpTransportTarget((ip_address, port)),
                       ContextData(),
                       ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'dskPercent', 1)))
            )
            if not errorIndication and not errorStatus:
                metrics['disk_used'] = float(varBinds[0][1])
        except:
            pass
            
        return 'up', metrics
    except Exception:
        return 'unknown', None

def create_alert(device, title, message, severity='warning'):
    """Create a new alert for a device."""
    # Check if a similar unresolved alert already exists
    existing_alerts = Alert.objects.filter(
        device=device,
        title=title,
        status__in=['new', 'acknowledged']
    ).order_by('-created_at')
    
    if existing_alerts.exists():
        # Update the existing alert if it's more than 1 hour old
        existing_alert = existing_alerts.first()
        time_diff = timezone.now() - existing_alert.created_at
        if time_diff.total_seconds() > 3600:  # 1 hour
            existing_alert.created_at = timezone.now()
            existing_alert.message = message
            existing_alert.save()
    else:
        # Create a new alert
        Alert.objects.create(
            device=device,
            title=title,
            message=message,
            severity=severity,
            status='new'
        )

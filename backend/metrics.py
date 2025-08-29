from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request metrics
REQUEST_COUNT = Counter('safevault_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('safevault_request_duration_seconds', 'Request duration', ['method', 'endpoint'])

# Authentication metrics
LOGIN_ATTEMPTS = Counter('safevault_login_attempts_total', 'Login attempts', ['status'])
FAILED_LOGINS = Counter('safevault_failed_logins_total', 'Failed login attempts', ['username'])

# Security metrics
SECURITY_EVENTS = Counter('safevault_security_events_total', 'Security events', ['event_type'])

# Business metrics
ACTIVE_USERS = Gauge('safevault_active_users', 'Number of active users')
SECRETS_COUNT = Gauge('safevault_secrets_total', 'Total number of secrets')
AWS_OPERATIONS = Counter('safevault_aws_operations_total', 'AWS operations', ['operation', 'status'])

def get_metrics():
    """Return Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

def record_login_attempt(success: bool, username: str = None):
    """Record login attempt metrics"""
    status = 'success' if success else 'failed'
    LOGIN_ATTEMPTS.labels(status=status).inc()
    if not success and username:
        FAILED_LOGINS.labels(username=username).inc()

def record_security_event(event_type: str):
    """Record security event metrics"""
    SECURITY_EVENTS.labels(event_type=event_type).inc()

def record_aws_operation(operation: str, success: bool):
    """Record AWS operation metrics"""
    status = 'success' if success else 'failed'
    AWS_OPERATIONS.labels(operation=operation, status=status).inc()

def update_active_users(count: int):
    """Update active users gauge"""
    ACTIVE_USERS.set(count)

def update_secrets_count(count: int):
    """Update secrets count gauge"""
    SECRETS_COUNT.set(count)
from prometheus_client import Counter, Histogram

# Request metrics
REQUEST_COUNT = Counter(
    "medops_http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "medops_http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint"],
)

# Business metrics
APPOINTMENTS_CREATED = Counter(
    "medops_appointments_created_total",
    "Total Appointments Created",
    ["status"],
)

APPOINTMENTS_CANCELLED = Counter(
    "medops_appointments_cancelled_total",
    "Total Appointments Cancelled",
)

APPOINTMENTS_RESCHEDULED = Counter(
    "medops_appointments_rescheduled_total",
    "Total Appointments Rescheduled",
)

AVAILABILITY_QUERY_LATENCY = Histogram(
    "medops_availability_query_duration_seconds",
    "Time taken to calculate doctor availability",
)

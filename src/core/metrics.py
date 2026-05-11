from prometheus_client import Counter


HTTP_REQUESTS_TOTAL = Counter(
    "secpilot_http_requests_total",
    "Total HTTP requests handled by SecPilot API.",
    ["method", "path", "status"],
)

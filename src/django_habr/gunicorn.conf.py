from multiprocessing import cpu_count

_bind_host = "0.0.0.0"
_bind_port = "8000"

bind = f"{_bind_host}:{_bind_port}"

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

workers = cpu_count() * 2 + 1

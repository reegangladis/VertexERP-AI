import contextvars

# Global context variable for tracking the current request ID across threads/tasks
request_id_ctx = contextvars.ContextVar("request_id", default="N/A")

try:
    from .celery import app as celery_app
    # expose Celery app as a module-level variable for `celery -A volleyball_site worker`.
    __all__ = ('celery_app',)
except Exception:
    # Celery may not be available in some environments
    pass


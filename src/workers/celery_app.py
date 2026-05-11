from celery import Celery

from src.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "secpilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.workers.tasks", "src.workers.monitor_tasks"],
)
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "run-enabled-monitoring-checks": {
            "task": "secpilot.monitoring.run_enabled_checks",
            "schedule": settings.MONITORING_INTERVAL_SECONDS,
        }
    },
)

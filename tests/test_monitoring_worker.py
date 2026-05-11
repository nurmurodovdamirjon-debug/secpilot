from src.workers.celery_app import celery_app


def test_monitoring_task_is_scheduled() -> None:
    schedule = celery_app.conf.beat_schedule["run-enabled-monitoring-checks"]

    assert schedule["task"] == "secpilot.monitoring.run_enabled_checks"
    assert schedule["schedule"] > 0

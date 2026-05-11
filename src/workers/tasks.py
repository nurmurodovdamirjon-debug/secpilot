from src.workers.celery_app import celery_app


@celery_app.task(name="secpilot.health_check")
def health_check_task() -> dict[str, str]:
    return {"status": "ok"}


@celery_app.task(name="secpilot.defensive_job_placeholder")
def defensive_job_placeholder(job_id: str) -> dict[str, str]:
    # TODO: Wire authorized audit jobs after PolicyGate and audit persistence are complete.
    return {"job_id": job_id, "status": "queued"}

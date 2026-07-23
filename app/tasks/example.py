from app.core.celery import celery_app


@celery_app.task(name="example.add_numbers")
def add_numbers(first: int, second: int) -> int:
    return first + second

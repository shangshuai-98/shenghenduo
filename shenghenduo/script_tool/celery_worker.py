from celery import Celery


celery_app = Celery()

@celery_app.task
def run_task():
    print('task-1')
    return "success task "





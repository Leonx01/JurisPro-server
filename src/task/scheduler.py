import inspect
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.task import methods

scheduler = BackgroundScheduler()
method_lookup = {}


def load_local_methods():
    for name, obj in inspect.getmembers(methods):
        if inspect.isfunction(obj):
            method_lookup[name] = obj


task_examples = [
    {
        "cron_expr": "*/1 * * * * ",  # 每5秒执行一次
        "method": "run_task",
        "params": {"task_id": 1, "param": "value1"}
    },
    {
        "cron_expr": "*/2 * * * * ",  # 每10秒执行一次
        "method": "generate_report",
        "params": {"task_id": 2, "param": "detailed"}
    },
    {
        "cron_expr": "*/1 * * * * ",  # 每15秒执行一次
        "method": "send_email_notification",
        "params": {"task_id": 3, "param": "user@example.com"}
    },
    {
        "cron_expr": "*/15 * * * * ",  # 每15秒执行一次
        "method": "invalid_method",
        "params": {"task_id": 3, "param": "user@example.com"}
    }
]


def load_tasks():
    for task in task_examples:
        # 获取任务的 cron 表达式和方法名
        cron_expr = task["cron_expr"]
        method_name = task["method"]
        params = task["params"]

        # 获取方法
        method = method_lookup.get(method_name)
        if method:
            # 将任务添加到调度器
            cron_trigger = CronTrigger.from_crontab(cron_expr)
            scheduler.add_job(method, cron_trigger, kwargs=params, id=f"task_{method_name}", name=f"{method_name} Task",
                              replace_existing=True)
        else:
            logging.error(f"Method {method_name} not found")


# Start the scheduler if it's not already running
def start_scheduler():
    if not scheduler.running:
        load_local_methods()
        load_tasks()
        scheduler.start()

# methods.py
import logging

# 设置日志基本配置
logging.basicConfig(level=logging.INFO)


def run_task(task_id, param):
    logging.info(f"Running task {task_id} with params {param}")


def generate_report(task_id, param):
    logging.info(f"Generating report for task {task_id} with params {param}")


def send_email_notification(task_id, param):
    logging.info(f"Sending email for task {task_id} with params {param}")


def archive_data(task_id, param):
    logging.info(f"Archiving data for task {task_id} with params {param}")


def clean_up_temp_files(task_id, param):
    return f"Cleaning up temp files for task {task_id} with params {param}"

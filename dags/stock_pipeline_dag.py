from datetime import timedelta

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="stock_pipeline",
    # 17:00 เวลานิวยอร์ก วันจันทร์-ศุกร์ (ตลาดหุ้นสหรัฐปิด 16:00)
    schedule="0 17 * * 1-5",
    start_date=pendulum.datetime(2026, 10, 1, tz="America/New_York"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["stocks"],
) as dag:
    BashOperator(
        task_id="run_pipeline",
        bash_command="cd /opt/airflow/pipeline && /opt/airflow/pipeline-venv/bin/python main_pipeline.py",
        append_env=True,
    )
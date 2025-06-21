from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
import logging

def recalc_icer_and_qaly():
    try:
        with psycopg2.connect(
            dbname="valmed", user="valmed", password="valmedpass", host="db"
        ) as conn:
            with conn.cursor() as cur:
                # ICER calculation
                cur.execute("""
                    UPDATE prescriptions
                    SET calculated_icer = 
                        CASE 
                            WHEN effectiveness_at_time_of_prescription > 0 
                            THEN cost_at_time_of_prescription / effectiveness_at_time_of_prescription
                            ELSE NULL
                        END
                """)
                # QALY calculation (demo: qaly_score = effectiveness * 0.8)
                cur.execute("""
                    UPDATE prescriptions
                    SET qaly_score = 
                        CASE 
                            WHEN effectiveness_at_time_of_prescription IS NOT NULL
                            THEN effectiveness_at_time_of_prescription * 0.8
                            ELSE NULL
                        END
                """)
                conn.commit()
    except Exception as e:
        logging.error(f"Error in recalc_icer_and_qaly: {e}")
        raise

with DAG(
    dag_id="daily_metrics_recalc",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    PythonOperator(
        task_id="recalc_icer_and_qaly",
        python_callable=recalc_icer_and_qaly,
    ) 
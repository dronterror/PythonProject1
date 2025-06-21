from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2
import random
import logging

def sync_drug_prices():
    try:
        with psycopg2.connect(
            dbname="valmed", user="valmed", password="valmedpass", host="db"
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM drugs")
                ids = [row[0] for row in cur.fetchall()]
                for drug_id in ids:
                    new_price = round(random.uniform(10, 100), 2)
                    cur.execute("UPDATE drugs SET price_per_unit = %s WHERE id = %s", (new_price, drug_id))
                conn.commit()
    except Exception as e:
        logging.error(f"Error in sync_drug_prices: {e}")
        raise

with DAG(
    dag_id="drug_price_sync",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@weekly",
    catchup=False,
) as dag:
    PythonOperator(
        task_id="sync_drug_prices",
        python_callable=sync_drug_prices,
    ) 
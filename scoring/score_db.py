# DATABASE OPERATIONS

import os
import psycopg2
from psycopg2.extras import execute_batch
from scoring_engine import OEResult

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "ndi_agent_management"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Project33"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS operational_excellence_results (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(255),
    cycle_name VARCHAR(255),
    metric_id VARCHAR(50),
    maturity_level INT,
    maturity_label VARCHAR(255),
    maturity_description TEXT,
    percentage FLOAT,
    scale INT,
    weight FLOAT,
    weighted_score FLOAT,
    final_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def insert_oe_results(conn, result: OEResult):
    rows = [
        (
            result.entity_name,
            result.cycle_name,
            m.metric_id,
            result.maturity_level,
            result.maturity_label,
            result.maturity_description,
            m.percentage,
            m.scale,
            m.weight,
            m.weighted_score,
            result.final_score
        )
        for m in result.metrics
    ]

    sql = """
    INSERT INTO operational_excellence_results (
        entity_name, cycle_name, metric_id, maturity_level, 
        maturity_label, maturity_description,
        percentage, scale, weight, weighted_score,
        final_score
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (entity_name, cycle_name, metric_id) DO NOTHING;
    """

    with conn.cursor() as cur:
        execute_batch(cur, sql, rows)


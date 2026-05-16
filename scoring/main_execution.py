# Execution Runner for The Scoring Engine

from scoring.scoring_engine import evaluate_oe
from scoring.score_export import export_json, print_report
from scoring.score_db import insert_oe_results, CREATE_TABLE_SQL, get_connection
import psycopg2


if __name__ == "__main__":

    # SAMPLE INPUT DATA (13 OE METRICS)

    entity_name = "Ministry of Health"
    cycle_name = "Third Measurement Cycle"

    sample_data = {
        "DSI.OE.01": {"apis": [{"certified": 80, "total_attributes": 100, "classified": True}]},
        "DSI.OE.02": {"systems": [
            {"implemented": True, "method_followed": True, "updated": True},
            {"implemented": True, "method_followed": False, "updated": True}
        ]},
        "DO.OE.03": {"percentage": 88},
        "DQ.OE.02": {"percentage": 79},
        "DO.OE.02": {"percentage": 91},
        "RMD.OE.01": {"published": 20, "required": 25},
        "OD.OE.01": {"published": 100, "required": 120},
        "OD.OE.05": {"requests": [
            {"category": "Easy", "duration": 5},
            {"category": "Medium", "duration": 10}
        ]},
        "MCM.OE.01": {"done": 30, "required": 40},
        "MCM.OE.02": {"done": 15, "required": 20},
        "MCM.OE.03": {"done": 50, "required": 60},
        "DSI.OE.05": {"done": 45, "required": 50},
        "DQ.OE.03": {"done": 35, "required": 40}
    }

    # RUN THE SCORING ENGINE
    result = evaluate_oe(entity_name, cycle_name, sample_data)
    print_report(result)
    export_json("scoring_engine_OE_report.json", result)    # create JSON file

    # SAVE RESULTS TO DATABASE

    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
            insert_oe_results(conn, result)

        print("Operational Excellence results committed successfully.")

    except psycopg2.DatabaseError as e:
        print(f"Database execution failure: {e}")

    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


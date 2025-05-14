from fastapi import FastAPI, Request
import sqlite3
import json
from pathlib import Path
import uvicorn


def run():
    app = FastAPI()

    # Load allowed filter fields
    with open(Path(__file__).parent / "search_fields.json") as f:
        FILTER_FIELDS = json.load(f)

    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent  # ← gets to top-level `mds/`
    DB_PATH = BASE_DIR / "modelcard.db"

    @app.get("/search")
    def search_modelcards(request: Request):
        filters = []
        values = []

        for key, value in request.query_params.items():
            if key.endswith("_lte"):
                field = key[:-4]
                if field in FILTER_FIELDS:
                    filters.append(f"{field} <= ?")
                    values.append(value)
            elif key.endswith("_gte"):
                field = key[:-4]
                if field in FILTER_FIELDS:
                    filters.append(f"{field} >= ?")
                    values.append(value)
            elif key.endswith("_lt"):
                field = key[:-3]
                if field in FILTER_FIELDS:
                    filters.append(f"{field} < ?")
                    values.append(value)
            elif key.endswith("_gt"):
                field = key[:-3]
                if field in FILTER_FIELDS:
                    filters.append(f"{field} > ?")
                    values.append(value)
            elif key in FILTER_FIELDS:
                filters.append(f"{key} = ?")
                values.append(value)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        query = f"""
            SELECT hash, model_name, f1_score, license, dataset, cve_count
            FROM modelcards {where_clause}
        """

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, values)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "hash": r[0],
                "model_name": r[1],
                "f1_score": r[2],
                "license": r[3],
                "dataset": r[4],
                "cve_count": r[5],
            }
            for r in rows
        ]

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

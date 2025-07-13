import requests
import json
import os
import psycopg2
from beir import util
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.evaluation import EvaluateRetrieval
import logging
import pathlib
import time

# --- Configuration (from environment variables set in docker-compose) ---
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8080")
DATASET_NAME = "scifact"
# The script runs inside a container, so paths are relative to the container's /app directory
DATA_PATH = f"/app/beir_data/{DATASET_NAME}" 

DB_CONFIG = {
    "dbname":   os.getenv("DB_NAME", "smartdoc"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host":     os.getenv("DB_HOST", "db"), # Use the Docker service name
    "port":     5432 # Use the internal Docker port
}

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s:%(name)s: %(message)s')

def create_id_mapping() -> dict:
    """Connects to the DB and creates a map from your system's ID to the original BEIR ID."""
    logging.info(f"Connecting to PostgreSQL on host '{DB_CONFIG['host']}' to create ID mapping...")
    id_map = {}
    for i in range(5): # Retry connection
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            # We get all documents since the DB should only contain the BEIR corpus for this test
            cur.execute("SELECT id, file_name FROM documents")
            rows = cur.fetchall()
            
            for db_id, file_name in rows:
                # The original BEIR ID is the filename without the .txt extension
                beir_id = pathlib.Path(file_name).stem
                id_map[str(db_id)] = beir_id
                
            cur.close()
            conn.close()
            logging.info(f"Successfully created mapping for {len(id_map)} documents.")
            return id_map
        except psycopg2.OperationalError as e:
            logging.warning(f"DB connection failed (attempt {i+1}/5): {e}. Retrying in 5 seconds...")
            time.sleep(5)
    
    logging.error("Could not connect to the database after multiple retries.")
    return {}

def run_search_and_translate(query: str, id_map: dict) -> dict:
    """Calls your search API and translates the resulting IDs."""
    try:
        params = {"q": query, "maxHits": 100}
        response = requests.get(f"{BACKEND_API_URL}/docsearch/api/files/search", params=params)
        response.raise_for_status()
        
        results = response.json().get("searchResults", [])
        
        # Translate a dictionary of {beir_id: score}
        translated_results = {}
        for hit in results:
            db_id = str(hit['id'])
            if db_id in id_map:
                beir_id = id_map[db_id]
                translated_results[beir_id] = hit['hybridScore']
            else:
                logging.warning(f"DB ID {db_id} from search result not found in ID map. Skipping.")

        return translated_results
    except Exception as e:
        logging.error(f"Search failed for query '{query}': {e}")
        return {}

def main():
    # 1. Load the BEIR dataset from the mounted volume
    logging.info(f"Loading BEIR dataset '{DATASET_NAME}' from {DATA_PATH}...")
    try:
        corpus, queries, qrels = GenericDataLoader(data_folder=DATA_PATH).load(split="test")
    except Exception as e:
        logging.error(f"Failed to load dataset. Make sure it's downloaded to the './beir_data' directory. Error: {e}")
        return

    # 2. Create the ID translation map from the database
    id_map = create_id_mapping()
    if not id_map:
        logging.error("Could not create ID map. Aborting evaluation.")
        return

    # 3. Run all queries and get translated results
    results = {}
    logging.info(f"Running {len(queries)} queries against the search API...")
    for query_id, query_text in queries.items():
        results[query_id] = run_search_and_translate(query_text, id_map)
    
    logging.info("All queries complete.")

    # 4. Evaluate the results
    logging.info("Evaluating retrieval results...")
    evaluator = EvaluateRetrieval()
    scores = evaluator.evaluate(qrels, results, evaluator.k_values)

    print("\n--- BEIR Evaluation Results ---")
    print(json.dumps(scores, indent=2))

if __name__ == "__main__":
    main()

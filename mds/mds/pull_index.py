import subprocess
import sqlite3
import json
import yaml
from pathlib import Path
import tempfile
import shutil

# Paths
BASE_DIR = Path(__file__).parent.parent.parent  # ← gets to top-level `mds/`
DB_PATH = BASE_DIR / "modelcard.db"
CONFIG_PATH = Path(__file__).parent / "registry_config.yaml"




def list_tags(ref):
    try:
        result = subprocess.run(
            ["oras", "repo", "tags", "--plain-http", ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        tags = result.stdout.strip().splitlines()
        return [tag for tag in tags if not tag.startswith("sha256-")]
    except subprocess.CalledProcessError:
        return []


def discover_modelcards(ref):
    try:
        result = subprocess.run(
            ["oras", "discover", "--artifact-type", "application/vnd.oci.modelcard.v1+json",
            "--plain-http", ref],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        lines = result.stdout.strip().splitlines()
        return [line.strip().split()[-1] for line in lines if line.strip().startswith("└── sha256")]
    except subprocess.CalledProcessError:
        return []


def pull_modelcard(ref, digest):
    temp_dir = Path(tempfile.mkdtemp(prefix="modelcard-pull-"))
    pull_ref = f"{ref}@{digest}"

    try:
        subprocess.run(
            ["oras", "pull", "--plain-http", pull_ref, "-o", str(temp_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        json_files = list(temp_dir.rglob("*.json"))
        if not json_files:
            json_files = list(temp_dir.rglob("*"))

        if not json_files:
            raise FileNotFoundError(f"No modelcard file found in {pull_ref}")

        with open(json_files[0]) as f:
            return json.load(f)
    finally:
        shutil.rmtree(temp_dir)


def insert_modelcard(data):
     # Create or connect to SQLite DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hash_ = data.get("hash")
    if not hash_:
        print(f"❌ Skipping: missing 'hash'")
        return

    c.execute("SELECT 1 FROM modelcards WHERE hash = ?", (hash_,))
    if c.fetchone():
        print(f"⚠️  Already in DB: {hash_}")
        return

    c.execute("""
        INSERT INTO modelcards (hash, model_name, f1_score, license, dataset, cve_count, model_ref, registry)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        hash_,
        data.get("model_name"),
        data.get("f1_score"),
        data.get("license"),
        data.get("dataset"),
        data.get("cve_count"),
        data.get("model_ref"),
        data.get("registry")
    ))
    conn.commit()


def run():
    print("[MDS] Indexing modelcards from registry...")
    
    # Load registry config
    with open(CONFIG_PATH) as f:
        REGISTRIES = yaml.safe_load(f)

    # Create or connect to SQLite DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS modelcards (
            hash TEXT PRIMARY KEY,
            model_name TEXT,
            f1_score REAL,
            license TEXT,
            dataset TEXT,
            cve_count INTEGER,
            model_ref TEXT,
            registry TEXT
        )"""
    )
    conn.commit()

    # Main loop
    for reg in REGISTRIES:
        base = f"{reg['host']}/{reg['prefix']}"
        print(f"🔍 Crawling {base}")
        for repo in reg["repos"]:
            full_repo = f"{base}/{repo}"
            tags = list_tags(full_repo)
            for tag in tags:
                print("Tag", tag)
                ref = f"{full_repo}:{tag}"
                digests = discover_modelcards(ref)
                print(f"📎 {ref} -> {len(digests)} modelcard(s): {digests}")
                for digest in digests:
                    try:
                        modelcard = pull_modelcard(ref, digest)
                        modelcard["model_ref"] = ref
                        modelcard["registry"] = reg["host"]
                        insert_modelcard(modelcard)
                        print(f"✅ Indexed modelcard for {ref} @ {digest}")
                    except Exception as e:
                        print(f"❌ Failed to index {ref}@{digest}: {e}")

    conn.close()


    

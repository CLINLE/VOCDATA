"""
Lädt die Datei data/bfs_demo.csv nach MySQL (Tabelle bfs_demo).
Ausführen im aktivierten Conda-Env »vocdata«:  python etl/load_bfs_demo.py
"""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# Basis: Projekt-Hauptordner = zwei Ebenen über diesem Skript
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "bfs_demo.csv"   # absoluter Pfad
TABLE    = "bfs_demo"


# ❶ CSV einlesen
df = pd.read_csv(CSV_PATH)

# ❷ DB-Verbindung herstellen – Root-User, DB »vocdata«
engine = create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata",
    echo=False,
    pool_recycle=3600
)

# ❸ Sicherstellen, dass Tabelle existiert (einfaches Schema)
ddl = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    id    INT PRIMARY KEY,
    name  VARCHAR(100),
    value INT
);
"""
with engine.begin() as conn:
    conn.execute(text(ddl))

# ❹ Daten laden (replace = alte Einträge überschreiben)
df.to_sql(TABLE, con=engine, if_exists="replace", index=False)

print(f"{len(df)} Zeilen in die Tabelle »{TABLE}« geschrieben.")

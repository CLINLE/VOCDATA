# scripts/db_migrations.py
"""
Nachrüst-Migration für bestehende Tabelle qual_docs.
Legt fehlende Spalten an, füllt Hashes, setzt Constraints.
Beliebig oft aufrufbar – ignoriert Duplicate-Fehler.
"""

import sqlalchemy as sa
from sqlalchemy.exc import OperationalError, ProgrammingError
import contextlib

engine = sa.create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata?charset=utf8mb4"
)

def try_alter(sql: str):
    """Führt ALTER TABLE aus und unterdrückt 'duplicate column/index' Fehler."""
    with engine.begin() as c:
        try:
            c.exec_driver_sql(sql)
        except (OperationalError, ProgrammingError):
            pass

# ── 1  fehlende Spalten ergänzen ────────────────────────────────────────
try_alter("ALTER TABLE qual_docs ADD COLUMN sha256 CHAR(64) NULL;")
try_alter("ALTER TABLE qual_docs ADD COLUMN doc_type ENUM('Studie','Buch','Artikel','Sonstiges') DEFAULT 'Sonstiges';")
try_alter("ALTER TABLE qual_docs ADD COLUMN uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")

# ── 2  Hashes nachpflegen ───────────────────────────────────────────────
with engine.begin() as c:
    n = c.exec_driver_sql("""
        UPDATE qual_docs
        SET sha256 = SHA2(CONCAT(doc_id, filename),256)
        WHERE sha256 IS NULL OR sha256='';
    """).rowcount
print("Hashes nachgepflegt:", n)

# ── 3  NOT NULL + UNIQUE setzen ─────────────────────────────────────────
try_alter("ALTER TABLE qual_docs MODIFY sha256 CHAR(64) NOT NULL;")
try_alter("ALTER TABLE qual_docs ADD UNIQUE KEY uq_sha256 (sha256);")

print("Migration ✔")

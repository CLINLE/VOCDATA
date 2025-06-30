# tests/etl/test_pdf_ingest.py
"""
Smoke-Test: PDF-Ingestion

Ziel
----
* Prüft, ob die ETL-Routine `pdf_upload.ingest.ingest()` eine neue
  PDF-Datei erkennt, in die Tabelle `qual_docs` schreibt und damit
  die Anzahl Datensätze erhöht.

Ablauf
------
1.  Zählt die vorhandenen Zeilen in `qual_docs`.
2.  Kopiert eine kleine Demo-PDF nach `uploads/pdf/`.
3.  Ruft `ingest()` auf (Text-Extraktion → DB-Insert).
4.  Zählt erneut, der Wert muss mindestens um 1 steigen.

Skippt automatisch, wenn keine Demo-PDF gefunden wird.
"""

import shutil, pathlib, sys, sqlalchemy as sa, pytest

# --------------------------------------------------------------------
# Pfad-Fix (repo/  &  repo/scripts/)
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

# --------------------------------------------------------------------
# Imports aus Projekt
from pdf_upload import ingest              # scripts/pdf_upload/ingest.py

# DB-Engine
ENGINE = sa.create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata?charset=utf8mb4"
)

# --------------------------------------------------------------------
# Test-Funktion
@pytest.mark.skipif(
    not (ROOT / "seed" / "demo_pdfs").exists(),
    reason="keine Demo-PDFs vorhanden"
)
def test_pdf_ingest_adds_row(tmp_path):
    """Neue PDF → qual_docs-Rowcount +1"""

    # --- 1 Ausgangs-Rowcount ----------------------------------------
    start_count = sa.text("SELECT COUNT(*) FROM qual_docs")
    with ENGINE.connect() as con:
        before = con.execute(start_count).scalar_one()

    # --- 2 Demo-PDF kopieren ----------------------------------------
    demo_pdf = next((ROOT / "seed" / "demo_pdfs").glob("*.pdf"))
    uploads_dir = ROOT / "uploads" / "pdf"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    target_file = uploads_dir / demo_pdf.name
    shutil.copy(demo_pdf, target_file)

    # --- 3 Ingestion auslösen ---------------------------------------
    ingest.ingest()

    # --- 4 Rowcount erneut lesen ------------------------------------
    with ENGINE.connect() as con:
        after = con.execute(start_count).scalar_one()

    assert after == before + 1, "Ingestion hat keinen neuen Datensatz erzeugt"

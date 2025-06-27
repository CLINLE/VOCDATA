# scripts/pdf_ingest.py
import os
from glob import glob
from PyPDF2 import PdfReader
from sqlalchemy import create_engine, text

# --- DB-Verbindung ---------------------------------------------------------
ENGINE = create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata?charset=utf8mb4",
    future=True,
)

# --- PDF-Verzeichnis -------------------------------------------------------
PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "pdf")

def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "".join(page.extract_text() or "" for page in reader.pages)

def ingest():
    pdf_files = glob(os.path.join(PDF_DIR, "*.pdf"))
    if not pdf_files:
        print("Keine PDFs gefunden – lege Dateien in uploads/pdf/")
        return

    with ENGINE.begin() as conn:
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            print(f"Ingesting {filename} …")
            full_text = extract_text(pdf_path)

            stmt = text(
                """
                INSERT INTO qual_docs (filename, full_text)
                VALUES (:filename, :full_text)
                ON DUPLICATE KEY UPDATE full_text = VALUES(full_text)
                """
            )
            conn.execute(stmt, {"filename": filename, "full_text": full_text})

    print("✅ Ingestion abgeschlossen.")

if __name__ == "__main__":
    ingest()

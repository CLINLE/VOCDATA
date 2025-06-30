# Vocational Data Platform
Starter repository for my master thesis.
# VOCDATA – Datenarchitektur & -Pipeline für BFS-Berufsbildungsstatistik  
Masterarbeit Claudia Ledenig (ZHAW)

## 1 Überblick
Die Arbeit beweist den Mehrwert eines integrativen Datensystems (qualitative und quantitative daten) anhand einer effizienteren Auswertung von Berufsbildungsdaten, konkret **Lehrvertrags­abbrüchen**.  

Dieses Repository enthält aktuell den vollständigen, reproduzierbaren **ETL-Prozess** für zwei amtliche Datensätze des Bundesamts für Statistik (BFS):

1. **Lehrvertragsauflösungen (LVA) – Kohorte 2019**  
   *Beobachtungszeitraum: Lehrbeginn 2019 bis 31.12.2023*

2. **Abschlussquoten Sek II – Referenzjahr 2022**

Ziel ist ein **Sternschema** in MySQL 8, über das sich beide Datentöpfe konsistent analysieren lassen (Plotly-Dashboards, Power BI o. Ä.).  
Alle Schritte sind in Jupyter-Notebooks dokumentiert und versioniert.

---

## 2 Ordnerstruktur 
vvocdata/
├── data/                # Roh-Excel & CSV-Quellen
├── tmp/                 # Parquet-Staging + Audit-CSVs
├── uploads/
│   └── pdf/             # Manuell hochgeladene PDF-Dokumente
├── notebooks/
│   01a_profile_lva.ipynb
│   01b_profile_abschluss.ipynb
│   02a_clean_lva.ipynb
│   02b_clean_abschluss.ipynb
│   04a_load_facts_lva.ipynb
│   04b_load_facts_abschluss.ipynb
│   05_fk_updates.ipynb
│   06a_lva_audit.ipynb
│   06b_abs_audit.ipynb
│   07a_lva_quality.ipynb
│   07b_abs_quality.ipynb
│   90_qual_text_search.ipynb      # NEU: ChatGPT-Suche / Zusammenfassung
├── scripts/
│   pdf_ingest.py          # PDF → Text → qual_docs-Tabelle
│   etl_qual_docs.py       # Hilfsfunktionen für Text-ETL
│   db_models.py           # SQLAlchemy-ORM (Dim/Facts/qual_docs)
│   config.py              # Liest .env (OpenAI-Key, DB-Creds)
├── tests/                 # (optional) kleine Py-Tests für ETL-Funktionen
├── .env                   # **nicht committen** – API-Keys, DB-Passwörter
├── .gitignore
└── README.md





## 3 Voraussetzungen

| Komponente | Version | Kurzinstallation |
|------------|---------|------------------|
| **Miniconda 3** | ≥ 23.x | `conda create -n vocdata python=3.11` |
| **VS Code**    | ≥ 1.88 | Python- & Jupyter-Extension aktiv |
| **Docker Desktop** | ≥ 28.x | WSL 2 Backend, 4 GB RAM genügen |
| **MySQL 8 Container** | `mysql:8` | `docker run -d --name voc-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=voc_root mysql:8` |
| **MySQL Workbench** | ≥ 8.0.36 | optional – ER-Diagramm |

---

## 4 Schnellstart (End-to-End)

```bash
# 1. Umgebung aktivieren
conda activate vocdata
pip install -r requirements.txt   # pandas, SQLAlchemy, plotly, …

# 2. JupyterLab starten
jupyter lab

# 3. Notebooks sequenziell ausführen
#    a_profile/02_profile_bfs_lva.ipynb  (nur Sichtprüfung)
#    b_ETL/04_load_dims.ipynb            (Dimensionen schreiben)
#    b_ETL/05_load_facts.ipynb           (Kohorte 2019 LVA-Fakt)
#    a_profile/03_profile_bfs_abschlussquote.ipynb
#    b_ETL/08_load_fact_abschluss_stats.ipynb


Das Schema vocdata wird automatisch erstellt (Container-Root-Login).
Nach erfolgreichem Lauf liefert SELECT COUNT(*) FROM fact_lva_stats; 1188 Zeilen.

5 Notebook-Landkarte
Notebook	Zweck	Schreibt SQL?
01_poc_overview	Mini-End-to-End mit Demo-CSV und Plotly	✔ (bfs_demo)
02_profile_bfs_lva	Spaltencheck, Kardinalität, NULL-Anteile	✖
03_profile_bfs_abschlussquote	dito	✖
04_load_dims	13 Dimensionstabellen (inkl. dim_kohorte)	✔
05_load_facts	fact_lva_stats inkl. Flags + Kohorte	✔
07_check_abschlussquote	Audit‐Notebook für Abschlussfakt	✖
08_load_fact_abschluss_stats	fact_abschluss_stats schreiben	✔

6 ER-Diagramm
docs/diagramme/erm_v1.png zeigt das aktuelle Sternschema.
Die Tabellen sind in Workbench in zwei Gruppen gefasst:

LVA-Kohorte 2019 (grün)

Abschlussquoten 2022 (blau)

7 To Do (Stand 23 Jun 2025)
 Pfade im Code auf relative ../data/… prüfen

 README Methodik fertigschreiben (Kap 4 Thesis)

 PX-Dateien testweise integrieren (falls Zeitbudget)

 Qualitäts-Notebook: FK-Checks, Summenkontrolle

8 Lizenz
Nur für Lehr- und Forschungszwecke der ZHAW; Rohdaten © BFS.
Quellcode unter MIT-Lizenz.





_____
PDF-Upload & Ingestion – 3 – 4 h

ETL-Pipeline qualitative Texte (qual_docs) – 1 – 2 h

ChatGPT-Integration für Textanalyse – 1 – 2 h

Such-/Zusammenfassungsfunktion in Jupyter – 2 – 3 h



PDF-Upload & Ingestion
# Implementierung & Technische Entscheidungen (Stand MVP)

## 1 Conda-Umgebung `vocdata` aktiviert

* **Ziel / Problem** Reproduzierbare Laufzeit für alle ETL-Skripte.
* **Begründung** Conda bietet paketgenaue Isolation; Umgebung war bereits vorbereitet.
* **Ergebnis / Nachweis** Nach `conda activate vocdata` erscheint der Prompt `(vocdata)`.

---

## 2 Installation **PyPDF2**

* **Ziel** Textextraktion aus PDFs für den Import qualitativer Quellen.
* **Begründung** Reine-Python-Bibliothek, keine externen Services nötig, schnell genug für Klartext.
  *Alternativen:* pdfminer (langsamer) oder Apache Tika (Java-Abhängigkeit) – verworfen.
* **Ergebnis** `pip install PyPDF2` → *Successfully installed PyPDF2-3.0.1*.

---

## 3 Ordner *uploads*, *uploads/pdf*, *scripts* angelegt

* **Ziel** Saubere Trennung zwischen Roh-Uploads und wieder­verwendbarem Code.
* **Begründung** Verhindert Datenchaos, erleichtert Git-Diffs.
* **Ergebnis** Ordner committed (Git-Hash `dc51e19`).

---

## 4 Beispiel-PDFs hinzugefügt

Acht PDFs unter *uploads/pdf/* als Testmaterial für ETL und spätere NLP-Analyse.

---

## 5 MySQL-Tabelle `qual_docs` erstellt

```sql
CREATE TABLE IF NOT EXISTS vocdata.qual_docs (
    doc_id    INT AUTO_INCREMENT PRIMARY KEY,
    filename  VARCHAR(255) NOT NULL,
    title     VARCHAR(255),
    year      SMALLINT,
    full_text LONGTEXT,
    added_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

* **Ziel** Zentrale Ablage aller PDF-Volltexte – Basis für Suche / LLM.
* **Begründung** Einfaches Schema mit AUTO\_INCREMENT-PK; `LONGTEXT` deckt große Studien ab.
* **Ergebnis** MySQL meldet *Query OK*.

---

## 6 Skript `scripts/pdf_ingest.py` erstellt

* **Ziel** Automatisierte Ingestion: PDF → Text → MySQL (`qual_docs`).
* **Begründung** Skript (nicht Notebook), damit unbeaufsichtigt per Cron / CI startbar.
* **Technik** PyPDF2-Parsing, `sqlalchemy+pymysql`-Insert, `glob`‐Dateiscan.
* **Fix** SQLAlchemy-URL auf `?charset=utf8mb4` umgestellt.

---

## 7 Installation **PyCryptodome**

* **Ziel** Unterstützung für AES-verschlüsselte PDFs (PyPDF2-Requirement).
* **Ergebnis** `pip install pycryptodome` – keine Fehler.

---

## 8 Installation **ipywidgets**

* **Ziel** Interaktive Datei-Uploads direkt im Notebook.
* **Begründung** Jupyter-natives Widget, kein externes Front-End nötig.
* **Ergebnis** `pip install ipywidgets` erfolgreich; VS Code unterstützt Widgets sofort.

---

## Upload-Widget & Bereitstellung (fortgeschrittene Schritte)

9. **scripts/__init__.py angelegt**  
   - macht das Verzeichnis *scripts* als Python-Paket importierbar.

10. **Notebook *notebooks/widgets/upload_widget.ipynb* erstellt**  
    - Upload-Button (ipywidgets 8) + Sofort-Ingestion in `qual_docs`.  
    - Pfad-Fix:  
      ```python
      sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
      ```

11. **Event-Handler für ipywidgets 8 angepasst**  
    - `change["new"]` liefert ein *Tuple* → kein `.items()` mehr.

12. **Minimaler, aufgeräumter Widget-Code eingeführt**  
    - zwei Zellen genügen: *Setup & Widget*, *optional: Dateiliste*.  
    - Erfolgs­meldung: **🚀 Upload & Ingestion fertig.**

13. **Kurzer Listing-Snippet**  
    ```python
    for p in PDF_DIR.glob("*.pdf"):
        print(" -", p.name)
    ```

14. **Daten­bereitstellung für den Dozenten geklärt**  
    - Empfehlung: *Starter-Paket* → SQL-Seed + Beispiel-PDFs werden beim ersten `docker compose up` automatisch importiert.  
    - Alternative Wege (ZIP-Volume, Managed Cloud-DB) kurz erläutert.

### OpenAI-Integration & Code-Struktur

15. **scripts/config.py** erstellt  
    - Lädt `.env`, stellt `OPENAI_KEY` zentral bereit.

16. **.env** im Projektstamm angelegt (nicht im Repo):  
    `OPENAI_API_KEY=sk-…`

17. **Ordnerstruktur verfeinert**  
    ```
    scripts/
    ├─ pdf_upload/ingest.py        # ETL für PDFs
    └─ chatgpt_config/summarize_pdf_files.py
    ```
    `__init__.py` in allen Unterordnern, damit Python-Pakete.

18. **summarize_pdf_files.py** (neue OpenAI v1-Syntax)  
    - Funktion `summarize(doc_id)` holt Volltext aus `qual_docs`, ruft `gpt-4o-mini` auf, liefert 8-Satz-Summary.

19. **Bibliothek aktualisiert:** `pip install --upgrade openai python-dotenv`

20. **Funktions­test:**  
    ```powershell
    python -c "from scripts.chatgpt_config.summarize_pdf_files import summarize; print(summarize(1)[:400])"
    ```  
    → Zusammenfassung erscheint ⇒ Integration erfolgreich.

### Volltext-Suche & Unit-Tests

21. **FULLTEXT-Index angelegt**  
    ```sql
    ALTER TABLE qual_docs
    ADD FULLTEXT idx_full_text (full_text);
    ```

22. **search-Modul erstellt**  
    *scripts/chatgpt_config/search.py*  
    ```python
    def search(term, limit=20):
        SELECT doc_id, filename,
               SUBSTRING(full_text,1,300) AS snippet
        FROM qual_docs
        WHERE MATCH(full_text) AGAINST (:q IN NATURAL LANGUAGE MODE)
        LIMIT :lim
    ```

23. **Test-Infrastruktur eingerichtet**  
    - Ordner **tests/** auf Root-Ebene  
    - `test_summarize.py` mit Pfad-Fix + `assert summarize(1)`  
    - Aufruf: `python -m pytest -q` → **1 passed**

24. **Pytest in Conda-Env ausgeführt**  
    Verhindert Modul­fehler (`pymysql`) durch falschen Interpreter.

### Suche & Auswahl-Widget (Notebook)

25. **Notebook `search_widget.ipynb` angelegt**  
    - Pfad-Fix (`sys.path.insert`) ergänzt.  
    - Importiert jetzt  
      ```python
      from chatgpt_integration.search_widget import search
      from chatgpt_integration.summarize_widget import summarize
      ```

26. **Fehlerbehebung**  
    - Module `search_widget.py` und `summarize_widget.py` liegen unter `scripts/chatgpt_integration/`.  
    
      ```  
      brauchen noch lösung so dass kein `ModuleNotFoundError: scripts.config` mehr auftritt.



Notes Search funktion 2 Level
1.  Suche (search(term)) – reines SQL / FTS in MySQL (Läuft lokal in der DB-Engine.)
2. Kontext → LLM – Ausschnitte (snippet oder full_text[:12000]) werden zusammen mit der User-Frage an gpt-4o-mini geschickt (RAG-Aufruf, summarize() etc.)

Ablauf
Suchergebnis → Prompt
search() findet relevante Textstellen, z. B. 3 × 400 Wörter.
Diese Ausschnitte wandern in den System-/Kontext-Teil der Chat-Nachricht.

Promptlänge = Tokenverbrauch
Je mehr Treffer / längere Ausschnitte, desto mehr Input-Tokens.
Jeder zusätzliche Token kostet (Stand Juni 2025) z. B.
gpt-4o-mini: USD 0.0005 pro 1 k Input-Token, USD 0.0015 pro 1 k Output-Token.


--> Kosten steuern
Truncate lange Treffer ([:4000] oder SUBSTRING), wie in summarize()
Limit Anzahl Treffer (limit=5).
Dedup identische Stellen, wenn mehrere Suchbegriffe dasselbe Dokument liefern.

Weitere Kosten:
summarize(doc_id) (12 k Zeichen ≈ 1.8 k Tokens) + 120 Antwort-Tokens ≈ 1 900 typische Token ~ USD 0.003
RAG-Chat: 3 × 300 Wörter Kontext (≈ 750 Tokens) + Frage (50 Tokens) + Antwort (150 Tokens) ≈ 950 ~ USD 0.0014
https://platform.openai.com/docs/guides/production-best-practices/example-procedure-for-evaluating-a-gpt-3-based-system?utm_source=chatgpt.com

````markdown
## 🚀 Quick Start

> **Voraussetzungen**  
> – Docker Desktop ≥ 4.x  
> – Git  
> – eigener OpenAI API-Key

```bash
# 1. Repository klonen
git clone https://github.com/<your-org>/vocdata.git
cd vocdata

# 2. API-Key setzen
cp .env.example .env        # Datei anlegen
# ⇒ OPENAI_API_KEY=<dein_Key> in .env eintragen

# 3. Stack starten
docker compose up -d        # baut Image & startet Container
````

**Öffnen:** [http://localhost:8888](http://localhost:8888)
*(Login-Token steht im Container-Log `docker compose logs -f app`.)*

---

## 🔧 Was passiert beim ersten Start?

| Container               | Aufgabe                                                       | Persistenz                |
| ----------------------- | ------------------------------------------------------------- | ------------------------- |
| **db** (`mysql:8.4`)    | legt Schema an, zieht `seed/schema.sql` + `seed/seed.sql` ein | Volume `db_data`          |
| **app** (lokales Build) | installiert Pakete, startet Jupyter Lab :8888                 | Bind-Mount `uploads/pdf/` |

*Die ETL-Pipeline extrahiert Demo-PDFs direkt beim Seed-Import, sodass Dashboards und RAG sofort Daten liefern.*

---

## 🛠️ Häufige Kommandos

```bash
docker compose ps                  # Container-Status
docker compose logs -f app         # Live-Log Jupyter Lab
docker compose exec db \
  mysql -uroot -pvoc_root vocdata \
  -e "SHOW TABLES;"                # kurzer DB-Check
docker compose down                # Stack stoppen (Volumes bleiben)
```

---

## 📂 Verzeichnisstruktur (Auszug)

```text
vocdata/
├─ scripts/                # Python-Code (ETL, RAG, Adapter)
├─ notebooks/              # Dashboards & Widgets
├─ seed/
│   ├─ schema.sql          # DDL
│   ├─ seed.sql            # Demo-Kennzahlen
│   └─ demo_pdfs/          # kleine Beispiel-PDFs
├─ uploads/pdf/            # eigene PDF-Uploads  (ignored)
└─ docker-compose.yml
```

> **Tipp:**
> *`docker compose down -v`* entfernt Container **und** Volumes, falls Sie komplett neu starten möchten.

```
```

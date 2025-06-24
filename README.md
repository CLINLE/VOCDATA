# Vocational Data Platform
Starter repository for my master thesis.
# VOCDATA – Datenarchitektur & -Pipeline für BFS-Berufsbildungsstatistik  
Masterarbeit Claudia Ledenig (ZHAW)

## 1 Überblick
Dieses Repository enthält aktuell den vollständigen, reproduzierbaren **ETL-Prozess** für zwei amtliche Datensätze des Bundesamts für Statistik (BFS):

1. **Lehrvertragsauflösungen (LVA) – Kohorte 2019**  
   *Beobachtungszeitraum: Lehrbeginn 2019 bis 31.12.2023*

2. **Abschlussquoten Sek II – Referenzjahr 2022**

Ziel ist ein **Sternschema** in MySQL 8, über das sich beide Datentöpfe konsistent analysieren lassen (Plotly-Dashboards, Power BI o. Ä.).  
Alle Schritte sind in Jupyter-Notebooks dokumentiert und versioniert.

---

## 2 Ordnerstruktur 
├─ data/ # harmonisierte Excel-Quellen
│ ├─ bfs_data_lva.xlsx
│ └─ bfs_data_abschlussquote.xlsx
├─ notebooks/
│ ├─ a_profile/ # reine Lese-Notebooks (Datenprofiling)
│ │ ├─ 02_profile_bfs_lva.ipynb
│ │ └─ 03_profile_bfs_abschlussquote.ipynb
│ ├─ b_ETL/ # schreibt in MySQL
│ │ ├─ 04_load_dims.ipynb # 13 Dimensionstabellen
│ │ ├─ 05_load_facts.ipynb # fact_lva_stats
│ │ └─ 08_load_fact_abschluss_stats.ipynb
│ └─ c_sandbox/ # PoC & Tests
│ └─ 01_poc_overview.ipynb
├─ docs/
│ ├─ diagramme/erm_v1.png # exportiertes ER-Diagramm
│ └─ README_Methodik.md # Kapitel-Entwurf für die Thesis
└─ z_doku





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
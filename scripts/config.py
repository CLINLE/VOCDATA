# ── scripts/config.py ────────────────────────────────────────────────────

#Zentrale Projekt-Konfiguration

#Setzt PROJECT_ROOT, SCRIPTS_DIR, PDF_DIR
#Lädt OpenAI-Key (und weitere) aus .env
#Hängt scripts/ an PYTHONPATH, sodass alle Module importierbar sind


# scripts/config.py
from pathlib import Path
import sys, os
from dotenv import load_dotenv, find_dotenv

# ── Pfade ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR  = PROJECT_ROOT / "scripts"
PDF_DIR      = PROJECT_ROOT / "uploads" / "pdf"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


#Lädt Umgebungsvariablen aus .env (OPENAI_API_KEY etc.) und stellt sie
#als Konstanten zur Verfügung, damit alle Module zentrale Settings nutzen.

# ── 3  .env laden (falls vorhanden) ─────────────────────────────────────
load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
OPENAI_KEY     = OPENAI_API_KEY        # Alias danach, kein Fehler mehr

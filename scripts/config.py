"""
Lädt Umgebungsvariablen aus .env (OPENAI_API_KEY etc.) und stellt sie
als Konstanten zur Verfügung, damit alle Module zentrale Settings nutzen.
"""

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())          # .env laden, egal von wo gestartet
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = OPENAI_KEY    # Alias – beide Namen verfügbar


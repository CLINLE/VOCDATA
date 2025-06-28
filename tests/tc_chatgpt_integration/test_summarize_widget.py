# tests/test_summarize.py
import sys, pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]   # …/vocdata
sys.path.insert(0, str(PROJECT_ROOT))                        # ← NEU
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.chatgpt_config.summarize_pdf_files import summarize

def test_summary_not_empty():
    assert summarize(1)


      
    
    
    
    # gibt non-empty String zurück

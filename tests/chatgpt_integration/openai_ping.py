# tests/test_openai_ping.py

"""
Test: OpenAI-API (Ping)
Verifiziert, dass ein gültiger OPENAI_API_KEY
vorliegt und die HTTPS-Verbindung funktioniert.
Skipt automatisch, wenn kein Key gesetzt ist.
powershell: 
conda activate vocdata
pytest tests/openai_ping.py

"""
import os, pytest
from openai import OpenAI

@pytest.mark.skipif(os.getenv("OPENAI_API_KEY") is None, reason="no key")
def test_openai_ping():
    """Mini-Prompt („ping“) muss mindestens 1 Choice liefern."""
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1
    )
    assert resp.choices, "OpenAI response empty"

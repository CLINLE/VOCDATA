"""
Funktion summarize(doc_id) ruft den Volltext aus `qual_docs`,
schickt ihn an das OpenAI-Modell (gpt-4o-mini) und gibt eine
Kurz­zusammenfassung (max. 8 Sätze) zurück.
Import: from scripts.chatgpt_config.summarize_pdf_files import summarize
"""

"""
Erzeugt eine 8-Satz-Zusammenfassung eines PDF-Volltexts
(doc_id aus Tabelle `qual_docs`) via OpenAI-Chat-API (v1-Syntax).
"""
from openai import OpenAI
import sqlalchemy as sa
import pandas as pd
from scripts.config import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)

engine = sa.create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata?charset=utf8mb4"
)

def summarize(doc_id: int) -> str:
    text = pd.read_sql(
        f"SELECT full_text FROM qual_docs WHERE doc_id={doc_id}", engine
    ).iloc[0, 0][:12000]          # max 12 k Tokens

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Fasse den folgenden deutschen Fachtext in max. 8 Sätzen zusammen."},
            {"role": "user", "content": text}
        ]
    )
    return resp.choices[0].message.content


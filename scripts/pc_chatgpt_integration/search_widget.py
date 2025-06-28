from sqlalchemy import create_engine, text
import pandas as pd

ENGINE = create_engine(
    "mysql+pymysql://root:voc_root@localhost:3306/vocdata?charset=utf8mb4"
)

def search(term: str, limit: int = 20) -> pd.DataFrame:
    """
    Liefert doc_id, filename und ein 300-Zeichen-Snippet
    für PDFs, die den Suchbegriff enthalten.
    """
    sql = text("""
        SELECT
            doc_id,
            filename,
            SUBSTRING(full_text, 1, 300) AS snippet
        FROM qual_docs
        WHERE MATCH(full_text) AGAINST (:q IN NATURAL LANGUAGE MODE)
        LIMIT :lim
    """)
    return pd.read_sql(sql, ENGINE, params={"q": term, "lim": limit})

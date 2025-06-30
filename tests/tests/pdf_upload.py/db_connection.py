"""
Test: DB-Verbindung (Smoke)
Prüft ausschliesslich, ob MySQL unter
mysql://root:voc_root@localhost:3306/vocdata
erreichbar ist. Gibt „Fail“, falls Container
gestoppt, falsches PW oder Netzproblem.
"""
import sqlalchemy as sa


def test_db_connection():
    
    engine = sa.create_engine(
        "mysql+pymysql://root:voc_root@localhost:3306/vocdata",
        pool_pre_ping=True,
    )
    with engine.connect() as con:
        assert con.execute(sa.text("SELECT 1")).scalar_one() == 1

"""SELECT 1 muss 1 zurückgeben, sonst DB down."""